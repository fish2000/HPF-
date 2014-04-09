
from django.conf import settings
from appconf import AppConf

class SandpiperAppConf(AppConf):

    CHARSET = 'UTF-8'
    BASE_HOSTNAME = 'localhost'
    
    ADDRESS = '0.0.0.0'
    PORT = '9001'
    
    class Meta:

        prefix = 'SANDPIPER'

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


