from django.contrib import admin
import finance_core.models

class BudgetAreaAdmin(admin.ModelAdmin):
    pass
    #fields = [ 'path', 'name', 'comment', 'owner', 'interested', ]


class BudgetTermAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(finance_core.models.BudgetArea, BudgetAreaAdmin)
admin.site.register(finance_core.models.BudgetTerm, BudgetTermAdmin)
admin.site.register(finance_core.models.BudgetAreaTerm)
