from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .testapp.models import Child, Grandchild, Parent


class UnfoldNestedPagesTests(TestCase):
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

    def setUp(self):
        self.client.force_login(self.user)

    def child_url(self, view, *args):
        return reverse(
            f"admin:testapp_parent_child_{view}",
            args=[self.parent.pk, *args],
        )

    def grandchild_url(self, view, *args):
        return reverse(
            f"admin:testapp_parent_child_grandchild_{view}",
            args=[self.parent.pk, self.child.pk, *args],
        )

    def test_basic_pages_render(self):
        urls = (
            self.child_url("add"),
            self.child_url("history", self.child.pk),
            self.child_url("delete", self.child.pk),
            self.grandchild_url("add"),
            self.grandchild_url("history", self.grandchild.pk),
            self.grandchild_url("delete", self.grandchild.pk),
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

        confirmation = self.client.post(
            self.child_url("changelist"),
            {"action": "delete_selected", "_selected_action": [str(self.child.pk)]},
        )
        self.assertContains(confirmation, "First parent")

    def test_nested_group_and_two_level_breadcrumbs(self):
        child_change = self.client.get(self.child_url("change", self.child.pk))
        self.assertRegex(child_change.content.decode(), r">\s*Descendants\s*<")
        self.assertContains(child_change, self.grandchild_url("changelist"))

        grandchild_list = self.client.get(self.grandchild_url("changelist"))
        self.assertContains(grandchild_list, self.child_url("changelist"))
        self.assertContains(grandchild_list, self.child_url("change", self.child.pk))
        self.assertContains(grandchild_list, "First parent")
        self.assertContains(grandchild_list, "First child")

    def test_custom_subadmin_label_in_links_and_breadcrumbs(self):
        child_admin = admin.site._registry[Parent].subadmin_instances[0]
        with patch.object(child_admin, "get_subadmin_label", return_value="Members"):
            parent_change = self.client.get(
                reverse("admin:testapp_parent_change", args=[self.parent.pk])
            )
            self.assertContains(parent_change, "Members")

            for url in (
                self.child_url("changelist"),
                self.grandchild_url("changelist"),
            ):
                with self.subTest(url=url):
                    self.assertContains(self.client.get(url), "Members")

    def test_grouped_subadmin_links(self):
        note_url = reverse(
            "admin:testapp_parent_note_changelist", args=[self.parent.pk]
        )
        document_url = reverse(
            "admin:testapp_parent_document_changelist", args=[self.parent.pk]
        )
        response = self.client.get(
            reverse("admin:testapp_parent_change", args=[self.parent.pk])
        )
        self.assertContains(response, self.child_url("changelist"))
        self.assertContains(response, "groups")
        self.assertContains(response, "sticky_note_2")
        self.assertContains(response, "view_list")
        self.assertRegex(response.content.decode(), r">\s*Related\s*<")
        self.assertContains(response, note_url)
        self.assertContains(response, document_url)
        self.assertEqual(self.client.get(note_url).status_code, 200)
        self.assertEqual(self.client.get(document_url).status_code, 200)

    @override_settings(SUBADMIN_UNFOLD_DEFAULT_ICON="list_alt")
    def test_global_subadmin_icon_setting(self):
        response = self.client.get(
            reverse("admin:testapp_parent_change", args=[self.parent.pk])
        )
        self.assertContains(response, "list_alt")
        self.assertContains(response, "groups")
        self.assertContains(response, "sticky_note_2")

    def test_grouped_subadmin_links_follow_permissions(self):
        parent_admin = admin.site._registry[Parent]
        _, note_admin, document_admin = parent_admin.subadmin_instances
        change_url = reverse("admin:testapp_parent_change", args=[self.parent.pk])
        note_url = reverse(
            "admin:testapp_parent_note_changelist", args=[self.parent.pk]
        )
        document_url = reverse(
            "admin:testapp_parent_document_changelist", args=[self.parent.pk]
        )

        with patch.object(
            note_admin, "has_view_or_change_permission", return_value=False
        ):
            response = self.client.get(change_url)
            self.assertNotContains(response, note_url)
            self.assertContains(response, document_url)
            self.assertRegex(response.content.decode(), r">\s*Related\s*<")
            with patch.object(
                document_admin, "has_view_or_change_permission", return_value=False
            ):
                response = self.client.get(change_url)
                self.assertNotRegex(response.content.decode(), r">\s*Related\s*<")
                self.assertContains(response, self.child_url("changelist"))

    def test_nested_creation_and_scope(self):
        response = self.client.get(self.child_url("changelist"))
        self.assertContains(response, "First child")
        self.assertNotContains(response, "Other child")

        response = self.client.get(self.grandchild_url("changelist"))
        self.assertContains(response, "First grandchild")
        self.assertNotContains(response, "Other grandchild")

        response = self.client.post(
            self.grandchild_url("add"),
            {"name": "New grandchild", "_save": "Save"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Grandchild.objects.filter(child=self.child, name="New grandchild").exists()
        )

    def test_nested_unfold_list_action(self):
        action_url = self.grandchild_url("testapp_grandchild_show_ancestors")
        response = self.client.get(self.grandchild_url("changelist"))
        self.assertContains(response, action_url)
        self.assertRegex(response.content.decode(), r">\s*Tools\s*<")

        response = self.client.get(action_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"First parent / First child")

        wrong_parent_url = reverse(
            "admin:testapp_parent_child_grandchild_testapp_grandchild_show_ancestors",
            args=[self.other_parent.pk, self.child.pk],
        )
        self.assertEqual(self.client.get(wrong_parent_url).status_code, 404)

    def test_nested_unfold_detail_action(self):
        action_name = "testapp_grandchild_show_detail_ancestors"
        action_url = self.grandchild_url(action_name, self.grandchild.pk)
        response = self.client.get(self.grandchild_url("change", self.grandchild.pk))
        self.assertContains(response, action_url)

        response = self.client.get(action_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            f"First parent / First child / {self.grandchild.pk}".encode(),
        )

        wrong_parent_url = reverse(
            f"admin:testapp_parent_child_grandchild_{action_name}",
            args=[self.other_parent.pk, self.child.pk, self.grandchild.pk],
        )
        self.assertEqual(self.client.get(wrong_parent_url).status_code, 404)

        wrong_object_url = self.grandchild_url(
            action_name, self.other_grandchild.pk
        )
        self.assertEqual(self.client.get(wrong_object_url).status_code, 404)

    def test_nested_unfold_row_action(self):
        action_name = "testapp_grandchild_show_row_ancestors"
        action_url = self.grandchild_url(action_name, self.grandchild.pk)
        list_response = self.client.get(self.grandchild_url("changelist"))
        self.assertContains(list_response, action_url)

        response = self.client.get(action_url)
        self.assertEqual(
            response.content,
            f"First parent / First child / {self.grandchild.pk}".encode(),
        )
        dropdown_url = self.grandchild_url(
            "testapp_grandchild_show_row_dropdown", self.grandchild.pk
        )
        self.assertContains(list_response, dropdown_url)
        self.assertEqual(
            self.client.get(dropdown_url).content,
            f"dropdown: First parent / First child / {self.grandchild.pk}".encode(),
        )

    def test_nested_unfold_submit_line_action(self):
        change_url = self.grandchild_url("change", self.grandchild.pk)
        action_name = "testapp_grandchild_mark_reviewed"
        response = self.client.get(change_url)
        self.assertContains(response, f'name="{action_name}"')

        response = self.client.post(
            change_url,
            {"name": "Renamed grandchild", action_name: "1"},
        )
        self.assertEqual(response.status_code, 302)
        self.grandchild.refresh_from_db()
        self.assertEqual(self.grandchild.name, "Reviewed Renamed grandchild")

    def test_root_unfold_row_action(self):
        action_url = reverse(
            "admin:testapp_parent_show_parent_row", args=[self.parent.pk]
        )
        response = self.client.get(reverse("admin:testapp_parent_changelist"))
        self.assertContains(response, action_url)
        self.assertEqual(
            self.client.get(action_url).content, str(self.parent.pk).encode()
        )

    def test_nested_unfold_custom_urls(self):
        child_url = self.child_url("context")
        self.assertEqual(self.client.get(child_url).content, b"child: First parent")

        inspect_url = self.grandchild_url("inspect", 42)
        self.assertEqual(
            self.client.get(inspect_url).content,
            b"grandchild / First parent / First child / 42:int",
        )

        wrong_parent_url = reverse(
            "admin:testapp_parent_child_grandchild_inspect",
            args=[self.other_parent.pk, self.child.pk, 42],
        )
        self.assertEqual(self.client.get(wrong_parent_url).status_code, 404)

    def test_root_unfold_custom_url(self):
        url = reverse("admin:root_info")
        self.assertEqual(self.client.get(url).content, b"parent")
