
from south.db import db
from django.db import models
from finance_core.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
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
        'finance_core.budgetareaterm': {
            'budget_area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['finance_core.BudgetArea']"}),
            'budget_term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['finance_core.BudgetTerm']"}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'finance_core.budgetterm': {
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '20', 'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'submit_deadline': ('django.db.models.fields.DateField', [], {})
        },
        'finance_core.lineitem': {
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'budget_area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['finance_core.BudgetArea']"}),
            'budget_term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['finance_core.BudgetTerm']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'layer': ('django.db.models.fields.IntegerField', [], {}),
            'tx': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['finance_core.Transaction']"})
        },
        'finance_core.transaction': {
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incurred_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'tx_create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }
    
    complete_apps = ['finance_core']
