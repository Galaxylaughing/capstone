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


class GetSeriesTest(APITestCase):
    """ Test module for getting a list of a User's series """

    def setUp(self):
        # create a user
        self.user = User.objects.create(
            username="GetSeriesUser", password="password")
        # get the user's token
        self.token = str(self.user.auth_token)

    def test_can_access_a_users_series(self):
        # create a series
        series_name = "Great Series"
        planned_count = 3
        series = Series.objects.create(
            name=series_name, planned_count=planned_count, user=self.user)
        book_one = Book.objects.create(
            title="Book One", user=self.user, series=series)
        book_one_id = book_one.id
        book_two = Book.objects.create(
            title="Book Two", user=self.user, series=series)
        book_two_id = book_two.id
        
        series_id = series.id
        expected_data = {
            'series': [
                {
                    'id': series_id,
                    'name': series_name,
                    'planned_count': planned_count,
                    'books': [book_two_id, book_one_id]
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('series_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['series'][0]['id'], expected_data['series'][0]['id'])
        self.assertEqual(response.data['series'][0]['name'], expected_data['series'][0]['name'])
        self.assertEqual(response.data['series'][0]['planned_count'], expected_data['series'][0]['planned_count'])
        self.assertEqual(response.data['series'][0]['books'], expected_data['series'][0]['books'])

    def test_can_access_a_specific_users_series(self):
        # create a series
        series_name = "Great Series"
        planned_count = 3
        series = Series.objects.create(
            name=series_name, planned_count=planned_count, user=self.user)

        # create a second user and series
        other_user = User.objects.create(
            username="Other Series User", password="password")
        other_user_token = str(other_user.auth_token)
        other_series_name = series_name
        other_planned_count = 5
        other_series = Series.objects.create(
            name=other_series_name, planned_count=other_planned_count, user=other_user)
        book_one = Book.objects.create(
            title="Book One", user=other_user, series=other_series)
        book_one_id = book_one.id
        
        other_series_id = other_series.id
        expected_data = {
            'series': [
                {
                    'id': other_series_id,
                    'name': other_series_name,
                    'planned_count': other_planned_count,
                    'books': [book_one_id]
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + other_user_token)
        url = reverse('series_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['series'][0]['id'], expected_data['series'][0]['id'])
        self.assertEqual(response.data['series'][0]['name'], expected_data['series'][0]['name'])
        self.assertEqual(response.data['series'][0]['planned_count'], expected_data['series'][0]['planned_count'])
        self.assertEqual(response.data['series'][0]['books'], expected_data['series'][0]['books'])

        filteredSeries = Series.objects.filter(
            id=other_series.id)
        self.assertTrue(filteredSeries.exists())
        self.assertEqual(filteredSeries[0].planned_count, other_planned_count)

    def test_returns_empty_list_if_no_series(self):
        expected_data = {'series': []}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('series_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
