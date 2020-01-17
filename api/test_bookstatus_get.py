from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from django.utils import timezone
import datetime
import pytz

from .models import Book, BookStatus
from .serializers import BookStatusSerializer

from django.apps import apps
User = apps.get_model('userauth','User')

class GetBookStatusTest(APITestCase):
    # given a book id, should return all of the bookstatus rows associated with that book

    def setUp(self):
        username = 'Bertie'
        password = 'password'
        self.user = User.objects.create(
            username=username, password=password)
        self.token = str(self.user.auth_token)
        self.book = Book.objects.create(
            title="Get Status by Book Test", user=self.user)

    def test_can_get_bookstatuses_for_existing_book(self):
        date_one = pytz.utc.localize(datetime.datetime(2011, 1, 1))
        status_one = BookStatus.objects.create(
            status_code=Book.WANTTOREAD, 
            book=self.book, 
            user=self.user, 
            date=date_one
        )
        date_two = pytz.utc.localize(datetime.datetime(2011, 1, 2))
        status_two = BookStatus.objects.create(
            status_code=Book.CURRENT, 
            book=self.book, 
            user=self.user, 
            date=date_two
        )

        expected_data = {
            'status_history': [
                {
                    "id": status_one.id,
                    "status_code": status_one.status_code,
                    "book": self.book.id,
                    "date": date_one.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                {
                    "id": status_two.id,
                    "status_code": status_two.status_code,
                    "book": self.book.id,
                    "date": date_two.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookstatus', kwargs={'book_id': self.book.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_for_nonexisting_book(self):
        fake_id = 999

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookstatus', kwargs={'book_id': fake_id})
        response = self.client.get(url, format='json')

        expected_data = {
            "error": "Could not find book with ID: %s" %(fake_id)
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_for_a_book_that_is_not_the_users(self):
        other_user = User.objects.create(
            username="other user", password="password")
        other_book = Book.objects.create(
            title="Get Status by User's Book Test", user=other_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookstatus', kwargs={'book_id': other_book.id})
        response = self.client.get(url, format='json')

        expected_data = {
            "error": "Could not find book with ID: %s" %(other_book.id)
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)
