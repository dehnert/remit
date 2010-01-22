from django.db import models
import settings
import treebeard.mp_tree


class BudgetArea(treebeard.mp_tree.MP_Node):
    indent_str = u"\u00A0\u00A0"

    name = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    always = models.BooleanField(blank=True, default=False)

    # Contact / ACL information
    # If not specified, inherit from parent
    owner = models.EmailField(help_text = 'Email address of the officer responsible for the area', blank=True) # owner of the budget area
    interested = models.EmailField(help_text='Email address of parties interested in the area', blank=True) # interested parties (ie, whole committee)
    use_owner = models.BooleanField(default=False, blank=True)

    def contact_address(self,):
        address = ''
        if self.use_owner:
            address = self.owner or self.interested
        else:
            address = self.interested or self.owner
        return address or self.get_parent().contact_address()

    def mark_used(self, term, comment=""):
        BudgetAreaTerm.objects.get_or_create(
            budget_area=self,
            budget_term=term,
            defaults={'comment':comment}
        )

    @classmethod
    def get_by_path(cls, path):
        root = BudgetArea.objects.get(name=path[0], depth=1)
        node = root
        for name in path[1:]:
            node = node.get_children().filter(name=name)[0]
        return node

    def dump_to_html(self):
        struct = self.dump_bulk()
        return self.struct_to_html(struct, depth=0)

    def struct_to_html(self, struct, depth=0):
        def format_data(data):
            return "<em>"+data['name']+"</em> "+unicode(data)
        prefix = "\t"*depth
        html = prefix+"<ul>\n"
        html = html + "\n".join(
            [("%(prefix)s\t<li>%(data)s\n%(children)s\t%(prefix)s</li>\n" % {
                'prefix':prefix,
                'data':format_data(elem['data']),
                'children':('children' in elem and self.struct_to_html(elem['children'], depth+1) or '')
            }) for elem in struct])
        html = html + prefix + "</ul>\n"
        return html

    def indented_name(self, strip_levels=0):
        return self.indent_str*(self.depth-strip_levels) + unicode(self)

    def __unicode__(self,):
        return u"%s [%s] (%s)" % (self.name, self.contact_address(), self.always, )


class BudgetTerm(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    submit_deadline = models.DateField()

    def __unicode__(self,):
        return "%s (%s to %s [due %s])" % (self.name, self.start_date, self.end_date, self.submit_deadline, )


class BudgetAreaTerm(models.Model):
    budget_area = models.ForeignKey(BudgetArea)
    budget_term = models.ForeignKey(BudgetTerm)
    comment = models.TextField(blank=True, )

    def __unicode__(self,):
        return "%s during %s" % (self.budget_area, self.budget_term, )


class Transaction(models.Model):
    name = models.CharField(max_length=40)
    desc = models.TextField(blank=True)

    def __unicode__(self,):
        return self.name

def make_transfer(name, amount,
    layer, budget_term, from_area, to_area, desc, ):
    tx = Transaction(
        name=name,
        desc=desc,
    )
    tx.save()

    from_li = LineItem(
        label='Send: %s' % (name, ),
        amount=-amount,
        budget_area=from_area,
        budget_term=budget_term,
        layer=layer,
        tx=tx,
    )
    from_li.save()

    to_li = LineItem(
        label='Receive: %s' % (name, ),
        amount=amount,
        budget_area=to_area,
        budget_term=budget_term,
        layer=layer,
        tx=tx,
    )
    to_li.save()

    return tx


class LineItem(models.Model):
    tx = models.ForeignKey(Transaction)
    amount = models.DecimalField(max_digits=7, decimal_places=2, help_text='Do not include "$"')
    label = models.CharField(max_length=40)
    budget_area = models.ForeignKey(BudgetArea)
    budget_term = models.ForeignKey(BudgetTerm)
    layer = models.IntegerField() # this might actually be a Transaction property...

    def layer_string(self,):
        layer = self.layer
        return layer_name(get_layer_by_num(layer))

    def __unicode__(self, ):
        return "%s: %s: $%s (%s) in %s during %s" % (
            self.tx, self.label, self.amount, self.layer,
            self.budget_area, self.budget_term, )


layers=(
    (10, 'budget'),
    (20, 'allocation'),
    (30, 'expenditure'),
    (40, 'closeout'),
)
def get_layer_by_name(name):
    for layer in layers:
        if name == layer[1]:
            return layer
    raise KeyError, "layer %s not found" % (name, )
def get_layer_by_num(num):
    for layer in layers:
        if num == layer[0]:
            return layer
    raise KeyError, "layer %d not found" % (num, )
def layer_name(layer): return layer[1]
def layer_num(layer):  return layer[0]


def coerce_full_email(email):
    if '@' in email: return email
    else: return email + '@' + settings.DEFAULT_DOMAIN
