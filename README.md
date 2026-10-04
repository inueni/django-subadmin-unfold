# django-subadmin-unfold

`django-subadmin-unfold` makes
[django-subadmin](https://github.com/inueni/django-subadmin)'s nested model
admins feel at home in [Django Unfold](https://unfoldadmin.com/), from
navigation and breadcrumbs to custom actions.

## Installation

```console
pip install django-subadmin-unfold
```

The package requires Python 3.12+, Django 5.2+, django-subadmin 5.2+, and
django-unfold 0.102+. It has been tested with Django 5.2, 6.0, and 6.1. Add
the apps in this order so the adapter's templates are used:

```python
# settings.py
INSTALLED_APPS = [
    "subadmin_unfold",
    "unfold",
    "subadmin",
    "django.contrib.admin",
    # Django's other contrib apps and your own apps...
]
```

## Using it

Start with the [django-subadmin example](https://github.com/inueni/django-subadmin#example).
The model relationships are the same. Use `UnfoldSubAdmin` for nested admins
and `UnfoldRootSubAdmin` for the registered parent admin:

```python
from django.contrib import admin
from subadmin_unfold.admin import UnfoldRootSubAdmin, UnfoldSubAdmin

from .models import Child, Parent


class ChildAdmin(UnfoldSubAdmin):
    model = Child


@admin.register(Parent)
class ParentAdmin(UnfoldRootSubAdmin):
    subadmins = (ChildAdmin,)
```

The nested list and change pages use Unfold's templates and breadcrumbs.

![Child list nested under Example parent](https://raw.githubusercontent.com/inueni/django-subadmin-unfold/1.0.0/docs/images/subadmin-children-list.png)

## Grouping subadmin links

Django admin has no subadmin links, and django-subadmin displays each link
separately. This adapter lets you group links into dropdowns, following
Unfold's dropdown actions pattern. Here **Children** stays as a direct link,
while **Notes** and **Documents** sit under **Related**:

```python
subadmins = (
    ChildAdmin,
    {
        "title": "Related",
        "icon": "folder",
        "items": (NoteAdmin, DocumentAdmin),
    },
)
```

![Parent admin with a direct Children link and an open Related dropdown](https://raw.githubusercontent.com/inueni/django-subadmin-unfold/1.0.0/docs/images/subadmin-parent-grouped-links.png)

`NoteAdmin` and `DocumentAdmin` are defined like `ChildAdmin`. Groups work on
root and nested admins. A group with no permitted links is hidden; one
permitted link still appears in a dropdown.

## Icons

Set `subadmin_icon` on a nested admin to give its link a
[Material Symbols](https://fonts.google.com/icons) icon:

```python
class ChildAdmin(UnfoldSubAdmin):
    model = Child
    subadmin_icon = "groups"
```

The default link icon is `view_list`. To change it for all subadmins, set
`SUBADMIN_UNFOLD_DEFAULT_ICON` in your Django settings:

```python
SUBADMIN_UNFOLD_DEFAULT_ICON = "list_alt"
```

A class's `subadmin_icon` takes precedence over this setting. Both work for
direct links and links inside groups. Set a dropdown's icon with the group's
`icon` key, as above.

## Datasets

[Unfold datasets](https://unfoldadmin.com/docs/configuration/datasets/) display
a changelist inside a change form. Regular `BaseDataset` works on subadmin
pages. Use `SubAdminDataset` when the dataset's rows should link to a direct
child subadmin's change pages.

The following setup shows Children on a Parent change form. It replaces the
short `admin.py` example above. `ChildAdmin` provides the full nested pages,
`ChildDatasetAdmin` configures and filters the embedded table, and
`ChildDataset` points table rows to those nested pages:

```python
from django.contrib import admin
from django.contrib.admin.utils import unquote
from subadmin_unfold.admin import UnfoldRootSubAdmin, UnfoldSubAdmin
from subadmin_unfold.datasets import SubAdminDataset
from unfold.admin import ModelAdmin

from .models import Child, Parent


class ChildAdmin(UnfoldSubAdmin):
    model = Child


class ChildDatasetAdmin(ModelAdmin):
    list_display = ("name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        parent_id = (self.extra_context or {}).get("object")
        if not parent_id or not self.has_view_or_change_permission(request):
            return queryset.none()
        return queryset.filter(parent_id=unquote(parent_id))


class ChildDataset(SubAdminDataset):
    model = Child
    model_admin = ChildDatasetAdmin


@admin.register(Parent)
class ParentAdmin(UnfoldRootSubAdmin):
    subadmins = (ChildAdmin,)
    change_form_datasets = (ChildDataset,)
```

`ChildDatasetAdmin` is a separate, unregistered admin used by Unfold to render
the table. Its queryset must enforce parent scope and any child visibility
rules. `SubAdminDataset` only changes row links; it does not create detail pages
or inherit settings from `ChildAdmin`.

## Unfold actions

Define [Unfold actions](https://unfoldadmin.com/docs/actions/introduction/) on
`UnfoldSubAdmin` as you would on an Unfold `ModelAdmin`. List, detail, row, and
submit-line actions are supported. For example, a list action can use
`request.subadmin` to access the current parent:

```python
from django.http import HttpResponse
from unfold.decorators import action


class ChildAdmin(UnfoldSubAdmin):
    model = Child
    actions_list = ("show_parent",)

    @action(description="Show parent", icon="account_tree")
    def show_parent(self, request):
        return HttpResponse(request.subadmin.parent_instance.name)
```

The adapter includes the parent IDs in nested action URLs. Nested admins can
also define `get_custom_urls()`; those views receive `model_admin` and
`request.subadmin`. Reverse a nested custom URL with
`model_admin.reverse_url(name, *parent_ids, *custom_args)`.
