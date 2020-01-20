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

class DeleteBookStatusTest(APITestCase):
    # given a bookstatus id, should delete that bookstatus row

    def setUp(self):
        self.user = User.objects.create(
            username='Bertie', password='password')
        self.token = str(self.user.auth_token)
        self.book = Book.objects.create(
            title="Delete Status Test", user=self.user)

    def test_can_delete_a_bookstatus_by_id(self):
        date_one = pytz.utc.localize(datetime.datetime(2011, 1, 1))
        bookstatus = BookStatus.objects.create(
            status_code=Book.DISCARDED, 
            book=self.book, 
            user=self.user, 
            date=date_one
        )

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookstatus', kwargs={"id": bookstatus.id})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"]["id"], bookstatus.id)
        self.assertEqual(response.data["status"]["status_code"], bookstatus.status_code)
        self.assertEqual(response.data["status"]["book"], self.book.id)
        self.assertEqual(response.data["status"]["date"], date_one.strftime("%Y-%m-%dT%H:%M:%SZ"))

        deleted_status = BookStatus.objects.filter(id=bookstatus.id)
        self.assertFalse(deleted_status.exists())

    def test_deleting_a_bookstatus_updates_book(self):
        new_book = Book.objects.create(
            title="Delete Status Updates Book Test", 
            user=self.user
        )
        date_one = pytz.utc.localize(datetime.datetime(2011, 1, 1))
        bookstatus_one = BookStatus.objects.create(
            status_code=Book.CURRENT, 
            book=new_book, 
            user=self.user, 
            date=date_one
        )
        date_two = pytz.utc.localize(datetime.datetime(2012, 1, 1))
        bookstatus_two = BookStatus.objects.create(
            status_code=Book.DISCARDED, 
            book=new_book, 
            user=self.user, 
            date=date_two
        )

        new_book.current_status = bookstatus_two.status_code
        new_book.current_status_date = date_two
        new_book.save()

        matching_book_before = Book.objects.get(id=new_book.id)
        self.assertEqual(matching_book_before.current_status, bookstatus_two.status_code)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookstatus', kwargs={"id": bookstatus_two.id})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "status": {
                "id": bookstatus_two.id,
                "status_code": bookstatus_two.status_code,
                "book": new_book.id,
                "date": date_two.strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "current_status": bookstatus_one.status_code,
            "current_status_date": date_one
        }
        self.assertEqual(response.data, expected_data)
        
        matching_book_after = Book.objects.get(id=new_book.id)
        self.assertEqual(matching_book_after.current_status, bookstatus_one.status_code)

    def test_deleting_a_bookstatus_updates_book_2(self):
        new_book = Book.objects.create(
            title="Delete Status Updates Book Test", 
            user=self.user
        )
        date_one = pytz.utc.localize(datetime.datetime(2011, 1, 1))
        bookstatus_one = BookStatus.objects.create(
            status_code=Book.CURRENT, 
            book=new_book, 
            user=self.user, 
            date=date_one
        )
        date_two = pytz.utc.localize(datetime.datetime(2012, 1, 1))
        bookstatus_two = BookStatus.objects.create(
            status_code=Book.DISCARDED, 
            book=new_book, 
            user=self.user, 
            date=date_two
        )

        new_book.current_status = bookstatus_one.status_code
        new_book.current_status_date = date_one
        new_book.save()

        matching_book_before = Book.objects.get(id=new_book.id)
        self.assertEqual(matching_book_before.current_status, bookstatus_one.status_code)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookstatus', kwargs={"id": bookstatus_one.id})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "status": {
                "id": bookstatus_one.id,
                "status_code": bookstatus_one.status_code,
                "book": new_book.id,
                "date": date_one.strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "current_status": bookstatus_two.status_code,
            "current_status_date": date_two
        }
        self.assertEqual(response.data, expected_data)
        
        matching_book_after = Book.objects.get(id=new_book.id)
        self.assertEqual(matching_book_after.current_status, bookstatus_two.status_code)

    def test_user_can_only_delete_their_own_statuses(self):
        date_one = pytz.utc.localize(datetime.datetime(2011, 1, 1))
        bookstatus = BookStatus.objects.create(
            status_code=Book.DISCARDED, 
            book=self.book, 
            user=self.user, 
            date=date_one
        )

        other_user = User.objects.create(
            username="Status Delete Test Other User", password="password")
        other_book = Book.objects.create(
            title="Status Delete Test Other Book", user=other_user)
        other_status = BookStatus.objects.create(
            status_code=Book.CURRENT,
            user=other_user,
            book=other_book,
            date=date_one)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookstatus', kwargs={"id": other_status.id})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error = {
            "error": "Could not find status with ID: %s" %(other_status.id)
        }
        self.assertEqual(response.data, expected_error)

    def test_returns_error_if_no_status_found(self):
        fake_status_id = 999

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookstatus', kwargs={"id": fake_status_id})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error = {
            "error": "Could not find status with ID: %s" %(fake_status_id)
        }
        self.assertEqual(response.data, expected_error)
