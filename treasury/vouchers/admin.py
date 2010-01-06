import vouchers
from django.contrib import admin


class ReimbursementRequestAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(ReimbursementRequestAdmin, self).formfield_for_foreignkey(
                                                db_field, request, **kwargs)
        print "In RRA"
        if db_field.rel.to == vouchers.models.BudgetArea:
            field.label_from_instance = self.get_budgetarea_name
        return field

    def get_budgetarea_name(self, area, ):
        return area.indented_name()

    fieldsets = [
        ('Request metadata', {'fields': ['submitter', 'request_time', 'approval_time', 'printing_time', ]}),
        ('Recipient', {'fields': ['check_to_name', 'check_to_email', 'check_to_addr', ] }),
        ('Expense details', {'fields': ['amount', 'budget_area', 'budget_term', ] }),
    ]
    list_display = ('submitter', 'check_to_name', 'amount', 'budget_area', 'budget_term', )


admin.site.register(vouchers.models.ReimbursementRequest, ReimbursementRequestAdmin)
