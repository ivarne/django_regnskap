from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('django_regnskap.regnskap.views',
    url(r'^registrer/(\w+)/externalActorJSON$', 'bilag.ajaxExternalActors'),
    url(r'^registrer/uploadsJSON$',             'bilag.ajaxDropboxUploads'),
    url(r'^registrer/(\w+)/(\d*)$',             'bilag.registrerBilagForm'),
    url(r'^dropbox/export/(\d{4})$',            'dropbox_integrations.saveBackup'),
    url(r'^dropbox/test',                       'dropbox_integrations.test'),
    url(r'^rapport/year/(\w+)(\d{4}).html$',    'rapport.showYear'),
    url(r'^rapport/year/(\w+)(\d{4})res.html$', 'rapport.offisielltRegnskap'),
    url(r'^rapport/year/(\d{4}).xls$',          'excel.export'),
    url(r'^show/bilag/(\d+)$',                  'show.bilag'),
    url(r'^show/external_actor/(\d+)$',         'show.externla_actor'),
    url(r'^show/konto/(\d+)$',                  'show.konto'),
    url(r'^$',                                  'menues.frontpage'),
)
