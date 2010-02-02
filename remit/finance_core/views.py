from django.http import HttpResponse
import vouchers.models

def display_tree(request):
    root = vouchers.models.BudgetArea.get_by_path(['Accounts'])
    return HttpResponse(root.dump_to_html())
