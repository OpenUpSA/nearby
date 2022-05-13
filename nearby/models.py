import logging

import arrow
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from memoize import memoize

from django.conf import settings
from django.core.cache import caches

from django.db import models


log = logging.getLogger(__name__)


class CouncillorContactInfo(models.Model):

    id = models.AutoField(primary_key=True)    
    ward_id = models.CharField(max_length=100, unique=True)
    councillor = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.ward_id


# How long should we cache google sheets and IEC data for?
# Bear in mind that we cache an entire ward page for 12 hours
MEMOIZE_SECS = 60 * 60


class IECClient:
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
            return {'Authorization': f'Bearer {self.auth_token}'}

    def ward_councillor(self, ward_id):
        resp = self.get(f'/api/v1/LGEWardCouncilor?WardID={ward_id}')
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
        if resp.status_code == 400:
            log.warning(resp.content)
        resp.raise_for_status()
        data = resp.json()

        log.info(f"Got new auth token: {data}")
        self.token_expires = arrow.get(data['.expires'], 'ddd, DD MMM YYYY HH:mm:ss')
        self.token = data['access_token']
        return self.token


class WardInfoFinder:
    def __init__(self, iec_api, sheet_key):
        self.iec = iec_api
        self.sheet_key = sheet_key
        # We use this cache to store the results from the IEC
        # indefinitely, and use them as a fallback when the IEC's
        # site is down.
        self.cache = caches['iec']

    def ward_for_address(self, address):
        resp = requests.get('https://mapit.code4sa.org/address', verify=False, params={
            'address': address,
            'generation': 2,
            'type': 'WD',
        })
        resp.raise_for_status()
        data = resp.json()

        if 'error' in data:
            log.warning(f"Error for address '{address}': {data}")
            return None

        data = [v for k, v in data.iteritems() if k != "addresses"]
        if data:
            return data[0]
        return None

    def ward_for_location(self, lat, lng):
        resp = requests.get(f'https://mapit.code4sa.org/point/4326/{lng},{lat}', verify=False, params={
            'generation': 2,
            'type': 'WD',
        })
        resp.raise_for_status()
        data = resp.json()

        if 'error' in data:
            log.warning(f"Error for lat/long {lat}, {lng}: {data}")
            return None

        if data:
            return list(data.values())[0]
        return None

    def councillor_for_ward(self, ward_id, with_contact_details=True):
        cache_key = f'councillor-ward-{ward_id}'

        try:
            data = self.iec.ward_councillor(ward_id)
            if not data:
                return None
            self.cache.set(cache_key, data, None)
        except requests.HTTPError as e:
            # try the cache
            log.warning(f"Error from IEC, trying our local cache: {e}", exc_info=e)
            data = self.cache.get(cache_key)
            if data is None:
                # no luck :(
                raise e


        ward_contact_info = CouncillorContactInfo.objects.filter(ward_id=ward_id) # Fetch CouncillorContactInfo matching ward_id
        
        try:
            if ward_contact_info.values_list("ward_id", flat=True)[0] != ward_id: # if 0 matches use empty dict
                data["custom_contact_details"] = {}
            else:  # else turn 1st match into dict and use that
                data['custom_contact_details'] = {
                    "phone": ward_contact_info.values_list("phone", flat=True)[0],
                    "email": ward_contact_info.values_list("email", flat=True)[0]
                    }
        
        except Exception as e:
            log.warning(f"Error: {e}")

        print(f"data: {data}")

        return data


_gsheets_creds = None


def get_gsheets_creds():
    global _gsheets_creds
    scope = ['https://spreadsheets.google.com/feeds']

    if not _gsheets_creds:
        _gsheets_creds = ServiceAccountCredentials(
            settings.GOOGLE_SHEETS_EMAIL,
            settings.GOOGLE_SHEETS_PRIVATE_KEY,
            scope)

    return _gsheets_creds


def get_gsheets_client():
    return gspread.authorize(get_gsheets_creds())