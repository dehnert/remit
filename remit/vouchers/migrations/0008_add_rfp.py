# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RFP'
        db.create_table('vouchers_rfp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('vouchers', ['RFP'])

        # Adding field 'ReimbursementRequest.rfp'
        db.add_column('vouchers_reimbursementrequest', 'rfp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vouchers.RFP'], null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'RFP'
        db.delete_table('vouchers_rfp')

        # Deleting field 'ReimbursementRequest.rfp'
        db.delete_column('vouchers_reimbursementrequest', 'rfp_id')


    models = {
        'finance_core.budgetarea': {
            'Meta': {'ordering': "['path']", 'object_name': 'BudgetArea'},
            'account_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'budget_term': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['finance_core.BudgetTerm']", 'through': "orm['finance_core.BudgetAreaTerm']", 'symmetrical': 'False'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interested': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'use_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'finance_core.budgetareaterm': {
            'Meta': {'object_name': 'BudgetAreaTerm'},
            'budget_area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['finance_core.BudgetArea']"}),
            'budget_term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['finance_core.BudgetTerm']"}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'finance_core.budgetterm': {
            'Meta': {'object_name': 'BudgetTerm'},
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '20', 'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'submit_deadline': ('django.db.models.fields.DateField', [], {})
        },
        'vouchers.documentation': {
            'Meta': {'object_name': 'Documentation'},
            'backing_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'submitter': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'vouchers.reimbursementrequest': {
            'Meta': {'ordering': "['id']", 'object_name': 'ReimbursementRequest'},
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
            'documentation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vouchers.Documentation']", 'null': 'True', 'blank': 'True'}),
            'expense_area': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'as_expense_area'", 'to': "orm['finance_core.BudgetArea']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incurred_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'request_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'rfp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vouchers.RFP']", 'null': 'True', 'blank': 'True'}),
            'submitter': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'voucher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vouchers.Voucher']", 'null': 'True'})
        },
        'vouchers.rfp': {
            'Meta': {'object_name': 'RFP'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'vouchers.voucher': {
            'Meta': {'object_name': 'Voucher'},
            'account': ('django.db.models.fields.IntegerField', [], {}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'documentation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vouchers.Documentation']", 'null': 'True', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '50'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'gl': ('django.db.models.fields.IntegerField', [], {}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'mailing_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'process_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'signatory': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'signatory_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        }
    }

    complete_apps = ['vouchers']
