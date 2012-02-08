from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'regnskap.views.default'),
    url(r'^registrer$','regnskap.views.registrerBilagForm'),
    url(r'^export/(\d{4})/$','regnskap.views.export')
)
