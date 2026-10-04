from unittest.mock import patch

from django.contrib import admin
from django.contrib.admin.utils import quote, unquote
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unfold.admin import ModelAdmin

from subadmin_unfold.datasets import SubAdminDataset

from .testapp.models import Child, Grandchild, Parent, StringChild, StringParent


class ChildDatasetAdmin(ModelAdmin):
    list_display = ("name",)
    list_display_links = ("name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        parent_id = self.extra_context.get("object")
        return queryset.filter(parent_id=parent_id) if parent_id else queryset.none()


class ChildDataset(SubAdminDataset):
    model = Child
    model_admin = ChildDatasetAdmin


class GrandchildDatasetAdmin(ModelAdmin):
    list_display = ("name",)
    list_display_links = ("name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        child_id = request.subadmin.object_id
        return queryset.filter(child_id=child_id) if child_id else queryset.none()


class GrandchildDataset(SubAdminDataset):
    model = Grandchild
    model_admin = GrandchildDatasetAdmin


class StringChildDatasetAdmin(ModelAdmin):
    list_display = ("name",)
    list_display_links = ("name",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        parent_id = self.extra_context.get("object")
        if parent_id:
            return queryset.filter(parent_id=unquote(parent_id))
        return queryset.none()


class StringChildDataset(SubAdminDataset):
    model = StringChild
    model_admin = StringChildDatasetAdmin


class SubAdminDatasetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            "admin", "admin@example.com", "password"
        )
        cls.parent = Parent.objects.create(name="First parent")
        cls.other_parent = Parent.objects.create(name="Other parent")
        cls.child = Child.objects.create(parent=cls.parent, name="First child")
        cls.other_child = Child.objects.create(
            parent=cls.other_parent, name="Other child"
        )
        cls.grandchild = Grandchild.objects.create(
            child=cls.child, name="First grandchild"
        )
        cls.other_grandchild = Grandchild.objects.create(
            child=cls.other_child, name="Other grandchild"
        )
        cls.string_parent = StringParent.objects.create(
            id="parent_2Fid", name="String parent"
        )
        cls.string_child = StringChild.objects.create(
            id="child_2Fid", parent=cls.string_parent, name="String child"
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_root_dataset_links_to_child_subadmin(self):
        parent_admin = admin.site._registry[Parent]
        with patch.object(parent_admin, "change_form_datasets", (ChildDataset,)):
            response = self.client.get(
                reverse("admin:testapp_parent_change", args=[self.parent.pk])
            )
            add_response = self.client.get(reverse("admin:testapp_parent_add"))

        self.assertContains(response, "First child")
        self.assertNotContains(response, "Other child")
        self.assertContains(
            response,
            reverse(
                "admin:testapp_parent_child_change",
                args=[self.parent.pk, self.child.pk],
            ),
        )
        self.assertNotContains(add_response, "First child")

    def test_nested_dataset_uses_existing_subadmin_request(self):
        child_admin = admin.site._registry[Parent].subadmin_instances[0]
        with patch.object(child_admin, "change_form_datasets", (GrandchildDataset,)):
            response = self.client.get(
                reverse(
                    "admin:testapp_parent_child_change",
                    args=[self.parent.pk, self.child.pk],
                )
            )
            add_response = self.client.get(
                reverse("admin:testapp_parent_child_add", args=[self.parent.pk])
            )

        self.assertContains(response, "First grandchild")
        self.assertNotContains(response, "Other grandchild")
        self.assertContains(
            response,
            reverse(
                "admin:testapp_parent_child_grandchild_change",
                args=[self.parent.pk, self.child.pk, self.grandchild.pk],
            ),
        )
        self.assertNotContains(add_response, "First grandchild")

    def test_quoted_ids_in_dataset_links(self):
        parent_id = quote(self.string_parent.pk)
        child_id = quote(self.string_child.pk)
        parent_admin = admin.site._registry[StringParent]
        child_admin = parent_admin.subadmin_instances[0]
        change_url = child_admin.reverse_url("change", parent_id, child_id)

        with patch.object(parent_admin, "change_form_datasets", (StringChildDataset,)):
            parent_change = self.client.get(
                reverse("admin:testapp_stringparent_change", args=[parent_id])
            )
        self.assertContains(parent_change, change_url)
