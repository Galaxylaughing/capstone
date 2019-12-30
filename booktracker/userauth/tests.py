from django.test import TestCase

# Create your tests here.
from .models import User


class UserTest(TestCase):
    """ Test module for User model """

    def setUp(self):
        User.objects.create(
          username='Caspar', password='acoolpassword')
    
    def test_username_matches(self):
        user = User.objects.get(username='Caspar')
        self.assertEqual(
            user.get_username(), 'Caspar')
    
    def test_hash_id_exists(self):
        user = User.objects.get(username='Caspar')
        self.assertIsInstance(
          user.hash_id, str)
