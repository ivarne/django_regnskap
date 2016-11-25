from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django_regnskap import regnskap
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_regnskap.views.home', name='home'),
    # url(r'^django_regnskap/', include('django_regnskap.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^regnskap/', include('django_regnskap.regnskap.urls')),
    url(r'^faktura/',  include('django_regnskap.faktura.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^budsjett/', include('django_regnskap.budsjett.urls')),
    url(r'^lonn/', include('django_regnskap.lonn.urls')),
    url(r'^$', RedirectView.as_view(url= "/regnskap",permanent=True) )
)
if settings.SERVE_MEDIA_IN_PYTHON:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
