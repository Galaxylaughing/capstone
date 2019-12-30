from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

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


class LoginUserTest(APITestCase):
    """ Test module for logging in a User """

    def setUp(self):
        """ create a user instance to login """
        self.user = User.objects.create_user(
            username='Caspar', password='acoolpassword')

    def test_logging_in_existing_user_returns_user(self):
        # get API response
        url = reverse('login')
        data = {'username': 'Caspar', 'password': 'acoolpassword'}
        response = self.client.post(url, data, format='json')

        # get data from database
        user = User.objects.get(username='Caspar')
        serializer = UserSerializer(user)

        # assert
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logging_in_new_user_returns_an_unauthorized_error(self):
        """ do other stuff """
