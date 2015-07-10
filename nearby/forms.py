import logging

from datetime import datetime

from django.conf import settings
from django import forms
from django.core.mail import mail_admins
from django.template.loader import render_to_string

from .models import get_gsheets_client


log = logging.getLogger(__name__)


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
            self.cleaned_data['councillor_phone'],
            self.cleaned_data['councillor_email'],
            self.cleaned_data['email'],
            request.META.get('HTTP_USER_AGENT', ''),
            request.META.get('HTTP_X_FORWARDED_FOR', ''),
        ])
        log.info("Saved")

        log.info("Sending email")
        mail_admins('New Ward Councillor Suggestion', '',
                    html_message=render_to_string('councillor/suggestion_email.html', self.cleaned_data))
        log.info("Sent")
