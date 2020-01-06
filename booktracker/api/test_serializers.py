from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book, BookAuthor, Series
from .serializers import BookSerializer, BookAuthorSerializer, SeriesSerializer

from django.apps import apps
User = apps.get_model('userauth','User')

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

    def test_series_serializer_returns_expected_data(self):
        first_series_name = "Cool Series"
        first_planned_count = 3
        first_series = Series.objects.create(
            name=first_series_name, planned_count=first_planned_count, user=self.user)

        second_series_name = "Other Series"
        second_planned_count = 2
        second_series = Series.objects.create(
            name=second_series_name, planned_count=second_planned_count, user=self.user)

        first_series_id = first_series.id
        expected_data = [
            {
                'id': first_series_id,
                'name': first_series_name,
                'planned_count': first_planned_count
            },
            {
                'id': second_series.id,
                'name': second_series_name,
                'planned_count': second_planned_count
            }
        ]

        seriesList = Series.objects.all()
        serializer = SeriesSerializer(seriesList, many=True)

        self.assertEqual(serializer.data, expected_data)
