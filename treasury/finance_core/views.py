from django.http import HttpResponse
import treasury.vouchers.models

def display_tree(request):
    root = treasury.vouchers.models.BudgetArea.get_by_path(['Accounts'])
    return HttpResponse(root.dump_to_html())
