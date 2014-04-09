
from django.db import models
from datetime import datetime
from modeldict import ModelDict
#from IGA.conf import settings
from IGA import modelfields


class Twitterer(models.Model):
    
    class Meta:
        verbose_name = 'Twitter User'
        verbose_name_plural = 'Twitter User Data'
        abstract = False
    
    createdate = models.DateTimeField('Created on',
        default=datetime.now,
        auto_now_add=True,
        blank=True,
        editable=False)
    
    modifydate = models.DateTimeField('Last modified on',
        default=datetime.now,
        auto_now=True,
        blank=True,
        editable=False)
    
    screen_name = models.CharField(verbose_name="Twitter Screen Name",
        max_length=100,
        db_index=True,
        unique=True,
        blank=True,
        null=True)
    
    api_data = modelfields.ElasticSearchData(
        verbose_name='Twiter API Data',
        datum_id=lambda instance, data: data['id'],
        null=True,
        blank=True)
    
    @classmethod
    def query(cls):
        from elasticutils import S
        return S().indexes(
            cls._meta.app_label.lower()).doctypes(
                cls._meta.model_name.lower())
    
    def __repr__(self):
        return u"@%s" % (
            self.screen_name or "???")
    
    def __str__(self):
        return repr(self)
    
    def __unicode__(self):
        return unicode(str(self))
    

twitterers = ModelDict(Twitterer,
    key='screen_name',
    value='api_data',
    instances=False)
