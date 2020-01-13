from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book, BookAuthor, Series, BookTag
from .serializers import BookSerializer, BookAuthorSerializer, SeriesSerializer, BookTagSerializer

from django.apps import apps
User = apps.get_model('userauth','User')

class BookAndBookAuthorSerializerTests(TestCase):
    """ test module for BookSerializer and BookAuthor Serializer """

    def setUp(self):
        self.user = User.objects.create(
            username='SerializerTestUser', password='password')

        self.firstBook = Book.objects.create(
            title="First Book", user=self.user)

        series_name = "Cool Series"
        planned_count = 3
        self.series = Series.objects.create(
            name=series_name, planned_count=planned_count, user=self.user)
        self.secondBook = Book.objects.create(
            title="Second Book", user=self.user, position_in_series=1, series=self.series)

        BookAuthor.objects.create(
            author_name="John Doe", user=self.user, book=self.firstBook)
        BookAuthor.objects.create(
            author_name='Jane Doe', user=self.user, book=self.firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", user=self.user, book=self.secondBook)

    # BOOK SERIALIZER
    def test_bookserializer_returns_expected_data(self):
        firstId = self.firstBook.id
        secondId = self.secondBook.id
        series_id = self.series.id
        expected_data = [
            {
                'id': firstId,
                'title': 'First Book',
                'authors': [
                    'Jane Doe',
                    'John Doe'
                ],
                'position_in_series': None,
                'series': None,
                'publisher': None,
                'publication_date': None,
                'tags': []
            }, 
            {
                'id': secondId,
                'title': 'Second Book',
                'authors': [
                    'Jane Doe'
                ],
                'position_in_series': 1,
                'series': series_id,
                'publisher': None,
                'publication_date': None,
                'tags': []
            }
        ]

        bookList = Book.objects.all()
        serializer = BookSerializer(bookList, many=True)

        self.assertEqual(serializer.data, expected_data)

    def test_serializer_will_return_tags(self):
        user = User.objects.create(
            username='UserToTestTagRelationship', password='password')
        book = Book.objects.create(
            title="Book", user=user)
        tag = BookTag.objects.create(
            tag_name="fiction", user=user, book=book)

        expected_data = {
            'id': book.id,
            'title': book.title,
            'authors': [],
            'position_in_series': None,
            'series': None,
            'publisher': None,
            'publication_date': None,
            'tags': [tag.tag_name]
        }

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data, expected_data)

    # BOOK-AUTHOR SERIALIZER
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

class SeriesSerializerTests(TestCase):

    # SERIES SERIALIZER
    def test_series_serializer_returns_expected_data(self):
        new_user = User.objects.create(
            username='Yet Another New User', password='password')

        first_series = Series.objects.create(
            name="A Series", planned_count=3, user=new_user)
        first_series_book = Book.objects.create(
            title="Book One", user=new_user, series=first_series)
        first_book_id = first_series_book.id

        second_series = Series.objects.create(
            name="Another Series", planned_count=2, user=new_user)

        first_series_id = first_series.id
        first_series_name = first_series.name
        first_series_count = first_series.planned_count
        second_series_id = second_series.id
        second_series_name = second_series.name
        second_series_count = second_series.planned_count
        expected_data = [
            {
                'id': second_series_id,
                'name': second_series_name,
                'planned_count': second_series_count,
                'books': []
            },
            {
                'id': first_series_id,
                'name': first_series_name,
                'planned_count': first_series_count,
                'books': [first_book_id]
            }
        ]

        seriesList = Series.objects.filter(user=new_user)
        serializer = SeriesSerializer(seriesList, many=True)

        self.assertEqual(serializer.data, expected_data)

class BookTagSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="Book Tag Serializer User", password="password")
        self.token = str(self.user.auth_token)

    # BOOKTAG SERIALIZER
    def test_booktag_serializer_returns_expected_data(self):
        tag_name_one = "non-fiction"
        book_one = Book.objects.create(
            title="Tag Serializer Test Book One", user=self.user)
        new_tag = BookTag.objects.create(
            tag_name=tag_name_one, user=self.user, book=book_one)

        tag_name_two = "fiction"
        book_two = Book.objects.create(
            title="Tag Serializer Test Book Two", user=self.user)
        new_tag = BookTag.objects.create(
            tag_name=tag_name_two, user=self.user, book=book_two)

        expected_data = [
            {
                "tag_name": tag_name_two,
                "book": book_two.id
            },
            {
                "tag_name": tag_name_one,
                "book": book_one.id
            },
        ]

        bookTagList = BookTag.objects.filter(user=self.user)
        serializer = BookTagSerializer(bookTagList, many=True)

        self.assertEqual(serializer.data, expected_data)
