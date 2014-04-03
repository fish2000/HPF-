
from django.conf import settings
from appconf import AppConf

class HamptonsAppConf(AppConf):

    CHARSET = 'UTF-8'
    BASE_HOSTNAME = 'localhost'
    
    class Meta:

        prefix = 'HAMPTONS'

    def configure_base_hostname(self, value):
        """ Infer the local hostname """

        if value is not None:
            return value
        import platform
        local_hostname = platform.node().lower()
        return local_hostname.endswith('local') and 'localhost' \
            or local_hostname



