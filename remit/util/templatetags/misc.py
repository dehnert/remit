from django import template
import finance_core.models

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

@register.filter
def approval_status_class(value):
    from vouchers.models import APPROVAL_STATES
    for num, name in APPROVAL_STATES:
        if num == value: return name.lower()
    else: return value

@register.filter
def sign(value):
    if value > 0: return 'positive'
    elif value < 0: return 'negative'
    else: return 'zero'

register.filter('layer_num', finance_core.models.layer_num)
register.filter('layer_name', finance_core.models.layer_name)
