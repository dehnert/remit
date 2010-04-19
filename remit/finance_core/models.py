from django.db import models, connection
import settings
import treebeard.mp_tree


class BudgetArea(treebeard.mp_tree.MP_Node):
    indent_str = u"\u00A0\u00A0"

    name = models.CharField(max_length=50)
    comment = models.TextField(blank=True)

    # Applicable to every term?
    always = models.BooleanField(blank=True, default=False)
    budget_term = models.ManyToManyField('BudgetTerm', through='BudgetAreaTerm')

    # Contact / ACL information
    # If not specified, inherit from parent
    owner = models.EmailField(help_text = 'Email address of the officer responsible for the area', blank=True) # owner of the budget area
    interested = models.EmailField(help_text='Email address of parties interested in the area', blank=True) # interested parties (ie, whole committee)
    use_owner = models.BooleanField(default=False, blank=True)
    account_number = models.IntegerField(help_text='Account number: for example, cost object or GL', blank=True, null=True)

    def contact_address(self,):
        address = ''
        if self.use_owner:
            address = self.owner or self.interested
        else:
            address = self.interested or self.owner

    def owner_address(self,):
        address = self.owner
        if address: return address
        else:
            parent = self.get_parent()
            if parent: return self.get_parent().owner_address()
            else: return settings.ADMINS[0][1]

    def get_account_number(self):
        """Retrieve the account number for this account.

        This properly recurses through the hierarchy until reaching the root
        or an account with the account number set."""

        print self.account_number
        if self.account_number:
            return self.account_number
        else:
            parent = self.get_parent()
            if parent:
                return parent.get_account_number()
            else:
                return 0

    def mark_used(self, term, comment=""):
        BudgetAreaTerm.objects.get_or_create(
            budget_area=self,
            budget_term=term,
            defaults={'comment':comment}
        )

    @classmethod
    def get_by_path(cls, path, base=None, ):
        if base:
            node = base
        else:
            try:
                root = BudgetArea.objects.get(name=path[0], depth=1)
            except IndexError, e:
                raise KeyError(e)
            node = root
            path = path[1:]
        for name in path:
            try:
                node = node.get_children().filter(name=name)[0]
            except IndexError, e:
                raise KeyError(e)
        return node

    @classmethod
    def get_by_pathstr(cls, path, base=None):
        path = path.split('.')
        return cls.get_by_path(path, base=base, )

    def pathstr(self, skip=0):
        if self.depth-1 > skip:
            parent = self.get_parent()
            prefix = parent.pathstr(skip=skip) + '.'
        else:
            prefix = ''
        return prefix + self.name

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

    class Meta:
        permissions = (
            ('use_reporting', 'Can use basic reporting functionality',),
        )
        ordering = ['path']


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
    label = models.CharField(max_length=60)
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


LAYER_BUDGET      = 10
LAYER_ALLOCATION  = 20
LAYER_EXPENDITURE = 30
LAYER_CLOSEOUT    = 40
layers=(
    (LAYER_BUDGET,      'budget'),
    (LAYER_ALLOCATION,  'allocation'),
    (LAYER_EXPENDITURE, 'expenditure'),
    (LAYER_CLOSEOUT,    'closeout'),
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
