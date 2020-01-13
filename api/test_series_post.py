from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book, BookAuthor, Series
from .serializers import BookSerializer, BookAuthorSerializer

from django.apps import apps
User = apps.get_model('userauth','User')


class PostSeriesTest(APITestCase):
    """ Test module for adding a series """

    def setUp(self):
        # create a user
        self.user = User.objects.create(
            username="GetSeriesUser", password="password")
        # get the user's token
        self.token = str(self.user.auth_token)

    def test_can_create_a_valid_series(self):
        # make post parameters
        series_name = 'Warrior Cats: The Prophecies Begin'
        series_count = 6
        data = {
            'name': series_name,
            'planned_count': series_count
        }
        # request
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('series_list')
        response = self.client.post(url, data, format='json')

        # check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check for new series
        new_series = Series.objects.get(name=series_name)
        new_series_id = new_series.id
        expected_data = {
            'series': [{
                'id': new_series_id,
                'name': series_name,
                'planned_count': series_count,
                'books': []
            }]
        }
        self.assertEqual(response.data, expected_data)

    def test_cannot_add_a_series_without_authentication(self):
        # make post parameters
        series_name = 'Warrior Cats: The Prophecies Begin'
        series_count = 6
        data = {
            'name': series_name,
            'planned_count': series_count
        }
        # request
        # DON'T add token to request header
        url = reverse('series_list')
        response = self.client.post(url, data, format='json')

        # check status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_add_invalid_series(self):
        # make post parameters
        series_count = 6
        data = {
            'planned_count': series_count
        }
        # request
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('series_list')
        response = self.client.post(url, data, format='json')

        # check status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_data = {
            "error": "Invalid series parameters"
        }
        self.assertEqual(response.data, expected_data)
