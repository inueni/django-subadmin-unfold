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


@register.inclusion_tag("subadmin_unfold/subadmin_links.html", takes_context=True)
def unfold_subadmin_links(context):
    model_admin = context["adminform"].model_admin
    visible = {link["subadmin"]: link for link in context["subadmin_links"]}
    instances = iter(model_admin.subadmin_instances)
    navigation = []

    def item(instance):
        link = visible.get(instance)
        if link is not None:
            return {
                "title": link["name"],
                "path": link["url"],
                "icon": instance.get_subadmin_icon(),
            }

    for index, entry in enumerate(model_admin.subadmins or ()):
        if isinstance(entry, dict):
            items = [link for _ in entry["items"] if (link := item(next(instances)))]
            if items:
                navigation.append(
                    {
                        "title": entry["title"],
                        "icon": entry.get("icon"),
                        "method_name": f"subadmin_group_{index}",
                        "items": items,
                    }
                )
        elif link := item(next(instances)):
            navigation.append(link)

    return {"navigation": navigation}


@register.inclusion_tag("subadmin_unfold/submit_line.html", takes_context=True)
def unfold_subadmin_submit_row(context):
    data = submit_row(context)
    data["request"] = context["request"]
    return data
