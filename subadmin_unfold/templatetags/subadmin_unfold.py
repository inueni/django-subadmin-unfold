from django.contrib.admin.templatetags.admin_modify import submit_row
from django.contrib.admin.utils import quote
from django.template import Library
from django.urls import reverse
from subadmin.templatetags.subadmin_tags import subadmin_breadcrumbs

register = Library()


@register.simple_tag
def unfold_subadmin_row_url(cl, raw_path, object_id):
    request = getattr(cl, "request", None)
    if request is not None and hasattr(request, "subadmin"):
        return cl.model_admin.reverse_url(
            raw_path.rsplit(":", 1)[-1],
            *[quote(arg) for arg in request.subadmin.base_url_args],
            quote(object_id),
        )
    return reverse(raw_path, args=(object_id,))


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
