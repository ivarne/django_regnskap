from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('django_regnskap.regnskap.views',
#    url(r'^$', 'regnskap.views.default'),
    url(r'^registrer/(\w+)/externalActorJSON$', 'bilag.ajaxExternalActors'),
    url(r'^registrer/(\w+)/$',                  'bilag.registrerBilagForm'),
    url(r'^dropbox/export/(\d{4})$',            'dropbox_integrations.saveBackup'),
    url(r'^rapport/(\w+)/year/(\d{4}).html$',   'rapport.showYear'),
    url(r'^rapport/(\w+)/year/(\d{4}).xls$',    'excel.export'),
    url(r'^$',                                  'menues.frontpage'),
)