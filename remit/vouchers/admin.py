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
        ('Expense details', {'fields': ['name', 'description', 'amount', 'budget_area', 'budget_term', ] }),
        ('Request metadata', {'fields': ['submitter', 'request_time', 'approval_time', 'approval_status', 'printing_time', ]}),
        ('Recipient', {'fields': ['check_to_first_name', 'check_to_last_name', 'check_to_email', 'check_to_addr', ] }),
    ]
    list_display = ('name', 'submitter', 'check_to_first_name', 'check_to_last_name', 'amount', 'budget_area', 'budget_term', )

class VoucherAdmin(admin.ModelAdmin):
    list_display = ('processed', 'description', 'signatory', 'first_name', 'last_name', 'amount', 'account', 'gl', )

admin.site.register(vouchers.models.ReimbursementRequest, ReimbursementRequestAdmin)
admin.site.register(vouchers.models.Voucher, VoucherAdmin)
