
from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

app_patterns = patterns('',
    
    url(r'mobile/(?P<document_id>[\w\-\_\.]+)$',
        'hamptons.views.mobile',
        name='mobile'),
    
    url(r'mobile/?$',
        RedirectView.as_view(
            url=reverse_lazy('hamptons:mobile',
            current_app='hamptons'),
        permanent=False)),
    
    # url(r'download/(?P<document_id>[\w\-\_]+)/text/?$',
    #     'tika.views.download_text',
    #     name='download-text'),
    
    # url(r'(?P<document_id>[\w\-\_]+)/cleansed-html-viewer/?$',
    #     'tika.views.get_cleansed_html_viewer',
    #     name='cleansed-html-viewer'),
    
)

urlpatterns = patterns('',

    url(r'', include(app_patterns,
        namespace='hamptons', app_name='hamptons')),

)

