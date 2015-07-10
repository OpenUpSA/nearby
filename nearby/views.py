import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import Http404
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import WardInfoFinder, IECClient
from .forms import SuggestionForm


# re-use this guy so that it caches the auth token
iec_client = IECClient(settings.IEC_API_USERNAME, settings.IEC_API_PASSWORD)

finder = WardInfoFinder(iec_client, settings.GOOGLE_SHEETS_SHEET_KEY)


def normalise_url(url):
    if not url:
        return url

    return re.sub(r'https?://', '', url.lower())


@xframe_options_exempt
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


@xframe_options_exempt
def ward_councillor(request, ward_id):
    councillor = finder.councillor_for_ward(ward_id)
    if not councillor:
        raise Http404()

    location = {
        'councillor': councillor,
    }

    location['ward_id'] = councillor['Delimitation']['WardID']
    location['ward_number'] = location['ward_id'] % 1000
    location['province'] = councillor['Delimitation']['Province']
    # JHB - City of Johannesburg [Johannesburg]
    muni = councillor['Delimitation']['Municipality'].split('-', 1)[1]
    location['municipality'] = re.sub(r'\s*\[[^\]]+\]\s*', '', muni)

    location['councillor']['Municipality']['ContactDetails']['WebsiteUrl'] = \
        normalise_url(location['councillor']['Municipality']['ContactDetails']['WebsiteUrl'])
    location['councillor']['PartyDetail']['ContactDetails']['WebsiteUrl'] = \
        normalise_url(location['councillor']['PartyDetail']['ContactDetails']['WebsiteUrl'])

    form = SuggestionForm(data={'ward_id': ward_id})

    return render(request, 'councillor/ward.html', dict(
                  location=location,
                  suggest_form=form))


@xframe_options_exempt
def councillor_suggestion(request):
    """ Process a suggestion for new data.
    """
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            form.save(request)

        if form.cleaned_data['ward_id']:
            return redirect(reverse('ward_councillor', kwargs={'ward_id': form.cleaned_data['ward_id']}))

    return redirect('/')
