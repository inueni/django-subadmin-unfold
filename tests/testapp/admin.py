from django.contrib import admin

from subadmin_unfold.admin import UnfoldRootSubAdmin, UnfoldSubAdmin

from .models import Child, Grandchild, Parent


class GrandchildAdmin(UnfoldSubAdmin):
    model = Grandchild


class ChildAdmin(UnfoldSubAdmin):
    model = Child
    subadmins = (GrandchildAdmin,)


@admin.register(Parent)
class ParentAdmin(UnfoldRootSubAdmin):
    subadmins = (ChildAdmin,)
