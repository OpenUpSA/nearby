from django.test import TestCase
from nearby.models import CouncillorContactInfo


class TestModels(TestCase):

    def test_model_str(self):
        ward_id = CouncillorContactInfo.objects.create(ward_id="314159")
        councillor = CouncillorContactInfo.objects.create(councillor="Jim Testingson")
        phone = CouncillorContactInfo.objects.create(phone="123 456 7890")
        email = CouncillorContactInfo.objects.create(email="jim@gov.za")

        self.assertEqual(str(ward_id), "314159")
        self.assertEqual(str(councillor), "Jim Testingson")
        self.assertEqual(str(phone), "123 456 7890")
        self.assertEqual(str(email), "jim@gov.za")
