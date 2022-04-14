from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.urls import path
from django.views.generic.base import RedirectView
from django.views.decorators.cache import cache_page
from django.contrib import admin

from nearby.views import ward_councillor, councillor, councillor_suggestion

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/councillor')),
    path('councillor/', councillor, name='councillor'),
    url(r'^councillor/ward-(?P<ward_id>[0-9]+)(\.(?P<format>json|html))?$',
        # cache for 12 hours
        cache_page(60 * 60 * 12)(ward_councillor), name='ward_councillor'),
    path('councillor/suggestion/', councillor_suggestion, name='councillor_suggestion'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
