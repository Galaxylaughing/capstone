from django.test import TestCase

# Create your tests here.
from .models import User
from .serializers import UserSerializer


class UserTest(TestCase):
    """ Test module for User model """

    def setUp(self):
        """ create a user instance """
        self.user = User.objects.create(
          username='Caspar', password='acoolpassword')
        
        """ create serializer instance """
        self.serializer = UserSerializer(instance=self.user)
        self.serializer_keys = ['id', 'username']
    
    def test_user_is_created(self):
        """ assert setup user was added """
        self.assertEqual(User.objects.count(), 1)

        """ create new user """
        User.objects.create(
            username="Zanzibar", password='anothercoolpassword')

        """ assert count has changed """
        self.assertEqual(User.objects.count(), 2)
    
    def test_username_matches(self):
        user = self.user
        self.assertEqual(
            user.get_username(), 'Caspar')
    
    def test_hash_id_exists(self):
        user = self.user
        self.assertIsInstance(
          user.hash_id, str)

    def test_serializer_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(), self.serializer_keys)

    def test_serializer_returns_correct_username(self):
        data = self.serializer.data
        self.assertEqual(
            data['username'], self.user.get_username())

    def test_serializer_returns_a_hash(self):
        data = self.serializer.data
        self.assertIsInstance(
          data['id'], str)
