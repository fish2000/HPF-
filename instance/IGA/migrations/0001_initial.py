# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Twitterer'
        # db.create_table(u'IGA_twitterer', (
        #     (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        #     ('createdate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
        #     ('modifydate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        #     ('screen_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, unique=True, null=True, blank=True)),
        #     ('api_data', self.gf('IGA.modelfields.ElasticSearchData')(null=True, blank=True)),
        # ))
        # db.send_create_signal(u'IGA', ['Twitterer'])
        pass


    def backwards(self, orm):
        # Deleting model 'Twitterer'
        db.delete_table(u'IGA_twitterer')


    models = {
        u'IGA.twitterer': {
            'Meta': {'object_name': 'Twitterer'},
            'api_data': ('IGA.modelfields.ElasticSearchData', [], {'null': 'True', 'blank': 'True'}),
            'createdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifydate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'screen_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['IGA']