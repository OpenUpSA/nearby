from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/councillor')),
    url(r'^councillor/$', 'nearby.views.councillor', name='councillor'),
    url(r'^councillor/ward-(?P<ward_id>[0-9]+)$', 'nearby.views.ward_councillor', name='ward_councillor'),
)
