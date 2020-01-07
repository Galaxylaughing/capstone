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


class PutSeriesTest(APITestCase):
    """ Test module for updating a series """

    def setUp(self):
        # create a user
        self.user = User.objects.create(
            username="GetSeriesUser", password="password")
        # get the user's token
        self.token = str(self.user.auth_token)
        # make initial series
        self.series = Series.objects.create(
            name='Warrior Cats', planned_count=0, user=self.user)

    def test_can_update_with_all_fields_changed(self):
        # make put parameters
        series_name = 'Warrior Cats: The Prophecies Begin'
        series_count = 6
        data = {
            'name': series_name,
            'planned_count': series_count
        }
        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('series_details', kwargs={'series_id': self.series.id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'series': [{
                'id': self.series.id,
                'name': series_name,
                'planned_count': series_count,
                'books': []
            }]
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find series in database
        updated_series = Series.objects.get(id=self.series.id)
        self.assertEqual(updated_series.name, series_name)
        self.assertEqual(updated_series.planned_count, series_count)

    def test_can_update_with_only_some_fields_changed(self):
        # make put parameters
        series_name = 'Warrior Cats: The Prophecies Begin Again'
        data = {
            'name': series_name,
            'planned_count': self.series.planned_count
        }
        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('series_details', kwargs={'series_id': self.series.id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'series': [{
                'id': self.series.id,
                'name': series_name,
                'planned_count': self.series.planned_count,
                'books': []
            }]
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find series in database
        updated_series = Series.objects.get(id=self.series.id)
        self.assertEqual(updated_series.name, series_name)
        self.assertEqual(updated_series.planned_count, self.series.planned_count)

    def test_can_update_with_only_some_fields_provided(self):
        # make put parameters
        series_name = 'Warrior Cats: The Prophecies Begin Again Once More'
        data = {
            'name': series_name,
        }
        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('series_details', kwargs={'series_id': self.series.id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'series': [{
                'id': self.series.id,
                'name': series_name,
                'planned_count': self.series.planned_count,
                'books': []
            }]
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find series in database
        updated_series = Series.objects.get(id=self.series.id)
        self.assertEqual(updated_series.name, series_name)
        self.assertEqual(updated_series.planned_count, self.series.planned_count)

    def test_returns_error_if_series_not_found(self):
        fake_id = 999
        # make put parameters
        series_name = 'Warrior Cats: The Final Countdown'
        data = {
            'name': series_name,
        }
        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('series_details', kwargs={'series_id': fake_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'error': 'Could not find series with ID: %s' %(fake_id)
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

        # find series in database
        unchanged_series = Series.objects.get(id=self.series.id)
        self.assertEqual(unchanged_series.name, self.series.name)
        self.assertEqual(unchanged_series.planned_count, self.series.planned_count)