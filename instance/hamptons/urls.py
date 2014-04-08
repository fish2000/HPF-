
from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

app_patterns = patterns('',
    
    url(r'mobile/login/$',
        'hamptons.views.mobile_login',
        name='mobile_login'),
    
    url(r'mobile/(?P<document_id>[\w\-\_\.]+)$',
        'hamptons.views.mobile',
        name='mobile'),
    
    url(r'mobile/?$',
        RedirectView.as_view(
            url=reverse_lazy('hamptons:mobile',
            current_app='hamptons'),
        permanent=False)),
)

urlpatterns = patterns('',

    url(r'', include(app_patterns,
        namespace='hamptons', app_name='hamptons')),

)

