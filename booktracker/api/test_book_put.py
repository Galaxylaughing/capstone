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


class UpdateBookTests(APITestCase):
    """ test module for updating a book """

    def setUp(self):
        # create a user
        username = 'Bertie'
        password = 'password'
        self.user = User.objects.create(
            username=username, password=password)
        # get the user's token
        self.token = str(self.user.auth_token)
        # give the user a book
        self.title = "First Book"
        self.first_book = Book.objects.create(
            title=self.title, user=self.user)
        self.book_id = self.first_book.id
        # give the book two authors
        self.author_one = "Jane Doe"
        BookAuthor.objects.create(
            author_name=self.author_one, book=self.first_book)
        self.author_two = "John Doe"
        BookAuthor.objects.create(
            author_name=self.author_two, book=self.first_book)

    def test_can_update_with_all_fields_changed(self):
        """ if given all fields, and all are new, can update book """
        # make the parameters
        new_title = 'New Book With Unique Title'
        data = {
            "title": new_title,
            "authors": ["New Author", "Other Author"]
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': new_title,
                'authors': [
                    'Other Author',
                    'New Author'
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, new_title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue("New Author" in author_values)
        self.assertTrue("Other Author" in author_values)

    def test_can_update_with_only_some_fields_changed(self):
        """ if given all fields, but only some are new, can update book """
        # make the parameters
        new_title = 'New Book With Unique Title'
        author_one = self.author_one
        author_two = self.author_two
        data = {
            "title": new_title,
            "authors": [author_one, author_two]
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': new_title,
                'authors': [
                    author_two,
                    author_one
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, new_title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(author_one in author_values)
        self.assertTrue(author_two in author_values)

    def test_can_update_with_only_new_authors_provided(self):
        """ if given only the author field, and it is new, can update book """
        # make the parameters
        # not changing title
        author_one = self.author_one
        author_two = self.author_two
        data = {
            "authors": [author_one, author_two]
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': self.title,
                'authors': [
                    author_two,
                    author_one
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, self.title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(author_one in author_values)
        self.assertTrue(author_two in author_values)

    def test_can_update_with_only_new_title_provided(self):
        """ if given only the title field, and it is new, can update book """
        # make the parameters
        new_title = 'New Book With Unique Title'
        data = {
            "title": new_title
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        author_one = self.author_one
        author_two = self.author_two
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': new_title,
                'authors': [
                    author_two,
                    author_one
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, new_title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(author_one in author_values)
        self.assertTrue(author_two in author_values)
