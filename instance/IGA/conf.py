
from urlstring import URL
from django.conf import settings
from appconf import AppConf

class IGAAppConf(AppConf):

    CHARSET = 'UTF-8'
    BASE_HOSTNAME = 'localhost'
    PORT = 9200
    
    URL = 'http://localhost:9200/'
    
    class Meta:

        prefix = 'IGA'

    def configure_base_hostname(self, value):
        """ Infer the local hostname """
        if value is not None:
            return value
        import platform
        local_hostname = platform.node().lower()
        return local_hostname.endswith('local') and 'localhost' \
            or local_hostname
    
    def configure_port(self, value):
        """ Integer port value """
        if value is not None:
            return int(value)
        return 9001
    
    def configure_url(self, value):
        return URL(value or 'http://%s:%s/' % (
            self.BASE_HOSTNAME,
            self.PORT))


