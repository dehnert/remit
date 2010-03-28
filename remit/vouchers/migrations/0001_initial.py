
from south.db import db
from django.db import models
from vouchers.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Voucher'
        db.create_table('vouchers_voucher', (
            ('id', orm['vouchers.Voucher:id']),
            ('group_name', orm['vouchers.Voucher:group_name']),
            ('account', orm['vouchers.Voucher:account']),
            ('signatory', orm['vouchers.Voucher:signatory']),
            ('signatory_email', orm['vouchers.Voucher:signatory_email']),
            ('first_name', orm['vouchers.Voucher:first_name']),
            ('last_name', orm['vouchers.Voucher:last_name']),
            ('email_address', orm['vouchers.Voucher:email_address']),
            ('mailing_address', orm['vouchers.Voucher:mailing_address']),
            ('amount', orm['vouchers.Voucher:amount']),
            ('description', orm['vouchers.Voucher:description']),
            ('gl', orm['vouchers.Voucher:gl']),
            ('processed', orm['vouchers.Voucher:processed']),
        ))
        db.send_create_signal('vouchers', ['Voucher'])
        
        # Adding model 'ReimbursementRequest'
        db.create_table('vouchers_reimbursementrequest', (
            ('id', orm['vouchers.ReimbursementRequest:id']),
            ('submitter', orm['vouchers.ReimbursementRequest:submitter']),
            ('check_to_first_name', orm['vouchers.ReimbursementRequest:check_to_first_name']),
            ('check_to_last_name', orm['vouchers.ReimbursementRequest:check_to_last_name']),
            ('check_to_email', orm['vouchers.ReimbursementRequest:check_to_email']),
            ('check_to_addr', orm['vouchers.ReimbursementRequest:check_to_addr']),
            ('amount', orm['vouchers.ReimbursementRequest:amount']),
            ('budget_area', orm['vouchers.ReimbursementRequest:budget_area']),
            ('budget_term', orm['vouchers.ReimbursementRequest:budget_term']),
            ('expense_area', orm['vouchers.ReimbursementRequest:expense_area']),
            ('request_time', orm['vouchers.ReimbursementRequest:request_time']),
            ('approval_time', orm['vouchers.ReimbursementRequest:approval_time']),
            ('approval_status', orm['vouchers.ReimbursementRequest:approval_status']),
            ('printing_time', orm['vouchers.ReimbursementRequest:printing_time']),
            ('name', orm['vouchers.ReimbursementRequest:name']),
            ('description', orm['vouchers.ReimbursementRequest:description']),
        ))
        db.send_create_signal('vouchers', ['ReimbursementRequest'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Voucher'
        db.delete_table('vouchers_voucher')
        
        # Deleting model 'ReimbursementRequest'
        db.delete_table('vouchers_reimbursementrequest')
        
    
    
    models = {
        'finance_core.budgetarea': {
            'account_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'budget_term': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['finance_core.BudgetTerm']"}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interested': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'use_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'finance_core.budgetterm': {
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '20', 'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'submit_deadline': ('django.db.models.fields.DateField', [], {})
        },
        'vouchers.reimbursementrequest': {
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'approval_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'approval_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'budget_area': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'as_budget_area'", 'to': "orm['finance_core.BudgetArea']"}),
            'budget_term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['finance_core.BudgetTerm']"}),
            'check_to_addr': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'check_to_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'check_to_first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'check_to_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expense_area': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'as_expense_area'", 'to': "orm['finance_core.BudgetArea']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'printing_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'request_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'submitter': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'vouchers.voucher': {
            'account': ('django.db.models.fields.IntegerField', [], {}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '50'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'gl': ('django.db.models.fields.IntegerField', [], {}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'mailing_address': ('django.db.models.fields.TextField', [], {}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'signatory': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'signatory_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        }
    }
    
    complete_apps = ['vouchers']
