
import json
import requests

from django.db import models, connection
from django.db.models import signals
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext_lazy as _

from IGA.conf import settings

class JSONFieldEncoder(DjangoJSONEncoder):
    def __init__(self, *args, **kwargs):
        kwargs.pop('namedtuple_as_object', None)
        kwargs.pop('use_decimal', None)
        kwargs.pop('item_sort_key', None)
        kwargs.pop('for_json', None)
        kwargs.pop('bigint_as_string', None)
        kwargs.pop('tuple_as_array', None)
        kwargs.pop('ignore_nan', None)
        DjangoJSONEncoder.__init__(self, *args, **kwargs)

class MixIntrospector(object):
    
    def south_field_triple(self):
        """ Returns the field's module/classname pseudo-modulepath for South. """
        from south.modelsinspector import introspector
        field_class = "IGA.modelfields.%s" % self.__class__.__name__
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

class JSONField(models.TextField, MixIntrospector):
    """ JSONField is a TextField that stores Python tree values as JSON strings. """

    __metaclass__ = models.SubfieldBase
    description = _("Python Dictionary Structure Serialized as a String")

    def to_python(self, value):
        """ Convert the value to JSON from the string stored in the database. """
        if value == "":
            return None
        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass
        return value

    def get_db_prep_save(self, value, connection):
        """ Convert the object to a JSON string before saving. """
        if not value or value == "":
            return None
        if isinstance(value, (dict, list)):
            value = json.dumps(value, cls=JSONFieldEncoder)
        return super(JSONField, self).get_db_prep_save(value, connection)

    def value_to_string(self, obj):
        """ Return unicode data (for now) suitable for serialization. """
        return self.get_db_prep_value(self._get_val_from_obj(obj), connection)

class ElasticSearchData(JSONField):
    """ An ElasticSearchData field behaves in a manner indistinguishable from
    a JSONField, as far as Django application devs are concerned;
    its data is seamlessly synced with an ElasticSearch cluster instance (see below). """
    
    __metaclass__ = models.SubfieldBase
    description = _("")
    
    def __init__(self, *args, **kwargs):
        self.datum_id = kwargs.pop('datum_id', lambda instance, data: instance.id)
        super(ElasticSearchData, self).__init__(*args, **kwargs)
    
    def contribute_to_class(self, cls, name):
        super(ElasticSearchData, self).contribute_to_class(cls, name)
        signals.post_save.connect(self.reindex, sender=cls)
    
    def reindex(self, **kwargs):
        if kwargs.get('raw', False):
            return
        
        instance = kwargs.get('instance')
        sender = kwargs.get('sender')
        #update_fields = kwargs.get('update_fields'))
        
        data = getattr(instance, self.name, {})
        rosetta = self.datum_id
        datum_id = None
        
        if callable(rosetta):
            datum_id = rosetta(instance, data)
        elif rosetta in data:
            datum_id = data.get(rosetta)
        
        url = settings.IGA_URL.add_path("/%(app)s/%(model)s/%(id)s" % dict(
            app=sender._meta.app_label.lower(),
            model=sender._meta.model_name.lower(),
            id=datum_id)).lower()
        
        requests.put(url, data=json.dumps(data))



    