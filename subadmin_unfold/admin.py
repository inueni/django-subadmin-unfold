import re
from functools import update_wrapper

from django.http import Http404
from django.urls import path, re_path
from subadmin import RootSubAdminMixin, SubAdminMixin
from unfold.admin import ModelAdmin
from unfold.enums import ActionVariant


class UnfoldSubAdmin(SubAdminMixin, ModelAdmin):
    change_list_template = "subadmin_unfold/change_list.html"
    change_form_template = "subadmin_unfold/change_form.html"
    delete_confirmation_template = "subadmin_unfold/delete_confirmation.html"
    delete_selected_confirmation_template = (
        "subadmin_unfold/delete_selected_confirmation.html"
    )
    object_history_template = "subadmin_unfold/object_history.html"

    def get_urls(self):
        def wrap(action, detail=False):
            def view(request, *view_args):
                object_id = view_args[-1] if detail else None
                request.subadmin = self.get_subadmin_helper(
                    request, view_args, object_id=object_id
                )
                if detail:
                    if self.get_object(request, object_id) is None:
                        raise Http404
                    return action.method(request, object_id=object_id)
                return action.method(request)

            wrapped = self.admin_site.admin_view(view)
            wrapped.model_admin = self
            return update_wrapper(wrapped, action.method)

        base_viewname = self.get_base_viewname()
        row_action_urls = [
            re_path(
                rf"^(.+)/{re.escape(action.path.removesuffix('/'))}/$",
                wrap(action, detail=True),
                name=f"{base_viewname}_{action.action_name}",
            )
            for action in self._get_base_actions_row()
        ]
        list_action_urls = [
            path(
                f"{action.path.removesuffix('/')}/",
                wrap(action),
                name=f"{base_viewname}_{action.action_name}",
            )
            for action in self._get_base_actions_list()
        ]
        detail_action_urls = [
            re_path(
                rf"^(.+)/{re.escape(action.path.removesuffix('/'))}/$",
                wrap(action, detail=True),
                name=f"{base_viewname}_{action.action_name}",
            )
            for action in self._get_base_actions_detail()
        ]
        return (
            row_action_urls + list_action_urls + detail_action_urls + super().get_urls()
        )

    def get_actions_list(self, request):
        actions = super().get_actions_list(request)
        for action in actions:
            action.subadmin_url_args = request.subadmin.base_url_args
        return actions

    def get_actions_detail(self, request, object_id):
        actions = super().get_actions_detail(request, object_id)
        for action in actions:
            action.subadmin_url_args = request.subadmin.base_url_args
        return actions

    def _get_actions_navigation(
        self, provided_actions, allowed_actions, object_id=None
    ):
        """Give actions the ancestor URL arguments Unfold 0.108 omits."""

        prefix = f"{self.model._meta.app_label}_{self.model._meta.model_name}_"
        allowed_by_name = {
            action.action_name.removeprefix(prefix): action
            for action in allowed_actions
        }

        def item(name):
            action = allowed_by_name.get(name)
            if action is None:
                return None
            return {
                "title": action.description,
                "icon": action.icon,
                "variant": action.variant,
                "attrs": action.method.attrs,
                "dialog": action.dialog,
                "path": self.reverse_url(action.action_name, *action.subadmin_url_args),
            }

        navigation = []
        for entry in provided_actions:
            if isinstance(entry, str):
                if action_item := item(entry):
                    navigation.append(action_item)
            elif action_items := [
                action_item for name in entry["items"] if (action_item := item(name))
            ]:
                navigation.append(
                    {
                        "title": entry["title"],
                        "icon": entry.get("icon"),
                        "variant": entry.get("variant", ActionVariant.DEFAULT),
                        "items": action_items,
                    }
                )
        return navigation


class UnfoldRootSubAdmin(RootSubAdminMixin, ModelAdmin):
    change_form_template = "subadmin_unfold/parent_change_form.html"
