import vouchers.models
from vouchers.models import ReimbursementRequest, Documentation
from finance_core.models import BudgetTerm, BudgetArea
from util.shortcuts import get_403_response, ListViewWithContext

from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
import django.forms
from django.forms import Form
from django.forms import ModelForm
from django.forms import ModelChoiceField
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, mail_admins
from django.db.models import Q
from django.template import Context, Template
from django.template.loader import get_template

import decimal

import settings

class RequestForm(ModelForm):
    class Meta:
        model = ReimbursementRequest
        fields = (
            'name',
            'description',
            'incurred_time',
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
        base_area = BudgetArea.get_by_path(settings.BASE_COMMITTEE_PATH)
        self.strip_levels = base_area.depth
        areas = (base_area.get_descendants()
            .filter(depth__lte=base_area.depth+settings.COMMITTEE_HIERARCHY_LEVELS)
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

class DocUploadForm(ModelForm):
    def clean_backing_file(self, ):
        f = self.cleaned_data['backing_file']
        ext = f.name.rsplit('.')[-1]
        contenttype = f.content_type
        if ext != 'pdf':
            raise django.forms.ValidationError("Only PDF files are accepted --- you submitted a .%s file" % (ext, ))
        elif contenttype != 'application/pdf':
            raise django.forms.ValidationError("Only PDF files are accepted --- you submitted a %s file" % (contenttype, ))
        else:
            return f

    class Meta:
        model = Documentation
        fields = (
            'label',
            'backing_file',
        )


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

    # Prefill from user information (itself prefilled from LDAP now)
    initial = {}
    initial['check_to_first_name'] = http_request.user.first_name
    initial['check_to_last_name']  = http_request.user.last_name
    initial['check_to_email']      = http_request.user.email

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
            if settings.CC_SUBMITTER:
                recipients.append(http_request.user.email)
            send_mail(
                '%sRequest submittal: %s requested $%s' % (
                    settings.EMAIL_SUBJECT_PREFIX,
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
    user = http_request.user
    pagename = 'request_reimbursement'
    new = False
    if 'new' in http_request.REQUEST:
        if http_request.REQUEST['new'].upper() == 'TRUE':
            new = True
        else:
            new = False

    if (user.has_perm('vouchers.can_list') or
        user.username == request_obj.submitter or
        user.email.upper() == request_obj.check_to_email.upper()
        ):
        pass
    else:
        return get_403_response(http_request, errmsg="You do not have permission to access this reimbursement request. You can only view requests you submitted or are the recipient for, unless you have general viewing permissions.", pagename=pagename, )

    # DOCUMENTATION #
    if request_obj.documentation:
        doc_upload_form = None
    else:
        new_docs = Documentation()
        new_docs.submitter = http_request.user.username
        if http_request.method == 'POST' and 'upload_documentation' in http_request.REQUEST: # If the form has been submitted...
            doc_upload_form = DocUploadForm(http_request.POST, http_request.FILES, instance=new_docs) # A form bound to the POST data

            if doc_upload_form.is_valid(): # All validation rules pass
                new_docs = doc_upload_form.save()
                request_obj.documentation = new_docs
                request_obj.save()

                return HttpResponseRedirect(reverse(review_request, args=[object_id],)) # Redirect after POST
        else:
            doc_upload_form = DocUploadForm(instance=new_docs, ) # An unbound form

    # SEND EMAILS
    show_email = http_request.user.has_perm('vouchers.can_email')
    if show_email:
        email_message = ''
        if http_request.method == 'POST' and 'send_email' in http_request.REQUEST:
            mail = vouchers.models.stock_emails[http_request.REQUEST['email_name']]
            assert mail.context == 'request'
            mail.send_email_request(request_obj)
            email_message = 'Sent email "%s".' % (mail.label, )
        email_options = []
        for mail in vouchers.models.stock_emails.values():
            if mail.context == 'request':
                email_options.append({
                    'label': mail.label,
                    'name' : mail.name,
                })

    # APPROVE VOUCHERS
    show_approve = (http_request.user.has_perm('vouchers.can_approve')
        and request_obj.approval_status == vouchers.models.APPROVAL_STATE_PENDING)
    if show_approve:
        # Voucherize form
        # Prefill from certs / config
        initial = {}
        initial['name'] = '%s %s' % (http_request.user.first_name, http_request.user.last_name, )
        if settings.SIGNATORY_EMAIL:
            initial['email'] = settings.SIGNATORY_EMAIL
        else:
            initial['email'] = http_request.user.email

        approve_message = ''
        if http_request.method == 'POST' and 'approve' in http_request.REQUEST:
            approve_form = VoucherizeForm(http_request.POST)
            if approve_form.is_valid():
                request_obj.approve(
                    approver=http_request.user,
                    signatory_name=approve_form.cleaned_data['name'],
                    signatory_email=approve_form.cleaned_data['email'],
                )
                approve_message = 'Created new voucher from request'
        else:
            approve_form = VoucherizeForm(initial=initial)

    context = {
        'rr':request_obj,
        'pagename':pagename,
        'new': new,
        'doc_form': doc_upload_form,
    }
    if show_approve:
        context['approve_form'] = approve_form
        context['approve_message'] = approve_message
    if show_email:
        context['email_options'] = email_options
        context['email_message'] = email_message
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

    total = decimal.Decimal('0.00')
    for voucher in lst:
        total = total + voucher.amount

    context = {
        'vouchers': lst,
        'total': total,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
    response = render_to_response(
        'vouchers/vouchers.tex',
        context, context_instance=RequestContext(http_request),
        mimetype=settings.LATEX_MIMETYPE,
    )

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
            voucher.mark_processed()

    return response

def get_related_requests_qobj(user, ):
    return Q(submitter=user.username) | Q(check_to_email=user.email)

request_list_orders = (
#   Name            Label               Columns
    ('default',     'Default',          ()),
    ('id',          'ID',               ('id', )),
    ('state',       'Approval Status',  ('approval_status', )),
    ('stateamount', 'Approval Status, then amount',  ('approval_status', 'amount', )),
    ('stateto',     'Approval Status, then recipient',  ('approval_status', 'check_to_first_name', 'check_to_last_name', )),
    ('statesubmit', 'Approval Status, then submitter',  ('approval_status', 'submitter', )),
    ('name',        'Request Name',     ('name', )),
    ('amount',      'Amount',           ('amount', )),
    ('check_to',    'Check Recipient',  ('check_to_first_name', 'check_to_last_name', )),
    ('submitter',   'Submitter',        ('submitter', )),
)

def list_to_keys(lst):
    dct = {}
    for key in lst:
        dct[key] = True
    return dct

@login_required
def show_requests(http_request, ):
    # BULK ACTIONS
    actions = vouchers.models.BulkRequestAction.filter_can_only(
        vouchers.models.bulk_request_actions,
        http_request.user,
    )
    apply_action_message = None
    apply_action_errors = []
    if 'select' in http_request.REQUEST:
        selected_rr_ids = [ int(item) for item in http_request.REQUEST.getlist('select') ]
    else:
        selected_rr_ids = []
    if "apply-action" in http_request.POST:
        action_name = http_request.POST['action']
        if action_name == 'none':
            apply_action_message = "No action selected."
        else:
            matching_actions = [ action for action in actions if action.name == action_name]
            if(len(matching_actions) > 0):
                action = matching_actions[0]
                rrs = ReimbursementRequest.objects.filter(pk__in=selected_rr_ids)
                for rr in rrs:
                    success, msg = action.do(http_request, rr)
                    if not success:
                        apply_action_errors.append((rr, msg))
                apply_action_message = '"%s" applied to %d request(s) (%d errors encountered)' % (action.label, len(rrs), len(apply_action_errors), )
            else:
                apply_action_message = "Unknown or forbidden action requested."

    # PERMISSION-BASED REQUEST FILTERING
    if http_request.user.has_perm('vouchers.can_list'):
        qs = ReimbursementRequest.objects.all()
        useronly = False
    else:
        qs = ReimbursementRequest.objects.filter(get_related_requests_qobj(http_request.user))
        useronly = True

    # SORTING
    if 'order' in http_request.REQUEST:
        order_row = [row for row in request_list_orders if row[0] == http_request.REQUEST['order']]
        if order_row:
            order, label, cols = order_row[0]
            qs = qs.order_by(*cols)
        else:
            raise Http404('Order by constraint not known')
    else:
        order = 'default'

    # DISCRETIONARY REQUEST FILTERING
    if 'approval_status' in http_request.REQUEST:
        approval_status = http_request.REQUEST['approval_status']
    else:
        approval_status = vouchers.models.APPROVAL_STATE_PENDING
    if approval_status == 'all':
        pass
    else:
        try:
            approval_status = int(approval_status)
        except ValueError:
            raise Http404('approval_status poorly formatted')
        state_row = [row for row in vouchers.models.APPROVAL_STATES if row[0] == approval_status]
        if state_row:
            qs = qs.filter(approval_status=approval_status)
        else:
            raise Http404('approval_status not known')

    # GENERATE THE REQUEST
    callable = ListViewWithContext.as_view(
        queryset=qs,
        extra_context={
            'actions' : actions,
            'selected_ids'  : list_to_keys(selected_rr_ids),
            'action_message': apply_action_message,
            'action_errors' : apply_action_errors,
            'useronly': useronly,
            'order'   : order,
            'orders'  : request_list_orders,
            'approval_status' : approval_status,
            'approval_states':  vouchers.models.APPROVAL_STATES,
            'pagename': 'list_requests',
        },
    )
    return callable(http_request)
