from django.contrib.admin.utils import quote, unquote
from django.urls import NoReverseMatch, reverse
from unfold.datasets import BaseDataset


class SubAdminDataset(BaseDataset):
    """Link dataset rows to a direct child subadmin of the current admin."""

    def get_result_url(self, result):
        object_id = (self.extra_context or {}).get("object")
        if object_id is None:
            raise NoReverseMatch

        view_name = self.request.resolver_match.view_name
        if not view_name.endswith("_change"):
            raise NoReverseMatch
        nested_view_name = (
            f"{view_name.removesuffix('_change')}_{self.model._meta.model_name}_change"
        )

        if hasattr(self.request, "subadmin"):
            parent_ids = self.request.subadmin.base_url_args
        else:
            parent_ids = [unquote(object_id)]

        return reverse(
            nested_view_name,
            args=[quote(value) for value in (*parent_ids, result.pk)],
        )

    @property
    def cl(self):
        changelist = super().cl
        changelist.url_for_result = self.get_result_url
        return changelist
