from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django_regnskap import regnskap

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^regnskap/', include('django_regnskap.regnskap.urls')),
    url(r'^faktura/',  include('django_regnskap.faktura.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^budsjett/', include('django_regnskap.budsjett.urls')),
    url(r'^lonn/', include('django_regnskap.lonn.urls')),
    url(r'^$', RedirectView.as_view(url= "/regnskap", permanent=True) ),

    url(r'^(robots\.txt)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,}),
    url(r'^(favicon\.ico)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,})
)
if settings.SERVE_MEDIA_IN_PYTHON:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
   
if settings.SERVE_STATIC_IN_PYTHON:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
   )
