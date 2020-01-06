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
        self.firstBook = Book.objects.create(
            title=self.title, user=self.user)
        self.book_id = self.firstBook.id
        # give the book two authors
        self.authorOne = "Jane Doe"
        BookAuthor.objects.create(
            author_name=self.authorOne, book=self.firstBook)
        self.authorTwo = "John Doe"
        BookAuthor.objects.create(
            author_name=self.authorTwo, book=self.firstBook)

    def test_can_update_with_all_fields_changed(self):
        """ if given all fields, and all are new, can update book """

        # make the parameters
        newTitle = 'New Book With Unique Title'
        data = f'title={newTitle}&author=New Author&author=Other Author'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, content_type='application/x-www-form-urlencoded')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': newTitle,
                'authors': [
                    'Other Author',
                    'New Author'
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updatedBook = Book.objects.get(id=self.book_id)
        self.assertEqual(updatedBook.title, newTitle)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updatedBook)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue("New Author" in author_values)
        self.assertTrue("Other Author" in author_values)

    def test_can_update_with_only_some_fields_changed(self):
        """ if given all fields, but only some are new, can update book """

        # make the parameters
        newTitle = 'New Book With Unique Title'
        authorOne = self.authorOne
        authorTwo = self.authorTwo
        data = f'title={newTitle}&author={authorOne}&author={authorTwo}'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, content_type='application/x-www-form-urlencoded')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': newTitle,
                'authors': [
                    authorTwo,
                    authorOne
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updatedBook = Book.objects.get(id=self.book_id)
        self.assertEqual(updatedBook.title, newTitle)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updatedBook)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(authorOne in author_values)
        self.assertTrue(authorTwo in author_values)

    def test_can_update_with_only_new_authors_provided(self):
        """ if given only the author field, and it is new, can update book """

        # make the parameters
        # not changing title
        authorOne = self.authorOne
        authorTwo = self.authorTwo
        data = f'author={authorOne}&author={authorTwo}'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, content_type='application/x-www-form-urlencoded')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': self.title,
                'authors': [
                    authorTwo,
                    authorOne
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updatedBook = Book.objects.get(id=self.book_id)
        self.assertEqual(updatedBook.title, self.title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updatedBook)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(authorOne in author_values)
        self.assertTrue(authorTwo in author_values)

    def test_can_update_with_only_new_title_provided(self):
        """ if given only the title field, and it is new, can update book """

        # make the parameters
        newTitle = 'New Book With Unique Title'
        data = f'title={newTitle}'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, content_type='application/x-www-form-urlencoded')

        # determine expected data
        authorOne = self.authorOne
        authorTwo = self.authorTwo
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': newTitle,
                'authors': [
                    authorTwo,
                    authorOne
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updatedBook = Book.objects.get(id=self.book_id)
        self.assertEqual(updatedBook.title, newTitle)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updatedBook)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(authorOne in author_values)
        self.assertTrue(authorTwo in author_values)
