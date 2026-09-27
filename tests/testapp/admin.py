from django.contrib import admin
from django.http import HttpResponse
from unfold.decorators import action

from subadmin_unfold.admin import UnfoldRootSubAdmin, UnfoldSubAdmin

from .models import Child, Grandchild, Parent


class GrandchildAdmin(UnfoldSubAdmin):
    model = Grandchild
    actions_list = ("show_ancestors",)
    actions_detail = ("show_detail_ancestors",)
    actions_row = ("show_row_ancestors",)
    actions_submit_line = ("mark_reviewed",)

    def get_custom_urls(self):
        return (
            ("overview/", "overview", self.overview),
            ("<int:item_id>/inspect/", "inspect", self.inspect),
        )

    def overview(self, request, model_admin):
        names = [str(parent["object"]) for parent in reversed(request.subadmin.parents)]
        return HttpResponse(" / ".join((model_admin.model._meta.model_name, *names)))

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

    @action(description="Mark reviewed", icon="check")
    def mark_reviewed(self, request, obj):
        obj.name = f"Reviewed {obj.name}"
        obj.save(update_fields=["name"])


class ChildAdmin(UnfoldSubAdmin):
    model = Child
    subadmins = (GrandchildAdmin,)

    def get_custom_urls(self):
        return (("context/", "context", self.context),)

    def context(self, request, model_admin):
        return HttpResponse(
            f"{model_admin.model._meta.model_name}: {request.subadmin.parent_instance}"
        )


@admin.register(Parent)
class ParentAdmin(UnfoldRootSubAdmin):
    subadmins = (ChildAdmin,)
    actions_row = ("show_parent_row",)

    def get_custom_urls(self):
        return (("root-info/", "root_info", self.root_info),)

    def root_info(self, request, model_admin):
        return HttpResponse(model_admin.model._meta.model_name)

    @action(description="Show parent row", icon="account_tree")
    def show_parent_row(self, request, object_id):
        return HttpResponse(object_id)
