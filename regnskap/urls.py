from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
#    url(r'^$', 'regnskap.views.default'),
    url(r'^registrer$','regnskap.views.bilag.registrerBilagForm'),
    url(r'^registrer/externalActorJSON$', 'regnskap.views.bilag.ajaxExternalActors'),
    url(r'^export/(\d{4})/$','regnskap.views.excel.export'),
    url(r'^dropbox/connect$','regnskap.views.dropbox_integrations.connect'),
    url(r'^drpobox/export/(\d{4})$', 'regnskap.views.dropbox_integrations.saveBackup'),
    url(r'^rapport/year/(\d{4})$' , 'regnskap.views.rapport.showYear'),
)