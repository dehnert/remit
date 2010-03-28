
from south.db import db
from django.db import models
from finance_core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'LineItem'
        db.create_table('finance_core_lineitem', (
            ('id', orm['finance_core.LineItem:id']),
            ('tx', orm['finance_core.LineItem:tx']),
            ('amount', orm['finance_core.LineItem:amount']),
            ('label', orm['finance_core.LineItem:label']),
            ('budget_area', orm['finance_core.LineItem:budget_area']),
            ('budget_term', orm['finance_core.LineItem:budget_term']),
            ('layer', orm['finance_core.LineItem:layer']),
        ))
        db.send_create_signal('finance_core', ['LineItem'])
        
        # Adding model 'Transaction'
        db.create_table('finance_core_transaction', (
            ('id', orm['finance_core.Transaction:id']),
            ('name', orm['finance_core.Transaction:name']),
            ('desc', orm['finance_core.Transaction:desc']),
        ))
        db.send_create_signal('finance_core', ['Transaction'])
        
        # Adding model 'BudgetTerm'
        db.create_table('finance_core_budgetterm', (
            ('id', orm['finance_core.BudgetTerm:id']),
            ('name', orm['finance_core.BudgetTerm:name']),
            ('slug', orm['finance_core.BudgetTerm:slug']),
            ('start_date', orm['finance_core.BudgetTerm:start_date']),
            ('end_date', orm['finance_core.BudgetTerm:end_date']),
            ('submit_deadline', orm['finance_core.BudgetTerm:submit_deadline']),
        ))
        db.send_create_signal('finance_core', ['BudgetTerm'])
        
        # Adding model 'BudgetArea'
        db.create_table('finance_core_budgetarea', (
            ('id', orm['finance_core.BudgetArea:id']),
            ('path', orm['finance_core.BudgetArea:path']),
            ('depth', orm['finance_core.BudgetArea:depth']),
            ('numchild', orm['finance_core.BudgetArea:numchild']),
            ('name', orm['finance_core.BudgetArea:name']),
            ('comment', orm['finance_core.BudgetArea:comment']),
            ('always', orm['finance_core.BudgetArea:always']),
            ('owner', orm['finance_core.BudgetArea:owner']),
            ('interested', orm['finance_core.BudgetArea:interested']),
            ('use_owner', orm['finance_core.BudgetArea:use_owner']),
            ('account_number', orm['finance_core.BudgetArea:account_number']),
        ))
        db.send_create_signal('finance_core', ['BudgetArea'])
        
        # Adding model 'BudgetAreaTerm'
        db.create_table('finance_core_budgetareaterm', (
            ('id', orm['finance_core.BudgetAreaTerm:id']),
            ('budget_area', orm['finance_core.BudgetAreaTerm:budget_area']),
            ('budget_term', orm['finance_core.BudgetAreaTerm:budget_term']),
            ('comment', orm['finance_core.BudgetAreaTerm:comment']),
        ))
        db.send_create_signal('finance_core', ['BudgetAreaTerm'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'LineItem'
        db.delete_table('finance_core_lineitem')
        
        # Deleting model 'Transaction'
        db.delete_table('finance_core_transaction')
        
        # Deleting model 'BudgetTerm'
        db.delete_table('finance_core_budgetterm')
        
        # Deleting model 'BudgetArea'
        db.delete_table('finance_core_budgetarea')
        
        # Deleting model 'BudgetAreaTerm'
        db.delete_table('finance_core_budgetareaterm')
        
    
    
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }
    
    complete_apps = ['finance_core']
