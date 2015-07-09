import logging
import re
from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import Http404
from django import forms

from .models import WardInfoFinder, IECClient, get_gsheets_client


# re-use this guy so that it caches the auth token
iec_client = IECClient(settings.IEC_API_USERNAME, settings.IEC_API_PASSWORD)

finder = WardInfoFinder(iec_client, settings.GOOGLE_SHEETS_SHEET_KEY)
log = logging.getLogger(__name__)


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


class SuggestionForm(forms.Form):
    ward_id = forms.CharField(widget=forms.HiddenInput())
    councillor_name = forms.CharField(label='Councillor name', required=False)
    councillor_email = forms.EmailField(label='Councillor email address', required=False)
    councillor_phone = forms.CharField(label='Councillor phone number', required=False)
    email = forms.CharField(label="Your email address", required=False)

    # honeypot, if this is filled in it's probably spam
    website = forms.CharField(label='Leave this blank', required=False)

    def save(self, request):
        # check for honey pot, if this is filled in, ignore the submission
        if self.cleaned_data['website']:
            log.info("Honeypot not empty, ignoring spammy submission: %s" % self.cleaned_data)
            return

        sheets = get_gsheets_client()
        spreadsheet = sheets.open_by_key(settings.GOOGLE_SHEETS_SHEET_KEY)
        worksheet = spreadsheet.worksheet('Suggestions')

        log.info("Saving suggestion: %s" % self.cleaned_data)
        worksheet.append_row([
            datetime.now().isoformat(),
            self.cleaned_data['ward_id'],
            self.cleaned_data['councillor_name'],
            self.cleaned_data['councillor_email'],
            self.cleaned_data['councillor_phone'],
            self.cleaned_data['email'],
            request.META.get('HTTP_USER_AGENT', ''),
            request.META.get('HTTP_X_FORWARDED_FOR', ''),
        ])
        log.info("Saved")


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
