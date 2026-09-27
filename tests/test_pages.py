from django.contrib.auth import get_user_model
from django.test import TestCase
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
            reverse("admin:testapp_parent_change", args=[self.parent.pk]),
            self.child_url("changelist"),
            self.child_url("add"),
            self.child_url("change", self.child.pk),
            self.child_url("history", self.child.pk),
            self.child_url("delete", self.child.pk),
            self.grandchild_url("changelist"),
            self.grandchild_url("add"),
            self.grandchild_url("change", self.grandchild.pk),
            self.grandchild_url("history", self.grandchild.pk),
            self.grandchild_url("delete", self.grandchild.pk),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_root_link_and_two_level_breadcrumbs(self):
        root = self.client.get(
            reverse("admin:testapp_parent_change", args=[self.parent.pk])
        )
        self.assertContains(root, self.child_url("changelist"))

        child_change = self.client.get(self.child_url("change", self.child.pk))
        self.assertContains(child_change, self.grandchild_url("changelist"))

        grandchild_list = self.client.get(self.grandchild_url("changelist"))
        self.assertContains(grandchild_list, self.child_url("changelist"))
        self.assertContains(grandchild_list, self.child_url("change", self.child.pk))
        self.assertContains(grandchild_list, "First parent")
        self.assertContains(grandchild_list, "First child")

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

    def test_wrong_ancestor_returns_404(self):
        url = reverse(
            "admin:testapp_parent_child_grandchild_changelist",
            args=[self.other_parent.pk, self.child.pk],
        )
        self.assertEqual(self.client.get(url).status_code, 404)
