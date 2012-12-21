from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('django_regnskap.budsjett.views',
    url(r'^show/(\w+)$',     'show.show'),
    url(r'^(\w+)/(\d{4})$', 'show.list'),
)
