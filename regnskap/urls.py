from django.conf.urls.defaults import patterns, include, url

module = "django_regnskap.regnskap.views."

urlpatterns = patterns('',
#    url(r'^$', 'regnskap.views.default'),
    url(r'^registrer$', module + 'bilag.registrerBilagForm'),
    url(r'^registrer/externalActorJSON$', module + 'bilag.ajaxExternalActors'),
    url(r'^export/(\d{4})/$', module + 'excel.export'),
    url(r'^dropbox/connect$', module + 'dropbox_integrations.connect'),
    url(r'^drpobox/export/(\d{4})$', module + 'dropbox_integrations.saveBackup'),
    url(r'^rapport/year/(\d{4})$' , module + 'rapport.showYear'),
)