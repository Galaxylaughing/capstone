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


class DeleteBookTests(APITestCase):
    """ test module for deleting a book """

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
        # give the book an author
        self.author = "Jane Doe"
        BookAuthor.objects.create(
            author_name=self.author, user=self.user, book=self.firstBook)

    def test_can_delete_a_book(self):
        firstId = self.firstBook.id
        firstTitle = self.title
        firstAuthor = self.author
        expected_data = {
            'book': {
                'id': firstId,
                'title': firstTitle,
                'authors': [
                    firstAuthor
                ],
                'position_in_series': None,
                'series': None,
                'publisher': None,
                'publication_date': None,
                'isbn_10': None,
                'isbn_13': None,
                'tags': []
            }
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': firstId})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # check that I can't find it in database
        filteredBooks = Book.objects.filter(id=firstId)
        self.assertEqual(filteredBooks.count(), 0)

    def test_returns_error_if_invalid_bookid(self):
        fakeId = 999
        expected_data = {
            "error": "Could not find book with ID: %s" %(fakeId)
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': fakeId})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_deletion_of_an_authors_only_book_deletes_author(self):
        # create new book
        title = "Unique Book"
        uniqueBook = Book.objects.create(
            title=title, user=self.user)
        uniqueBookId = uniqueBook.id
        # give the book an author
        uniqueAuthor = "Unique Author"
        uniqueBookAuthor = BookAuthor.objects.create(
            author_name=uniqueAuthor, user=self.user, book=uniqueBook)
        uniqueAuthorId = uniqueBookAuthor.id

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': uniqueBookId})
        response = self.client.delete(url, format='json')

        # check that I can't find the book in database
        filteredBooks = Book.objects.filter(id=uniqueBookId)
        self.assertEqual(filteredBooks.count(), 0)

        # check that I can't find the author in database
        filteredAuthors = BookAuthor.objects.filter(id=uniqueAuthorId)
        self.assertEqual(filteredAuthors.count(), 0)

    def test_user_cannot_delete_other_users_book(self):
        newUser = User.objects.create(
        username="New User", password="password")
        # give the user a book
        otherBook = Book.objects.create(
            title="Other User's Book", user=newUser)

        otherId = otherBook.id
        expected_data = {
            "error": "Users can only delete their own books; book %s belongs to user %s" %(otherId, newUser.id)
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': otherId})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)
