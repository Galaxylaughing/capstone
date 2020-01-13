from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book, BookAuthor, Series
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
        tag_one = "new"
        tag_two = "very-unique"
        data = {
            "title": title,
            "authors": ["New Author", "Other Author"],
            "tags": [tag_one, tag_two]
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
                ],
                'position_in_series': None,
                'series': None,
                'publisher': None,
                'publication_date': None,
                'isbn_10': None,
                'isbn_13': None,
                'page_count': None,
                'description': None,
                'tags': [tag_two, tag_one]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)

    def test_can_add_a_valid_book_with_series(self):
        # make a new seires
        series_name = "Cool Series"
        planned_count = 3
        series = Series.objects.create(
            name=series_name, planned_count=planned_count, user=self.user)
        series_id = series.id

        # make some post parameters
        title = 'New Book With Very Unique Title'
        data = {
            "title": title,
            "authors": ["New Author"],
            "position_in_series": 2,
            "series": series_id
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
                    'New Author'
                ],
                'position_in_series': 2,
                'series': series_id,
                'publisher': None,
                'publication_date': None,
                'isbn_10': None,
                'isbn_13': None,
                'page_count': None,
                'description': None,
                'tags': []
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

        # DON'T add token to request header
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

    @skip("Not sure this is worth it, considering possible real life edge cases")
    def test_cannot_add_duplicate_title_author_combinations(self):
        title = 'A Generic Book Title'
        author_name = "Author"

        existing_book = Book.objects.create(
            title=title, user=self.user)
        existing_author = BookAuthor.objects.create(
            author_name=author_name, user=self.user, book=existing_book)

        # post parameters
        data = {
            "title": title,
            "authors": [author_name]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('books')
        response = self.client.post(url, data, format='json')

        expected_error = {
            "error": "Book with provided title and author(s) already exists"
        }
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_can_add_a_valid_book_with_publisher_and_publication_date(self):
        # make some post parameters
        title = 'New Book With Very Unique Title'
        publisher = "Tor"
        publication_date = "2019-10-10"
        data = {
            "title": title,
            "authors": ["New Author"],
            "publisher": publisher,
            "publication_date": publication_date,
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
                    'New Author'
                ],
                'position_in_series': None,
                'series': None,
                'publisher': publisher,
                'publication_date': publication_date,
                'isbn_10': None,
                'isbn_13': None,
                'page_count': None,
                'description': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)

    def test_can_add_a_valid_book_with_isbns(self):
        # make some post parameters
        title = 'New Book With Very Unique Title'
        isbn10 = "8175257660"
        isbn13 = "9788175257665"
        data = {
            "title": title,
            "authors": ["New Author"],
            "isbn_10": isbn10,
            "isbn_13": isbn13,
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
                    'New Author'
                ],
                'position_in_series': None,
                'series': None,
                'publisher': None,
                'publication_date': None,
                'isbn_10': isbn10,
                'isbn_13': isbn13,
                'page_count': None,
                'description': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)

    def test_can_add_a_valid_book_with_pagecount_and_description(self):
        # make some post parameters
        title = 'New Book With Very Unique Title'
        page_count = 717
        description = """Warbreaker is the story of two sisters, 
        who happen to be princesses, the God King one of them has to marry, 
        the lesser god who doesn&#39;t like his job, and the immortal who&#39;s 
        still trying to undo the mistakes he made hundreds of years ago."""
        data = {
            "title": title,
            "authors": ["New Author"],
            "page_count": page_count,
            "description": description,
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
                    'New Author'
                ],
                'position_in_series': None,
                'series': None,
                'publisher': None,
                'publication_date': None,
                'isbn_10': None,
                'isbn_13': None,
                'page_count': page_count,
                'description': description,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)