
from south.db import db
from django.db import models
from vouchers.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Documentation.submitter'
        db.add_column('vouchers_documentation', 'submitter', orm['vouchers.documentation:submitter'])
        
        # Adding field 'Documentation.upload_time'
        db.add_column('vouchers_documentation', 'upload_time', orm['vouchers.documentation:upload_time'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Documentation.submitter'
        db.delete_column('vouchers_documentation', 'submitter')
        
        # Deleting field 'Documentation.upload_time'
        db.delete_column('vouchers_documentation', 'upload_time')
        
    
    
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
        'vouchers.documentation': {
            'backing_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'submitter': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
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
            'documentation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vouchers.Documentation']", 'null': 'True'}),
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
            'documentation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vouchers.Documentation']", 'null': 'True'}),
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
