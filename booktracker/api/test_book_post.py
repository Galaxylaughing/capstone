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


class PostBookTest(APITestCase):
    """ Test module for posting a book to the database """

    def setUp(self):
        # create a user
        username = 'Bertie'
        password = 'password'
        self.user = User.objects.create(
            username=username, password=password)
        # get the user's token
        self.token = str(self.user.auth_token)

    def test_can_add_a_valid_book(self):
        # make some post parameters
        title = 'New Book With Unique Title'
        data = {
            "title": title,
            "authors": ["New Author", "Other Author"]
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('books')
        # make request
        response = self.client.post(url, data, format='json')

        # find book in database
        newBook = Book.objects.get(title=title)
        # grab id
        newBookId = newBook.id
        # determine expected data
        expected_data = {
            'books': [{
                'id': newBookId,
                'title': title,
                'authors': [
                    'Other Author',
                    'New Author'
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)

    def test_cannot_add_a_book_without_authentication(self):
        # make some post parameters
        title = 'New Book With Unique Title'
        data = {
            "title": title,
            "authors": ["New Author", "Other Author"]
        }

        # DON'T request header
        # get url
        url = reverse('books')
        # make request
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_cannot_add_invalid_book(self):
        # make some invalid post parameters
        title = 'New Book With Unique Title'
        data = {
            "authors": ["New Author", "Other Author"]
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('books')
        # make request
        response = self.client.post(url, data, format='json')

        expected_error = {
            "error": "Invalid book parameters"
        }
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)
