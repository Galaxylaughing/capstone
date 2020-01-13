from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book, BookAuthor
from .serializers import BookSerializer, BookAuthorSerializer

from django.apps import apps
User = apps.get_model('userauth','User')


class GetBookDetailsTest(APITestCase):
    """ Test module for getting the details of a specific book """

    def setUp(self):
        # create a user
        username = 'Bertie'
        password = 'password'
        self.user = User.objects.create(
            username=username, password=password)
        # get the user's token
        self.token = str(self.user.auth_token)

    def test_can_get_details_for_existing_book(self):
        # give the user a book
        publisher = "Tor"
        publication_date = "2010-10-10"
        isbn_10 = "8175257660"
        isbn_13 = "9788175257665"
        page_count = 717
        description = """Warbreaker is the story of two sisters, 
        who happen to be princesses, the God King one of them has to marry, 
        the lesser god who doesn&#39;t like his job, and the immortal who&#39;s 
        still trying to undo the mistakes he made hundreds of years ago."""

        firstBook = Book.objects.create(
            title="First Book", 
            user=self.user,
            publisher=publisher,
            publication_date=publication_date,
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            page_count=page_count,
            description=description)

        # give the book an author
        BookAuthor.objects.create(
            author_name="Jane Doe", user=self.user, book=firstBook)

        firstId = firstBook.id
        expected_data = {
            'book': {
                'id': firstId,
                'title': 'First Book',
                'authors': [
                    'Jane Doe'
                ],
                'position_in_series': None,
                'series': None,
                'publisher': publisher,
                'publication_date': publication_date,
                'isbn_10': isbn_10,
                'isbn_13': isbn_13,
                'page_count': page_count,
                'description': description,
                'tags': []
            }
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': firstId})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_cannot_get_details_for_another_users_book(self):
        new_user = User.objects.create(
            username="New User", password="password")
        new_book = Book.objects.create(
            title="New User's Book", user=new_user)

        expected_data = {
            "error": "unauthorized"
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': new_book.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_no_book_found(self):
        fakeId = 999
        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': fakeId})
        response = self.client.get(url, format='json')

        error_message = "No book found with the ID: %s" %(fakeId)
        expected_data = {
            'error': error_message
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)
        
    def test_returns_error_if_unauthorized(self):
        # give the user a book
        firstBook = Book.objects.create(
            title="First Book", user=self.user)
        # give the book an author
        BookAuthor.objects.create(
            author_name="Jane Doe", user=self.user, book=firstBook)

        firstId = firstBook.id
        
        # DON'T add token to header
        # get the API response
        url = reverse('book', kwargs={'book_id': firstId})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
