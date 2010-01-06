import vouchers
from django.contrib import admin

indent_str = u"\u00A0\u00A0"

class BudgetAreaAdmin(admin.ModelAdmin):
    pass
    #fields = [ 'path', 'name', 'comment', 'owner', 'interested', ]

class ReimbursementRequestAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(ReimbursementRequestAdmin, self).formfield_for_foreignkey(
                                                db_field, request, **kwargs)
        print "In RRA"
        if db_field.rel.to == vouchers.models.BudgetArea:
            field.label_from_instance = self.get_budgetarea_name
        return field

    def get_budgetarea_name(self, area, ):
        return indent_str*area.depth + unicode(area)

    fieldsets = [
        ('Request metadata', {'fields': ['submitter']}),
        ('Recipient', {'fields': ['check_to_name', 'check_to_email', 'check_to_addr', ] }),
        ('Expense details', {'fields': ['amount', 'budget_area', 'budget_term', ] }),
    ]

admin.site.register(vouchers.models.BudgetArea, BudgetAreaAdmin)
admin.site.register(vouchers.models.BudgetTerm)
admin.site.register(vouchers.models.BudgetAreaTerm)
admin.site.register(vouchers.models.ReimbursementRequest, ReimbursementRequestAdmin)
