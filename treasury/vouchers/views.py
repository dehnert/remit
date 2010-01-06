import vouchers.models
from finance_core.models import BudgetTerm, BudgetArea

from django.shortcuts import render_to_response
from django.http import Http404

def submit_request(request, term, committee):
    try:
        term_obj = BudgetTerm.objects.get(slug=term)
    except BudgetTerm.DoesNotExist:
        raise Http404
    try:
        comm_obj = BudgetArea.objects.get(pk=committee)
    except BudgetArea.DoesNotExist:
        raise Http404

    context = {
        'term':term_obj,
        'comm':comm_obj,
    }
    return render_to_response('vouchers/submit.html', context)
