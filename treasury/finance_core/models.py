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


def coerce_full_email(email):
    if '@' in email: return email
    else: return email + '@' + settings.DEFAULT_DOMAIN
