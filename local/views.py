import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import Http404

from local.models import WardInfoFinder, IECClient


# re-use this guy so that it caches the auth token
finder = WardInfoFinder(IECClient(settings.IEC_API_USERNAME, settings.IEC_API_PASSWORD))


def normalise_url(url):
    if not url:
        return url

    return re.sub(r'https?://', '', url.lower())


def councillor(request):
    bad_address = False
    ward = None

    if request.GET.get('address'):
        ward = finder.ward_for_address(request.GET.get('address'))
        if not ward:
            bad_address = True

    if request.GET.get('lat') and request.GET.get('lng'):
        ward = finder.ward_for_location(request.GET.get('lat'), request.GET.get('lng'))
        if not ward:
            bad_address = True

    if ward:
        return redirect(reverse('ward_councillor', kwargs={'ward_id': ward['ward']}))

    return render(request, 'councillor/index.html', dict(
                  bad_address=bad_address))


def ward_councillor(request, ward_id):
    councillor = finder.councillor_for_ward(ward_id)
    if not councillor:
        raise Http404()

    location = {
        'councillor': councillor,
    }

    location['ward_id'] = councillor['Delimitation']['WardID']
    location['province'] = councillor['Delimitation']['Province']
    # JHB - City of Johannesburg [Johannesburg]
    muni = councillor['Delimitation']['Municipality'].split('-', 1)[1]
    location['municipality'] = re.sub(r'\s*\[[^\]]+\]\s*', '', muni)

    location['councillor']['Municipality']['ContactDetails']['WebsiteUrl'] = \
        normalise_url(location['councillor']['Municipality']['ContactDetails']['WebsiteUrl'])
    location['councillor']['PartyDetail']['ContactDetails']['WebsiteUrl'] = \
        normalise_url(location['councillor']['PartyDetail']['ContactDetails']['WebsiteUrl'])

    return render(request, 'councillor/ward.html', dict(
                  location=location))
