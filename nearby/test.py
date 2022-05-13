from django.test import Client, TestCase


class IndexTestCase(TestCase):
    def test_index(self):
        c = Client()
        response = c.get("/councillor/")
        self.assertContains(response, "Find your ward councillor")

