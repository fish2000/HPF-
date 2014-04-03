
from django.conf.urls.static import static
# from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, include, url
# from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

from hamptons.urls import app_patterns as hamptons_urlpatterns

urlpatterns = patterns('',
    
    url(r'^hamptons/',
        include(hamptons_urlpatterns,
            namespace='hamptons',
            app_name='hamptons')),

    url(r'^admin/',
        include(admin.site.urls)),

)


from django.conf import settings
if not settings.DEPLOYED:
    
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
    
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT)

