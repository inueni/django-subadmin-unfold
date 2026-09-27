from subadmin import RootSubAdminMixin, SubAdminMixin
from unfold.admin import ModelAdmin


class UnfoldSubAdmin(SubAdminMixin, ModelAdmin):
    change_list_template = "subadmin_unfold/change_list.html"
    change_form_template = "subadmin_unfold/change_form.html"
    delete_confirmation_template = "subadmin_unfold/delete_confirmation.html"
    delete_selected_confirmation_template = (
        "subadmin_unfold/delete_selected_confirmation.html"
    )
    object_history_template = "subadmin_unfold/object_history.html"


class UnfoldRootSubAdmin(RootSubAdminMixin, ModelAdmin):
    change_form_template = "subadmin_unfold/parent_change_form.html"
