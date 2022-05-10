from django.test import TestCase
import unittest
import requests


class TestModels(TestCase):

    def test_contact_info_present(self):
        response = requests.get("http://localhost:8000/councillor/ward-19100064.json")

        if response.status_code == 200:
            contact_info = response.json()["councillor"]["custom_contact_details"]

            self.assertEqual(r'contact_info, {"phone": "062-873-2894", "email": "aimeek.da@gmail.com"}')

        else:
            print(f"status code: {response.status_code}")


    def test_contact_info_missing(self):
        response = requests.get("http://localhost:8000/councillor/ward-19100062.json")

        if response.status_code == 200:
            contact_info = response.json()["councillor"]["custom_contact_details"]

            self.assertEqual(r'contact_info, {}')

        else:
            print(f"status code: {response.status_code}")