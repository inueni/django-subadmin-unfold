from django.contrib.admin.templatetags.admin_modify import submit_row
from django.template import Library
from subadmin.templatetags.subadmin_tags import subadmin_breadcrumbs

register = Library()


@register.simple_tag(takes_context=True)
def unfold_subadmin_navigation(context):
    data = subadmin_breadcrumbs(context)
    return {
        "root": data["root"],
        "ancestors": data["breadcrumbs"],
        "parent_url": data["breadcrumbs"][-1]["url"],
    }


@register.inclusion_tag("subadmin_unfold/submit_line.html", takes_context=True)
def unfold_subadmin_submit_row(context):
    data = submit_row(context)
    data["request"] = context["request"]
    return data
