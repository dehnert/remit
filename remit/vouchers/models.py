from django.db import models
import settings
from finance_core.models import BudgetArea, BudgetTerm

import datetime

APPROVAL_STATES = (
    ( 0, 'Pending'),
    ( 1, 'Approved'),
    (-1, 'Rejected'),
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


class Voucher(models.Model):
    group_name = models.CharField(max_length=10)
    account = models.IntegerField()
    signatory = models.CharField(max_length=50)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email_address = models.EmailField(max_length=50)
    mailing_address = models.TextField()
    amount = models.DecimalField(max_digits=7, decimal_places=2,)
    description = models.TextField()
    gl = models.IntegerField()
