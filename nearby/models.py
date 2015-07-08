import logging

import arrow
import requests
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from memoize import memoize

from django.conf import settings


log = logging.getLogger(__name__)


MEMOIZE_SECS = 60 * 60


class IECClient(object):
    def __init__(self, username, password, url=None):
        self.url = url or 'https://api.elections.org.za'
        self.username = username
        self.password = password

        self.token = None
        self.token_expires = None

    @memoize(timeout=MEMOIZE_SECS)
    def get(self, path, _auth=True, **params):
        url = self.url + path
        return requests.get(url, params=params, headers=self.headers(auth=_auth))

    def headers(self, auth=True):
        if not auth:
            return {}
        else:
            return {'Authorization': 'Bearer %s' % self.auth_token}

    def ward_councillor(self, ward_id):
        resp = self.get('/api/v1/LGEWardCouncilor?WardID=%s' % ward_id)
        resp.raise_for_status()

        if resp.status_code == 204 or not resp.text:
            return None
        return resp.json()

    @property
    def auth_token(self):
        if self.token and self.token_expires > arrow.now():
            return self.token
        return self.refresh_auth_token()

    def refresh_auth_token(self):
        log.info("Refreshing auth token")
        resp = requests.post(self.url + "/token", data={
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
        })
        resp.raise_for_status()
        data = resp.json()

        log.info("Got new auth token: %s" % data)
        self.token_expires = arrow.get(data['.expires'], 'ddd, DD MMM YYYY HH:mm:ss')
        self.token = data['access_token']
        return self.token


class WardInfoFinder(object):
    def __init__(self, iec_api, gsheets, sheet_key):
        self.iec = iec_api
        log.info("Fetching Google Sheets %s" % sheet_key)
        spreadsheet = gsheets.open_by_key(sheet_key)
        self.worksheet = spreadsheet.sheet1

    def ward_for_address(self, address):
        resp = requests.get('http://wards.code4sa.org', params={
            'address': address,
            'database': 'wards_2011'
        })
        resp.raise_for_status()
        data = resp.json()

        if 'error' in data:
            log.warn("Error for address '%s': %s" % (address, data))
            return None

        return data[0]

    def ward_for_location(self, lat, lng):
        return self.ward_for_address('%s,%s' % (lat, lng))

    def councillor_for_ward(self, ward_id, with_contact_details=True):
        data = self.iec.ward_councillor(ward_id)

        if with_contact_details:
            # merge in contact details
            data['custom_contact_details'] = self.councillor_contact_details(ward_id) or {}

        return data

    def councillor_contact_details(self, ward_id):
        """ Fetch councillor contact details for this ward.
        """
        for ward in self.gsheets_records():
            if str(ward['ward_id']) == ward_id:
                return ward

    @memoize(timeout=MEMOIZE_SECS)
    def gsheets_records(self):
        # get all records from the google sheet, as a list of dicts
        return self.worksheet.get_all_records()


def get_gsheets_creds(scope):
    return SignedJwtAssertionCredentials(
        settings.GOOGLE_SHEETS_EMAIL,
        settings.GOOGLE_SHEETS_PRIVATE_KEY,
        scope)


def get_gsheets_client():
    creds = get_gsheets_creds(['https://spreadsheets.google.com/feeds'])
    log.info("Authenticating with Google Sheets...")
    return gspread.authorize(creds)
