from django.contrib import admin
from django.http import HttpResponse
from unfold.decorators import action

from subadmin_unfold.admin import UnfoldRootSubAdmin, UnfoldSubAdmin

from .models import Child, Document, Grandchild, Note, Parent, StringChild, StringParent


class GrandchildAdmin(UnfoldSubAdmin):
    model = Grandchild
    actions_list = ({"title": "Tools", "items": ("show_ancestors",)},)
    actions_detail = ("show_detail_ancestors",)
    actions_row = ("show_row_ancestors", "show_row_dropdown", "confirm_row")
    actions_submit_line = ("mark_reviewed",)

    def get_custom_urls(self):
        return (("<int:item_id>/inspect/", "inspect", self.inspect),)

    def inspect(self, request, model_admin, item_id):
        names = [str(parent["object"]) for parent in reversed(request.subadmin.parents)]
        return HttpResponse(
            " / ".join(
                (
                    model_admin.model._meta.model_name,
                    *names,
                    f"{item_id}:{type(item_id).__name__}",
                )
            )
        )

    @action(description="Show ancestors", icon="account_tree")
    def show_ancestors(self, request):
        names = [str(parent["object"]) for parent in reversed(request.subadmin.parents)]
        return HttpResponse(" / ".join(names))

    @action(description="Show detail ancestors", icon="account_tree")
    def show_detail_ancestors(self, request, object_id):
        names = [str(parent["object"]) for parent in reversed(request.subadmin.parents)]
        return HttpResponse(" / ".join((*names, object_id)))

    @action(
        description="Show row ancestors",
        icon="account_tree",
        extra_options={"display_in_dropdown": False},
    )
    def show_row_ancestors(self, request, object_id):
        names = [str(parent["object"]) for parent in reversed(request.subadmin.parents)]
        return HttpResponse(" / ".join((*names, object_id)))

    @action(description="Show row dropdown", icon="account_tree")
    def show_row_dropdown(self, request, object_id):
        names = [str(parent["object"]) for parent in reversed(request.subadmin.parents)]
        return HttpResponse("dropdown: " + " / ".join((*names, object_id)))

    @action(
        description="Confirm row",
        dialog={"title": "Confirm row", "description": "Confirm this action"},
    )
    def confirm_row(self, request, form, object_id):
        names = [str(parent["object"]) for parent in reversed(request.subadmin.parents)]
        return HttpResponse("confirmed: " + " / ".join((*names, object_id)))

    @action(description="Mark reviewed", icon="check")
    def mark_reviewed(self, request, obj):
        obj.name = f"Reviewed {obj.name}"
        obj.save(update_fields=["name"])


class ChildAdmin(UnfoldSubAdmin):
    model = Child
    subadmin_icon = "groups"
    subadmins = (
        {"title": "Descendants", "icon": "account_tree", "items": (GrandchildAdmin,)},
    )

    def get_custom_urls(self):
        return (("context/", "context", self.context),)

    def context(self, request, model_admin):
        return HttpResponse(
            f"{model_admin.model._meta.model_name}: {request.subadmin.parent_instance}"
        )


class NoteAdmin(UnfoldSubAdmin):
    model = Note
    subadmin_icon = "sticky_note_2"


class DocumentAdmin(UnfoldSubAdmin):
    model = Document


@admin.register(Parent)
class ParentAdmin(UnfoldRootSubAdmin):
    subadmins = (
        ChildAdmin,
        {"title": "Related", "icon": "folder", "items": (NoteAdmin, DocumentAdmin)},
    )
    actions_row = ("show_parent_row",)

    def get_custom_urls(self):
        return (("root-info/", "root_info", self.root_info),)

    def root_info(self, request, model_admin):
        return HttpResponse(model_admin.model._meta.model_name)

    @action(description="Show parent row", icon="account_tree")
    def show_parent_row(self, request, object_id):
        return HttpResponse(object_id)


class StringChildAdmin(UnfoldSubAdmin):
    model = StringChild


@admin.register(StringParent)
class StringParentAdmin(UnfoldRootSubAdmin):
    subadmins = (StringChildAdmin,)
