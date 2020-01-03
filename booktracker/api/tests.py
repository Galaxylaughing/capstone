from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip


# Create your tests here.
from .models import Book
from .models import BookAuthor

from django.apps import apps
User = apps.get_model('userauth','User')


class BookTest(TestCase):
    """ Test module for the Book model """

    def setUp(self):
        self.user = User.objects.create(
            username="Fakey", password="password")

    def test_book_can_be_created(self):
        expectedCount = Book.objects.count() + 1
        
        Book.objects.create(
            title="Test Book", user=self.user)
        filteredBooks = Book.objects.filter(title="Test Book")

        self.assertEqual(Book.objects.count(), expectedCount)
        # exists() returns True if the QuerySet contains any results
        self.assertTrue(filteredBooks.exists())

    def test_book_str_method(self):
        book_title = "A Good Book"

        book = Book.objects.create(
            title=book_title, user=self.user)
        
        self.assertEqual(str(book), book_title)


class BookAuthorTests(TestCase):
    """ Test module for the BookAuthor model """

    def setUp(self):
        # make the User a Book relies on
        self.user = User.objects.create(
            username="Fakey", password="password")
        # make the Book a BookAuthor relies on
        self.book = Book.objects.create(
            title="Test Book", user=self.user)

    def test_bookauthor_can_be_created(self):
        expectedCount = BookAuthor.objects.count() + 1

        BookAuthor.objects.create(
            author_name="First Last", book=self.book)
        filteredBookAuthors = BookAuthor.objects.filter(
            author_name="First Last")

        self.assertEqual(BookAuthor.objects.count(), expectedCount)
        self.assertTrue(filteredBookAuthors.exists())

    def test_bookauthor_str_method(self):
        author_name = "M.K. Author"

        book_author = BookAuthor.objects.create(
            author_name=author_name, book=self.book)
        
        self.assertEqual(str(book_author), author_name)


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

    @skip("skip")
    def test_can_access_a_users_books(self):
        # give the user some books
        Book.objects.create(
            title="First Book", user=self.user)
        Book.objects.create(
            title="Second Book", user=self.user)

        print(self.token)

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('get_books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    # endpoint should require a user's token
    # endpoint should look up user by token
    # endpoint should return an array of objects representing books
    # and the status code 200 OK
    # the book data should be the title and the author name

    # if the user has no books,
    # return an empty array
    # and the status code 200 OK

    # if a token is not recieved, 
    # or the recieved token doesn't match a user
    # return an error, 401 unauthorized
