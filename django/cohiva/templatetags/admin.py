from django import template

register = template.Library()


@register.simple_tag(name="has_nav_or_subnav_item_active")
def has_nav_or_subnav_item_active(items: list) -> bool:
    for item in items:
        if "active" in item and item["active"]:
            return True
        if "is_subgroup" in item and item["is_subgroup"]:
            return has_nav_or_subnav_item_active(item["items"])

    return False
