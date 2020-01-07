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


class DeleteSeriesTest(APITestCase):
    """ Test module for deleting a series """

    def setUp(self):
        # create a user
        self.user = User.objects.create(
            username="GetSeriesUser", password="password")
        # get the user's token
        self.token = str(self.user.auth_token)
        # make initial series
        self.series = Series.objects.create(
            name='Series To Get Deleted', planned_count=0, user=self.user)

    def test_can_delete_a_series(self):
        expected_data = {
            'series': {
                'id': self.series.id,
                'name': self.series.name,
                'planned_count': self.series.planned_count,
                'books': []
            }
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('series_details', kwargs={'series_id': self.series.id})
        # make request
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        filtered_series = Series.objects.filter(id=self.series.id)
        self.assertEqual(filtered_series.count(), 0)

    def test_returns_an_error_if_nonexistant_series(self):
        fake_id = 999
        expected_data = {
            "error": "Could not find series with ID: %s" %(fake_id)
        }
        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('series_details', kwargs={'series_id': fake_id})
        # make request
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_user_cannot_delete_other_users_series(self):
        new_user = User.objects.create(
            username="I can only delete my own series", password="password")
        new_series = Series.objects.create(
            name=self.series.name, planned_count=7, user=new_user)

        expected_data = {
            "error": "Users can only delete their own series; series %s belongs to user %s" %(new_series.id, new_user.id)
        }
        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token) # using setup user's token
        # get url
        url = reverse('series_details', kwargs={'series_id': new_series.id})
        # make request
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_user_can_delete_a_series_with_book(self):
        book_one = Book.objects.create(
            title="First Book of a Not-So-Beloved Series", user=self.user, series=self.series)

        expected_data = {
            'series': {
                'id': self.series.id,
                'name': self.series.name,
                'planned_count': self.series.planned_count,
                'books': [book_one.id]
            }
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('series_details', kwargs={'series_id': self.series.id})
        # make request
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        filtered_series = Series.objects.filter(id=self.series.id)
        self.assertEqual(filtered_series.count(), 0)
