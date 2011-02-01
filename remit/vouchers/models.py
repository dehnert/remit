from django.db import models
import settings
import finance_core
from finance_core.models import BudgetArea, BudgetTerm

from django.core.mail import send_mail, mail_admins
from django.template import Context, Template
from django.template.loader import get_template

import datetime

APPROVAL_STATE_PENDING = 0
APPROVAL_STATE_APPROVED = 1
APPROVAL_STATE_REJECTED = -1
APPROVAL_STATES = (
    (APPROVAL_STATE_PENDING,  'Pending'),
    (APPROVAL_STATE_APPROVED, 'Approved'),
    (APPROVAL_STATE_REJECTED, 'Rejected'),
)

class ReimbursementRequest(models.Model):
    submitter = models.CharField(max_length=30) # Username of submitter
    check_to_first_name = models.CharField(max_length=50, verbose_name="check recipient's first name")
    check_to_last_name = models.CharField(max_length=50, verbose_name="check recipient's last name")
    check_to_email = models.EmailField(verbose_name="email address for check pickup")
    check_to_addr = models.TextField(blank=True, verbose_name="address for check mailing", help_text="For most requests, this should be blank for pickup in SAO (W20-549)")
    amount = models.DecimalField(max_digits=7, decimal_places=2, help_text='Do not include "$"')
    budget_area = models.ForeignKey(BudgetArea, related_name='as_budget_area')
    budget_term = models.ForeignKey(BudgetTerm)
    expense_area = models.ForeignKey(BudgetArea, related_name='as_expense_area') # ~GL
    incurred_time = models.DateTimeField(default=datetime.datetime.now, help_text='Time the item or service was purchased')
    request_time = models.DateTimeField(default=datetime.datetime.now)
    approval_time = models.DateTimeField(blank=True, null=True,)
    approval_status = models.IntegerField(default=0, choices=APPROVAL_STATES)
    name = models.CharField(max_length=50, verbose_name='short description', )
    description = models.TextField(blank=True, verbose_name='long description', )
    documentation = models.ForeignKey('Documentation', null=True, blank=True, )
    voucher       = models.ForeignKey('Voucher',       null=True, )
    rfp           = models.ForeignKey('RFP',           null=True, blank=True, )

    class Meta:
        permissions = (
            ('can_list', 'Can list requests',),
            ('can_approve', 'Can approve requests',),
            ('can_email', 'Can send mail about requests',),
        )
        ordering = ['id', ]

    def __unicode__(self, ):
        return "%s: %s %s (%s) (by %s) for $%s" % (
            self.name,
            self.check_to_first_name,
            self.check_to_last_name,
            self.check_to_email,
            self.submitter,
            self.amount,
        )

    def create_transfers(self, signatory, signatory_email=None):
        finance_core.models.make_transfer(
            self.name,
            self.amount,
            finance_core.models.LAYER_EXPENDITURE,
            self.budget_term,
            self.budget_area,
            self.expense_area,
            self.description,
            self.incurred_time,
        )

    def convert_to_voucher(self, signatory, signatory_email=None):
        if signatory_email is None:
            signatory_email = settings.SIGNATORY_EMAIL
        voucher = Voucher()
        voucher.group_name = settings.GROUP_NAME
        voucher.account = self.budget_area.get_account_number()
        voucher.signatory = signatory
        voucher.signatory_email = signatory_email
        voucher.first_name = self.check_to_first_name
        voucher.last_name = self.check_to_last_name
        voucher.email_address = self.check_to_email
        voucher.mailing_address = self.check_to_addr
        voucher.amount = self.amount
        voucher.description = self.label() + ': ' + self.name
        voucher.gl = self.expense_area.get_account_number()
        voucher.documentation = self.documentation
        voucher.save()
        self.create_transfers()
        self.approval_status = 1
        self.approval_time = datetime.datetime.now()
        self.voucher = voucher
        self.save()

    def convert_to_rfp(self, ):
        rfp = RFP()
        rfp.save()
        self.create_transfers()
        self.approval_status = APPROVAL_STATE_APPROVED
        self.approval_time = datetime.datetime.now()
        self.rfp = rfp
        self.save()

    def approve(self, approver, signatory_name, signatory_email=None, ):
        """Mark a request as approved.

        approver:       user object of the approving user
        signatory_name: name of signatory
        signatory_email: email address of signatory (provide None for default)
        """
        voucher = self.convert_to_voucher(signatory_name, signatory_email,)
        tmpl = get_template('vouchers/emails/request_approval_admin.txt')
        ctx = Context({
            'approver': approver,
            'request': self,
        })
        body = tmpl.render(ctx)
        mail_admins(
            'Request approval: %s approved $%s' % (
                approver,
                self.amount,
            ),
            body,
        )

    def approve_with_rfp(self, approver, ):
        

    def label(self, ):
        return settings.GROUP_ABBR + unicode(self.pk) + 'RR'

class Voucher(models.Model):
    group_name = models.CharField(max_length=40)
    account = models.IntegerField()
    signatory = models.CharField(max_length=50)
    signatory_email = models.EmailField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email_address = models.EmailField(max_length=50)
    mailing_address = models.TextField(blank=True, )
    amount = models.DecimalField(max_digits=7, decimal_places=2,)
    description = models.TextField()
    gl = models.IntegerField()
    processed = models.BooleanField()
    process_time = models.DateTimeField(blank=True, null=True,)
    documentation = models.ForeignKey('Documentation', blank=True, null=True, )

    def mailing_addr_lines(self):
        import re
        if self.mailing_address:
            lst = re.split(re.compile('[\n\r]*'), self.mailing_address)
            lst = filter(lambda elem: len(elem)>0, lst)
        else:
            lst = []
        lst = lst + ['']*(3-len(lst))
        return lst

    def mark_processed(self, ):
        self.process_time = datetime.datetime.now()
        self.processed = True
        self.save()

    def __unicode__(self, ):
        return "%s: %s %s (%s) for $%s" % (
            self.description,
            self.first_name,
            self.last_name,
            self.email_address,
            self.amount,
        )

    class Meta:
        permissions = (
            ('generate_vouchers', 'Can generate vouchers',),
        )


class Documentation(models.Model):
    backing_file = models.FileField(upload_to='documentation', verbose_name='File', help_text='PDF files only', )
    label = models.CharField(max_length=50, default="")
    submitter = models.CharField(max_length=30, null=True, ) # Username of submitter
    upload_time = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self, ):
        return "%s; uploaded at %s" % (self.label, self.upload_time, )


class StockEmail:
    def __init__(self, name, label, recipients, template, subject_template, context, ):
        """
        Initialize a stock email object.
        
        Each argument is required.
        
        name:       Short name. Letters, numbers, and hyphens only.
        label:      User-readable label. Briefly describe what the email says
        recipients: Who receives the email. List of "recipient" (check recipient), "area" (area owner), "admins" (site admins)
        template:   Django template filename with the actual text
        subject_template: Django template string with the subject
        context:    Type of context the email needs. Must be 'request' currently.
        """

        self.name       = name
        self.label      = label
        self.recipients = recipients
        self.template   = template
        self.subject_template = subject_template
        self.context    = context

    def send_email_request(self, request,):
        """
        Send an email that requires context "request".
        """

        assert self.context == 'request'

        # Generate text
        from django.template import Context, Template
        from django.template.loader import get_template
        ctx = Context({
            'prefix': settings.EMAIL_SUBJECT_PREFIX,
            'request': request,
            'sender': settings.USER_EMAIL_SIGNATURE,
        })
        tmpl = get_template(self.template)
        body = tmpl.render(ctx)
        subject_tmpl = Template(self.subject_template)
        subject = subject_tmpl.render(ctx)

        # Generate recipients
        recipients = []
        for rt in self.recipients:
            if rt == 'recipient':
                recipients.append(request.check_to_email)
            elif rt == 'area':
                recipients.append(request.budget_area.owner_address())
            elif rt == 'admins':
                pass # you don't *actually* have a choice...
        for name, addr in settings.ADMINS:
            recipients.append(addr)

        # Send mail!
        from django.core.mail import send_mail
        send_mail(
            subject,
            body,
            settings.SERVER_EMAIL,
            recipients,
        )

stock_emails = {
    'nodoc': StockEmail(
        name='nodoc',
        label='No documentation',
        recipients=['recipient', 'area',],
        template='vouchers/emails/no_docs_user.txt',
        subject_template='{{prefix}}Missing documentation for reimbursement',
        context = 'request',
    ),
    'voucher-sao': StockEmail(
        name='voucher-sao',
        label='Voucher submitted to SAO',
        recipients=['recipient', ],
        template='vouchers/emails/voucher_sao_user.txt',
        subject_template='{{prefix}}Reimbursement sent to SAO for processing',
        context = 'request',
    ),
}

class BulkRequestAction:
    def __init__(self, name, label, action, perm_predicate=None, ):
        self.name = name
        self.label = label
        self.action = action
        if perm_predicate is None:
            perm_predicate = lambda user: True
        elif perm_predicate == True:
            perm_predicate = lambda user: True
        self.perm_predicate = perm_predicate
    def can(self, user):
        return self.perm_predicate(user)
    def do(self, http_request, rr, ):
        if self.can(http_request.user):
            return self.action(http_request, rr, )
        else:
            return False, "permission denied"
    def __str__(self):
        return self.label
    @classmethod
    def filter_can_only(cls, actions, user):
        return [ action for action in actions if action.can(user) ]
def bulk_action_approve(http_request, rr):
    approver = http_request.user
    signatory_name = http_request.user.get_full_name()
    if rr.voucher:
        return False, "already approved"
    else:
        rr.approve(approver, signatory_name)
        return True, "request approved"

def bulk_action_email_factory(stock_email_obj):
    assert stock_email_obj.context == 'request'
    def inner(http_request, rr):
        stock_email_obj.send_email_request(rr)
        return True, "mail sent"
    return inner
def perm_checker(perm):
    def predicate(user):
        return user.has_perm(perm)
    return predicate

bulk_request_actions = []
if settings.SIGNATORY_EMAIL:
    bulk_request_actions.append(BulkRequestAction(
        name='approve',
        label='Approve Requests',
        action=bulk_action_approve,
        perm_predicate=perm_checker('vouchers.can_approve'),
    ))
for name, stockemail in stock_emails.items():
    if stockemail.context == 'request':
        bulk_request_actions.append(BulkRequestAction(
            name='email/%s' % name,
            label='Stock Email: %s' % stockemail.label,
            action=bulk_action_email_factory(stockemail),
            perm_predicate=perm_checker('vouchers.can_email'),
        ))
