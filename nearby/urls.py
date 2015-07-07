from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView
from django.views.decorators.cache import cache_page

import nearby.views

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/councillor')),
    url(r'^councillor/$', 'nearby.views.councillor', name='councillor'),
    url(r'^councillor/ward-(?P<ward_id>[0-9]+)$',
        # cache for 12 hours
        cache_page(60 * 60 * 12)(nearby.views.ward_councillor), name='ward_councillor'),
)
