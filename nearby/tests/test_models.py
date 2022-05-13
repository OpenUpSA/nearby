from django.test import TestCase, Client


class TestModels(TestCase):

    def test_contact_info_present(self):
        response = Client().get("http://localhost:8000/councillor/ward-19100064.json")

        contact_info = response.json()["councillor"]["custom_contact_details"]

        test_contact_info = {'phone': '062-873-2894', 'email': 'aimeek.da@gmail.com'}
    
        self.assertEquals(response.status_code, 200)
        self.assertDictEqual(contact_info, test_contact_info)


    def test_contact_info_missing(self):
        response = Client().get("http://localhost:8000/councillor/ward-19100062.json")

        contact_info = response.json()["councillor"]["custom_contact_details"]

        test_contact_info = {}

        self.assertEquals(response.status_code, 200)
        self.assertDictEqual(contact_info, test_contact_info)
