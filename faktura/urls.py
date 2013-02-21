from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('django_regnskap.faktura.views',
    url(r'^list/(\w+)$',        'views.list_faktura'),
    url(r'^list_vare/(\w+)$',   'views.list_vare'),
    url(r'^show/(\d+)$',        'views.show_faktura'),
    url(r'^create/(\w+)/(\d+)/?(\d*)$','create.create_faktura'),
    url(r'^send$',              'views.send_faktura'),
    url(r'^betal/(\d+)$',            'views.betal_faktura'),
    url(r'^generate/(\d*)$',    'fakturaPDF.generate_response'),
)