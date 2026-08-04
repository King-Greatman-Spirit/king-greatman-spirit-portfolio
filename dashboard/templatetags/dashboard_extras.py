from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr):
    """Resolve an attribute path like 'a.b.c' on an object."""
    value = obj
    for part in str(attr).split("."):
        value = getattr(value, part, None)
        if value is None:
            return None
    return value


@register.filter
def col_val(obj, col):
    """Render a column value based on its kind."""
    attr, label, kind = col
    value = get_attr(obj, attr)
    if value is None or value == "":
        return ""
    if kind == "img":
        try:
            return value.url
        except AttributeError:
            return ""
    if kind == "date":
        return value.strftime("%d %b %Y")
    if kind == "bool":
        return "Yes" if value else "No"
    return value


@register.filter
def kgs_money(value):
    """Format a Decimal/int with thousands separators."""
    try:
        return format(value, ",.2f").rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return value


@register.filter
def status_cls(value):
    return {
        "new": "badge-new",
        "pending": "badge-warn",
        "contacted": "badge-info",
        "resolved": "badge-ok",
        "paid": "badge-ok",
        "failed": "badge-bad",
        "active": "badge-ok",
        "True": "badge-ok",
        "False": "badge-muted",
    }.get(str(value), "badge-muted")
