from django.test import TestCase
from nearby.models import CouncillorContactInfo


class TestModels(TestCase):

    def test_model_str(self):
        ward0 = CouncillorContactInfo.objects.create(
            ward_id="314159",
            councillor="Jim Testingson",
            phone="123 456 7890",
            email="jim@gov.za"
        )

        self.assertEqual(str(ward0), "314159")
