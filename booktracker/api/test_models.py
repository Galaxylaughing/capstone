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

    def test_book_can_have_a_position_in_series(self):
        expectedCount = Book.objects.count() + 1
        
        new_book = Book.objects.create(
            title="Test Book", user=self.user, position_in_series=1)
        filteredBooks = Book.objects.filter(id=new_book.id)

        self.assertEqual(Book.objects.count(), expectedCount)
        self.assertTrue(filteredBooks.exists())


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


class SeriesTests(TestCase):
    """ test module for the Series model """

    def setUp(self):
        self.user = User.objects.create(
            username="Series Test User", password="password")

    def test_series_can_be_created(self):
        expected_count = Series.objects.count() + 1

        series_name = "Cool Series"
        planned_count = 3
        Series.objects.create(
            name=series_name, planned_count=planned_count, user=self.user)

        self.assertEqual(Series.objects.count(), expected_count)

        filteredSeries = Series.objects.filter(
            name=series_name)
        self.assertTrue(filteredSeries.exists())
        self.assertEqual(filteredSeries[0].name, series_name)
        self.assertEqual(filteredSeries[0].planned_count, planned_count)

    def test_can_assign_book_to_series(self):
        # create series
        series_name = "Cool Series"
        planned_count = 3
        series = Series.objects.create(
            name=series_name, planned_count=planned_count, user=self.user)

        # create a book
        user = User.objects.create(
            username="Fakey", password="password")
        book_in_series = Book.objects.create(
            title="Book", user=user, series=series)

        filteredBook = Book.objects.filter(id=book_in_series.id)
        self.assertTrue(filteredBook.exists())
        self.assertEqual(filteredBook[0].title, "Book")
        self.assertEqual(filteredBook[0].series, series)

    def test_fk_to_series_can_be_nullified(self):
        # create series
        series_name = "Cool Series"
        planned_count = 3
        series = Series.objects.create(
            name=series_name, planned_count=planned_count, user=self.user)

        # create a book
        user = User.objects.create(
            username="Fakey", password="password")
        book_in_series = Book.objects.create(
            title="Book", user=user, series=series)

        # delete the series
        series.delete()

        filteredSeries = Series.objects.filter(
            name=series_name)
        self.assertFalse(filteredSeries.exists())

        filteredBook = Book.objects.filter(id=book_in_series.id)
        self.assertTrue(filteredBook.exists())
        self.assertEqual(filteredBook[0].series, None)

    def test_series_str_method(self):
        series_name = "Cool Series"
        planned_count = 3
        series = Series.objects.create(
            name=series_name, planned_count=planned_count, user=self.user)
        
        self.assertEqual(str(series), series_name)
