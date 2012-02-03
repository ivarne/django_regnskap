from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'regnskap.views.default'),
    url(r'^registrer$','regnskap.views.registerform'),
)
