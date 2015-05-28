from django.conf.urls import patterns, url, include


urlpatterns = patterns('django_regnskap.budsjett.views',
    url(r'^show/(\w+)$',     'show.show'),
    url(r'^(\w+)/(\d{4})$', 'show.list'),
)
