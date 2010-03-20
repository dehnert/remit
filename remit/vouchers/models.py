from django.db import models
import settings
import finance_core
from finance_core.models import BudgetArea, BudgetTerm

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
    submitter = models.CharField(max_length=10) # MIT username of submitter
    check_to_first_name = models.CharField(max_length=50, verbose_name="check recipient's first name")
    check_to_last_name = models.CharField(max_length=50, verbose_name="check recipient's last name")
    check_to_email = models.EmailField(verbose_name="email address for check pickup")
    check_to_addr = models.TextField(blank=True, verbose_name="address for check mailing", help_text="For most requests, this should be blank for pickup in SAO (W20-549)")
    amount = models.DecimalField(max_digits=7, decimal_places=2, help_text='Do not include "$"')
    budget_area = models.ForeignKey(BudgetArea, related_name='as_budget_area')
    budget_term = models.ForeignKey(BudgetTerm)
    expense_area = models.ForeignKey(BudgetArea, related_name='as_expense_area') # ~GL
    request_time = models.DateTimeField(default=datetime.datetime.now)
    approval_time = models.DateTimeField(blank=True, null=True,)
    approval_status = models.IntegerField(default=0, choices=APPROVAL_STATES)
    printing_time = models.DateTimeField(blank=True, null=True,)
    name = models.CharField(max_length=50, verbose_name='short description', )
    description = models.TextField(blank=True, verbose_name='long description', )

    class Meta:
        permissions = (
            ('can_list', 'Can list requests',),
            ('can_approve', 'Can approve requests',),
            ('can_email', 'Can send mail about requests',),
        )

    def __unicode__(self, ):
        return "%s: %s %s (%s) (by %s) for $%s" % (
            self.name,
            self.check_to_first_name,
            self.check_to_last_name,
            self.check_to_email,
            self.submitter,
            self.amount,
        )

    def convert(self, signatory, signatory_email=settings.SIGNATORY_EMAIL):
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
        voucher.save()
        finance_core.models.make_transfer(
            self.name,
            self.amount,
            finance_core.models.LAYER_EXPENDITURE,
            self.budget_term,
            self.budget_area,
            self.expense_area,
            self.description,
        )
        self.approval_status = 1
        self.approval_time = datetime.datetime.now()
        self.save()

    def label(self, ):
        return settings.GROUP_ABBR + unicode(self.pk) + 'RR'

class Voucher(models.Model):
    group_name = models.CharField(max_length=10)
    account = models.IntegerField()
    signatory = models.CharField(max_length=50)
    signatory_email = models.EmailField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email_address = models.EmailField(max_length=50)
    mailing_address = models.TextField()
    amount = models.DecimalField(max_digits=7, decimal_places=2,)
    description = models.TextField()
    gl = models.IntegerField()
    processed = models.BooleanField()

    def mailing_addr_lines(self):
        import re
        if self.mailing_address:
            lst = re.split(re.compile('[\n\r]*'), self.mailing_address)
            lst = filter(lambda elem: len(elem)>0, lst)
        else:
            lst = []
        lst = lst + ['']*(3-len(lst))
        return lst

    class Meta:
        permissions = (
            ('generate_vouchers', 'Can generate vouchers',),
        )


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
