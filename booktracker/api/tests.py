from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip


# Create your tests here.
from .models import Book, BookAuthor
from .serializers import BookSerializer, BookAuthorSerializer

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


class SerializerTests(TestCase):
    """ test module for BookSerializer """

    def setUp(self):
        self.user = User.objects.create(
            username='Bertie', password='password')

        self.firstBook = Book.objects.create(
            title="First Book", user=self.user)
        self.secondBook = Book.objects.create(
            title="Second Book", user=self.user)

        BookAuthor.objects.create(
            author_name="John Doe", book=self.firstBook)
        BookAuthor.objects.create(
            author_name='Jane Doe', book=self.firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", book=self.secondBook)

    def test_bookserializer_returns_expected_data(self):
        firstId = self.firstBook.id
        secondId = self.secondBook.id
        expected_data = [
            {
                'id': firstId,
                'title': 'First Book',
                'authors': [
                    'Jane Doe',
                    'John Doe'
                ]
            }, 
            {
                'id': secondId,
                'title': 'Second Book',
                'authors': [
                    'Jane Doe'
                ]
            }
        ]

        bookList = Book.objects.all()
        serializer = BookSerializer(bookList, many=True)

        self.assertEqual(serializer.data, expected_data)

    def test_bookauthorserializer_returns_expected_data(self):
        expected_data = [
            { 
                'author_name': 'John Doe',
                'book': 'First Book'
            },
            {
                'author_name': 'Jane Doe',
                'book': 'First Book'
            },
            { 
                'author_name': 'Jane Doe',
                'book': 'Second Book'
            }
        ]

        bookauthorList = BookAuthor.objects.all()
        serializer = BookAuthorSerializer(bookauthorList, many=True)

        self.assertEqual(serializer.data, expected_data)


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
            author_name="John Doe", book=firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", book=firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", book=secondBook)

        firstId = firstBook.id
        secondId = secondBook.id
        expected_data = {
            'books': [
                {
                    'id': secondId,
                    'title': 'Second Book',
                    'authors': [
                        'Jane Doe'
                    ]
                },
                {
                    'id': firstId,
                    'title': 'First Book',
                    'authors': [
                        'Jane Doe', 
                        'John Doe'
                    ]
                }
            ]
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('get_books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    @skip("TODO: unskip me again when XCode hand-testing done")
    def test_returns_empty_list_if_no_books(self):
        expected_data = {"books": []}

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('get_books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
        
    def test_returns_error_if_unauthorized(self):
        # DON'T add token to header
        # get the API response
        url = reverse('get_books')
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
            author_name="Jane Doe", book=firstBook)

        # give the setup user a book
        secondBook = Book.objects.create(
            title="Second Book", user=self.user)
        BookAuthor.objects.create(
            author_name="John Doe", book=secondBook)

        firstId = firstBook.id
        expected_data = {
            "books": [
                {
                    'id': firstId,
                    'title': 'First Book',
                    'authors': [
                        'Jane Doe'
                    ]
                }
            ]
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + newUserToken)
        # get the API response
        url = reverse('get_books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
