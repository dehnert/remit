import vouchers.models
from finance_core.models import BudgetTerm, BudgetArea
from vouchers.models import ReimbursementRequest

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.forms import Form
from django.forms import ModelForm
from django.forms import ModelChoiceField
from django.core.urlresolvers import reverse

class RequestForm(ModelForm):
    class Meta:
        model = ReimbursementRequest
        fields = (
            'name',
            'description',
            'amount',
            'budget_area',
            'expense_area',
            'check_to_first_name',
            'check_to_last_name',
            'check_to_email',
            'check_to_addr',
        )

class CommitteesField(ModelChoiceField):
    def __init__(self, *args, **kargs):
        base_area = BudgetArea.get_by_path(['Accounts', 'Assets', 'Budget', ])
        self.strip_levels = base_area.depth
        areas = (base_area.get_descendants()
            .filter(depth__lte=base_area.depth+2)
            .exclude(name='Holding')
        )
        ModelChoiceField.__init__(self, queryset=areas,
            help_text='Select the appropriate committe or other budget area',
            *args, **kargs)

    def label_from_instance(self, obj,):
        return obj.indented_name(strip_levels=self.strip_levels)

class SelectRequestBasicsForm(Form):
    area = CommitteesField()
    term = ModelChoiceField(queryset = BudgetTerm.objects.all())

@user_passes_test(lambda u: u.is_authenticated())
def select_request_basics(http_request, ):
    if http_request.method == 'POST': # If the form has been submitted...
        form = SelectRequestBasicsForm(http_request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            term = form.cleaned_data['term'].slug
            area = form.cleaned_data['area'].id
            return HttpResponseRedirect(reverse(submit_request, args=[term, area],)) # Redirect after POST
    else:
        form = SelectRequestBasicsForm() # An unbound form

    context = {
        'form':form,
    }
    return render_to_response('vouchers/select.html', context, context_instance=RequestContext(http_request), )

class CommitteeBudgetAreasField(ModelChoiceField):
    def __init__(self, base_area, *args, **kargs):
        self.strip_levels = base_area.depth
        areas = base_area.get_descendants()
        ModelChoiceField.__init__(self, queryset=areas,
            help_text='In general, this should be a fully indented budget area, not one with children',
            *args, **kargs)

    def label_from_instance(self, obj,):
        return obj.indented_name(strip_levels=self.strip_levels)

class ExpenseAreasField(ModelChoiceField):
    def __init__(self, *args, **kargs):
        base_area = vouchers.models.BudgetArea.get_by_path(['Accounts', 'Expenses'])
        self.strip_levels = base_area.depth
        areas = base_area.get_descendants()
        ModelChoiceField.__init__(self, queryset=areas,
            help_text='In general, this should be a fully indented budget area, not one with children',
            *args, **kargs)

    def label_from_instance(self, obj,):
        return obj.indented_name(strip_levels=self.strip_levels)

@user_passes_test(lambda u: u.is_authenticated())
def submit_request(http_request, term, committee):
    term_obj = get_object_or_404(BudgetTerm, slug=term)
    comm_obj = get_object_or_404(BudgetArea, pk=committee)

    new_request = ReimbursementRequest()
    new_request.submitter = http_request.user.username
    new_request.budget_term = term_obj

    if http_request.method == 'POST': # If the form has been submitted...
        form = RequestForm(http_request.POST, instance=new_request) # A form bound to the POST data
        form.fields['budget_area'] = CommitteeBudgetAreasField(comm_obj)
        form.fields['expense_area'] = ExpenseAreasField()
        if form.is_valid(): # All validation rules pass
            form.save()
            return HttpResponseRedirect(reverse(review_request, args=[new_request.pk],)) # Redirect after POST
    else:
        form = RequestForm(instance=new_request) # An unbound form
        form.fields['budget_area'] = CommitteeBudgetAreasField(comm_obj)
        form.fields['expense_area'] = ExpenseAreasField()

    context = {
        'term':term_obj,
        'comm':comm_obj,
        'form':form,
    }
    return render_to_response('vouchers/submit.html', context, context_instance=RequestContext(http_request), )

@user_passes_test(lambda u: u.is_authenticated())
def review_request(http_request, object_id):
    request_obj = get_object_or_404(ReimbursementRequest, pk=object_id)
    if not (http_request.user.has_perm('vouchers.view_requests')
        or http_request.user.username == request_obj.submitter):
        # I'd probably use a 403, but that requires like writing
        # a new template and stuff
        # So I'm going to call this "don't leak information"
        # and let it be
        raise Http404
    context = {
        'rr':request_obj,
    }
    return render_to_response('vouchers/ReimbursementRequest_review.html', context, context_instance=RequestContext(http_request), )

