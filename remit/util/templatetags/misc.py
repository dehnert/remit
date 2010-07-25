from django import template
from django.template import Node, NodeList, Template, Context, Variable
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

class IfInNode(Node):
    def __init__(self, member, container, nodelist_true, nodelist_false, negate):
        self.member, self.container = member, container
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfInNode>"

    def render(self, context):
        member_val = self.member.resolve(context, True)
        container_val = self.container.resolve(context, True)
        res = member_val in container_val
        if (self.negate and not res) or (not self.negate and res):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)

def do_ifin(parser, token, negate):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    member = parser.compile_filter(bits[1])
    container = parser.compile_filter(bits[2])
    return IfInNode(member, container, nodelist_true, nodelist_false, negate)
register.tag("ifin", lambda x, y: do_ifin(x, y, False))


register.filter('layer_num', finance_core.models.layer_num)
register.filter('layer_name', finance_core.models.layer_name)
