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


class GetBooksTest(APITestCase):
    """ Test module for getting a list of a User's books """

    def setUp(self):
        # create a user
        username = 'Bertie'
        password = 'password'
        self.user = User.objects.create(
            username=username, password=password)
        # get the user's token
        self.token = str(self.user.auth_token)

    def test_can_access_a_users_books(self):
        # give the user some books
        firstBook = Book.objects.create(
            title="First Book", user=self.user)
        secondBook = Book.objects.create(
            title="Second Book", user=self.user)

        # give the books some authors
        BookAuthor.objects.create(
            author_name="John Doe", user=self.user, book=firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", user=self.user, book=firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", user=self.user, book=secondBook)

        firstId = firstBook.id
        secondId = secondBook.id
        expected_data = {
            'books': [
                {
                    'id': secondId,
                    'title': 'Second Book',
                    'authors': [
                        'Jane Doe'
                    ],
                    'position_in_series': None,
                    'series': None,
                    'tags': []
                },
                {
                    'id': firstId,
                    'title': 'First Book',
                    'authors': [
                        'Jane Doe', 
                        'John Doe'
                    ],
                    'position_in_series': None,
                    'series': None,
                    'tags': []
                }
            ]
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_returns_empty_list_if_no_books(self):
        expected_data = {"books": []}

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
        
    def test_returns_error_if_unauthorized(self):
        # DON'T add token to header
        # get the API response
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_access_a_specific_users_books(self):
        # create a new user
        newUser = User.objects.create(
            username='Caspar', password='password')
        # get the user's token
        newUserToken = str(newUser.auth_token)

        # give the new user a book
        firstBook = Book.objects.create(
            title="First Book", user=newUser)
        BookAuthor.objects.create(
            author_name="Jane Doe", user=newUser, book=firstBook)

        # give the setup user a book
        secondBook = Book.objects.create(
            title="Second Book", user=self.user)
        BookAuthor.objects.create(
            author_name="John Doe", user=self.user, book=secondBook)

        firstId = firstBook.id
        expected_data = {
            "books": [
                {
                    'id': firstId,
                    'title': 'First Book',
                    'authors': [
                        'Jane Doe'
                    ],
                    'position_in_series': None,
                    'series': None,
                    'tags': []
                }
            ]
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + newUserToken)
        # get the API response
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
