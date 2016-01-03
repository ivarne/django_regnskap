from django.conf.urls import patterns, url, include

urlpatterns = patterns('django_regnskap.lonn.views',
    url(r'^lonnslipp/(\d+)$',       'lonnPDF.generate_slip_response'),
    url(r'^perioderapport/(\d+)$',  'lonnPDF.generate_periode_response'),
    url(r'^$',                      'views.show'),
    url(r'^periode/(\d+)',          'views.periode'),
    url(r'^finalizePeriode/(\d+)$',    'views.finalize_periode'),
    )
