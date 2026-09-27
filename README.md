# django-subadmin-unfold

Django Unfold templates and admin classes for django-subadmin.

This adapter is under development for django-subadmin 5.2.x and django-unfold
0.108.x. It has not been published yet.

Add the apps in this order:

    INSTALLED_APPS = [
        "unfold",
        "subadmin_unfold",
        "subadmin",
        "django.contrib.admin",
        # Django's other contrib apps and your own apps...
    ]

Use UnfoldRootSubAdmin for the registered parent admin and UnfoldSubAdmin
for each nested admin, importing both from subadmin_unfold.admin.
