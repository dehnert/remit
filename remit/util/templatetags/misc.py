from django import template

register = template.Library()

@register.filter
def budgetarea_pathstr(value, arg=0):
    if value:
        return value.pathstr(skip=arg)
    else: return ""

@register.filter
def approval_status(value):
    from vouchers.models import APPROVAL_STATES
    for num, name in APPROVAL_STATES:
        if num == value: return name
    else: return value
