from django.test import TestCase

# Create your tests here.
class UserManagerViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/backend/user-manager/')
        self.assertEqual(resp.status_code, 200)