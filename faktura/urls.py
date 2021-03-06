from django.conf.urls import patterns, url, include


urlpatterns = patterns('django_regnskap.faktura.views',
    url(r'^list/(\w+)$',        'views.list_faktura'),
    url(r'^list_vare/(\w+)$',   'views.list_vare'),
    url(r'^show/(\d+)$',        'views.show_faktura'),
    url(r'^create/(\w+)/(\d+)/?(\d*)$','create.create_faktura'),
    url(r'^send$',              'views.send_faktura'),
    url(r'^betal/(\d+)$',       'views.betal_faktura'),
    url(r'^generate/(\d*)$',    'fakturaPDF.generate_response'),
    url(r'^draft/(\d+)/(\d+)',  'views.betal_faktura_draft'),
    url(r'^kreditnota',         'views.kreditnota'),
    url(r'^purring',            'views.purring'),
)
