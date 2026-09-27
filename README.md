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

Nested admins can define Unfold's get_custom_urls(). Their views receive
model_admin and request.subadmin. Reverse a nested custom URL with
model_admin.reverse_url(name, *parent_ids, *custom_args); its URL name is
prefixed with the nested admin's base view name.
