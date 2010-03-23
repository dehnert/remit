from django.http import HttpResponse
import finance_core.models

def display_tree(request):
    root = finance_core.models.BudgetArea.get_by_path(['Accounts'])
    return HttpResponse(root.dump_to_html())
