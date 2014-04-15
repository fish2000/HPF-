
from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

app_patterns = patterns('',
    
    # API calls
    url(r'api/frampton/list/(?P<lister>[\w\-\_\.]+)/?$',
        'hamptons.views.api_frampton_list',
        name='api_frampton_list'),
    
    # mobile-specific pages
    url(r'mobile/login/$',
        'hamptons.views.mobile_login',
        name='mobile_login'),
    
    url(r'mobile/frampton/(?P<frampton>[\w\-\_\.]+)$',
        'hamptons.views.frampton',
        name='frampton'),
    
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

