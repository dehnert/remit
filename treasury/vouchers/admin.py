import vouchers
from django.contrib import admin

class BudgetAreaAdmin(admin.ModelAdmin):
    pass
    #fields = [ 'path', 'name', 'comment', 'owner', 'interested', ]

admin.site.register(vouchers.models.BudgetArea, BudgetAreaAdmin)
admin.site.register(vouchers.models.BudgetTerm)
admin.site.register(vouchers.models.BudgetAreaTerm)
admin.site.register(vouchers.models.ReimbursementRequest)
