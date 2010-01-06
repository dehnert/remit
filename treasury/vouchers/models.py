from django.db import models
import settings
from finance_core.models import BudgetArea, BudgetTerm


class ReimbursementRequest(models.Model):
    submitter = models.CharField(max_length=10) # MIT username of submitter
    check_to_name = models.CharField(max_length=50, verbose_name="check recipient's name")
    check_to_email = models.EmailField(verbose_name="email address for check pickup")
    check_to_addr = models.TextField(blank=True, verbose_name="address for check mailing", help_text="For most requests, this should be blank for pickup in SAO (W20-549)")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    budget_area = models.ForeignKey(BudgetArea)
    budget_term = models.ForeignKey(BudgetTerm)
