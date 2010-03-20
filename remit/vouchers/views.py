import vouchers.models
from vouchers.models import ReimbursementRequest
from finance_core.models import BudgetTerm, BudgetArea

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
import django.forms
from django.forms import Form
from django.forms import ModelForm
from django.forms import ModelChoiceField
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, mail_admins
from django.template import Context, Template
from django.template.loader import get_template

import settings

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
        'pagename':'request_reimbursement',
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

    # Prefill from certs
    initial = {}
    try:
        name = http_request.META['SSL_CLIENT_S_DN_CN']
        names = name.split(' ')
        initial['check_to_first_name'] = names[0]
        initial['check_to_last_name'] = names[-1]
    except KeyError:
        pass
    try:
        initial['check_to_email'] = http_request.META['SSL_CLIENT_S_DN_Email']
    except KeyError:
        pass

    if http_request.method == 'POST': # If the form has been submitted...
        form = RequestForm(http_request.POST, instance=new_request) # A form bound to the POST data
        form.fields['budget_area'] = CommitteeBudgetAreasField(comm_obj)
        form.fields['expense_area'] = ExpenseAreasField()
        if form.is_valid(): # All validation rules pass
            request_obj = form.save()

            # Send email
            tmpl = get_template('vouchers/emails/request_submit_admin.txt')
            ctx = Context({
                'submitter': http_request.user,
                'request': request_obj,
            })
            body = tmpl.render(ctx)
            recipients = []
            for name, addr in settings.ADMINS:
                recipients.append(addr)
            recipients.append(request_obj.budget_area.owner_address())
            send_mail(
                'Request submittal: %s requested $%s' % (
                    http_request.user,
                    request_obj.amount,
                ),
                body,
                settings.SERVER_EMAIL,
                recipients,
            )

            return HttpResponseRedirect(reverse(review_request, args=[new_request.pk],) + '?new=true') # Redirect after POST
    else:
        form = RequestForm(instance=new_request, initial=initial, ) # An unbound form
        form.fields['budget_area'] = CommitteeBudgetAreasField(comm_obj)
        form.fields['expense_area'] = ExpenseAreasField()

    context = {
        'term':term_obj,
        'comm':comm_obj,
        'form':form,
        'pagename':'request_reimbursement',
    }
    return render_to_response('vouchers/submit.html', context, context_instance=RequestContext(http_request), )

class VoucherizeForm(Form):
    name = django.forms.CharField(max_length=100, help_text='Signatory name for voucher',)
    email = django.forms.EmailField(max_length=100, help_text='Signatory email for voucher')


@user_passes_test(lambda u: u.is_authenticated())
def review_request(http_request, object_id):
    request_obj = get_object_or_404(ReimbursementRequest, pk=object_id)
    new = False
    if 'new' in http_request.REQUEST:
        if http_request.REQUEST['new'].upper() == 'TRUE':
            new = True
        else:
            new = False

    show_approve = (http_request.user.has_perm('vouchers.can_approve')
        and request_obj.approval_status == vouchers.models.APPROVAL_STATE_PENDING)
    if show_approve:
        # Voucherize form
        # Prefill from certs / config
        initial = {}
        try:
            name = http_request.META['SSL_CLIENT_S_DN_CN']
            initial['name'] = name
        except KeyError:
            pass
        if settings.SIGNATORY_EMAIL:
            initial['email'] = settings.SIGNATORY_EMAIL
        else:
            try:
                initial['email'] = http_request.META['SSL_CLIENT_S_DN_Email']
            except KeyError:
                pass

        approve_message = ''
        if http_request.method == 'POST' and 'approve' in http_request.REQUEST:
            approve_form = VoucherizeForm(http_request.POST)
            if approve_form.is_valid():
                voucher = request_obj.convert(
                    approve_form.cleaned_data['name'],
                    signatory_email=approve_form.cleaned_data['email'],)
                tmpl = get_template('vouchers/emails/request_approval_admin.txt')
                ctx = Context({
                    'approver': http_request.user,
                    'request': request_obj,
                })
                body = tmpl.render(ctx)
                mail_admins(
                    'Request approval: %s approved $%s' % (
                        http_request.user,
                        request_obj.amount,
                    ),
                    body,
                )
                approve_message = 'Created new voucher from request'
        else:
            approve_form = VoucherizeForm(initial=initial)

    # Display the content
    if not (http_request.user.has_perm('vouchers.view_requests')
        or http_request.user.username == request_obj.submitter):
        # I'd probably use a 403, but that requires like writing
        # a new template and stuff
        # So I'm going to call this "don't leak information"
        # and let it be
        raise Http404
    context = {
        'rr':request_obj,
        'pagename':'request_reimbursement',
        'new': new,
    }
    if show_approve:
        context['approve_form'] = approve_form
        context['approve_message'] = approve_message
    return render_to_response('vouchers/ReimbursementRequest_review.html', context, context_instance=RequestContext(http_request), )

@user_passes_test(lambda u: u.has_perm('vouchers.generate_vouchers'))
def generate_vouchers(http_request, *args):
    unprocessed = True
    if 'unprocessed' in http_request.REQUEST:
        if http_request.REQUEST['unprocessed'].upper() == 'TRUE':
            unprocessed = True
        else:
            unprocessed = False
    mark = True
    if 'mark' in http_request.REQUEST:
        if http_request.REQUEST['mark'].upper() == 'TRUE':
            mark = True
        else:
            mark = False

    lst = vouchers.models.Voucher.objects.all()
    if unprocessed:
        lst = lst.filter(processed=False)

    context = {'vouchers': lst }
    response = render_to_response('vouchers/vouchers.tex', context, context_instance=RequestContext(http_request), )

    # Send mail
    tmpl = get_template('vouchers/emails/vouchers_tex.txt')
    ctx = Context({
        'converter': http_request.user,
        'vouchers': lst,
        'mark': mark,
        'unprocessed': unprocessed,
    })
    body = tmpl.render(ctx)
    mail_admins(
        'Voucher rendering: %d by %s' % (
            len(lst),
            http_request.user,
        ),
        body,
    )

    if mark:
        for voucher in lst:
            voucher.processed = True
            voucher.save()

    return response
