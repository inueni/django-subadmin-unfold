# django-subadmin-unfold

Django Unfold templates and admin classes for django-subadmin.

This adapter is under development for django-subadmin 5.2.x and django-unfold
0.108.x. It has not been published yet.

Add the apps in this order:

    INSTALLED_APPS = [
        "subadmin_unfold",
        "unfold",
        "subadmin",
        "django.contrib.admin",
        # Django's other contrib apps and your own apps...
    ]

The adapter must appear before Unfold so its row-action template is selected.

Use UnfoldRootSubAdmin for the registered parent admin and UnfoldSubAdmin
for each nested admin, importing both from subadmin_unfold.admin.

Subadmin links can be grouped in one or more dropdowns by declaring groups
inside `subadmins` on a root or nested admin:

    subadmins = (
        ChildAdmin,
        {
            "title": "Related",
            "icon": "folder",
            "items": (NoteAdmin, DocumentAdmin),
        },
    )

Each child admin is registered once. Direct entries remain direct links; groups
with no permitted links are hidden. A group with one permitted link remains a
dropdown. Without groups, links display as before. Override
`get_subadmin_label(request)` on a child admin to change its link and breadcrumb
label without renaming the model. To set an icon for an individual subadmin
link, assign a Material Symbols name on its admin class:

    class NoteAdmin(UnfoldSubAdmin):
        model = Note
        subadmin_icon = "sticky_note_2"

The default link icon is `view_list`. To change it for all subadmins, set
`SUBADMIN_UNFOLD_DEFAULT_ICON` in your Django settings:

    SUBADMIN_UNFOLD_DEFAULT_ICON = "list_alt"

A class's `subadmin_icon` takes precedence over this setting. Both work for
direct links and items inside a group; the group's own `icon` stays in its
`subadmins` entry.

Nested admins can define Unfold's get_custom_urls(). Their views receive
model_admin and request.subadmin. Reverse a nested custom URL with
model_admin.reverse_url(name, *parent_ids, *custom_args); its URL name is
prefixed with the nested admin's base view name.
