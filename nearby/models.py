import logging

import arrow
import requests


log = logging.getLogger(__name__)


class IECClient(object):
    def __init__(self, username, password, url=None):
        self.url = url or 'https://api.elections.org.za'
        self.username = username
        self.password = password

        self.token = None
        self.token_expires = None

    def get(self, path, _auth=True, **params):
        url = self.url + path
        return requests.get(url, params=params, headers=self.headers(auth=_auth))

    def headers(self, auth=True):
        if not auth:
            return {}
        else:
            return {'Authorization': 'Bearer %s' % self.auth_token}

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
    def __init__(self, iec_api):
        self.iec = iec_api

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

    def councillor_for_ward(self, ward):
        resp = self.iec.get('/api/v1/LGEWardCouncilor?WardID=%s' % ward)
        resp.raise_for_status()

        if resp.status_code == 204 or not resp.text:
            return None

        return resp.json()
