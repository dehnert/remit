from django.contrib import admin
import finance_core.models

class BudgetAreaAdmin(admin.ModelAdmin):
    list_display = ('path', 'name', 'owner', 'interested', 'always', )
    #fields = [ 'path', 'name', 'comment', 'owner', 'interested', ]


class BudgetTermAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug', 'start_date', 'end_date', 'submit_deadline', )


class BudgetAreaTermAdmin(admin.ModelAdmin):
    list_display = ('budget_area', 'budget_term', )


class LineItemInline(admin.TabularInline):
    model = finance_core.models.LineItem


class LineItemAdmin(admin.ModelAdmin):
    list_display = ('tx', 'label', 'amount', 'budget_area', 'layer', )


class TransactionAdmin(admin.ModelAdmin):
    inlines = [
        LineItemInline,
    ]
    list_display = ('name', 'desc', )


admin.site.register(finance_core.models.BudgetArea, BudgetAreaAdmin)
admin.site.register(finance_core.models.BudgetTerm, BudgetTermAdmin)
admin.site.register(finance_core.models.BudgetAreaTerm, BudgetAreaTermAdmin)
admin.site.register(finance_core.models.Transaction, TransactionAdmin)
admin.site.register(finance_core.models.LineItem, LineItemAdmin)
