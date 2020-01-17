from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip
from django.utils import timezone
import datetime
import pytz

from .models import Book, BookAuthor, Series, BookTag, BookStatus
from .serializers import BookSerializer, BookAuthorSerializer, SeriesSerializer, BookTagSerializer, BookStatusSerializer

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
            name=series_name, 
            planned_count=planned_count, 
            user=self.user)
        self.secondBook = Book.objects.create(
            title="Second Book", 
            user=self.user, 
            position_in_series=1, 
            series=self.series)

        self.firstBookAuthorOne = BookAuthor.objects.create(
            author_name="John Doe", 
            user=self.user, 
            book=self.firstBook)
        self.firstBookAuthorTwo = BookAuthor.objects.create(
            author_name='Jane Doe', 
            user=self.user, 
            book=self.firstBook)
        self.secondBookAuthor = BookAuthor.objects.create(
            author_name="Jane Doe", 
            user=self.user, 
            book=self.secondBook)

    # BOOK SERIALIZER
    def test_bookserializer_returns_multiple_books(self):
        bookList = Book.objects.all()
        serializer = BookSerializer(bookList, many=True)

        self.assertEqual(serializer.data[0]['id'], self.firstBook.id)
        self.assertEqual(serializer.data[0]['title'], self.firstBook.title)

        self.assertEqual(serializer.data[1]['id'], self.secondBook.id)
        self.assertEqual(serializer.data[1]['title'], self.secondBook.title)

    def test_serializer_will_return_title(self):
        book = Book.objects.create(
            title="Serialize Title Test Book", user=self.user)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['title'], book.title)

    def test_serializer_will_return_authors(self):
        author_one = self.firstBookAuthorOne
        author_two = self.firstBookAuthorTwo

        book = self.firstBook
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['authors'][0], author_two.author_name)
        self.assertEqual(serializer.data['authors'][1], author_one.author_name)

    def test_serializer_will_return_publisher(self):
        publisher = "Tor Books"
        book = Book.objects.create(
            title="Serialize Publisher Test Book", 
            user=self.user,
            publisher=publisher)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['publisher'], book.publisher)

    def test_serializer_will_return_publication_date(self):
        publication_date = "2018-10-15"
        book = Book.objects.create(
            title="Serialize Publication Date Test Book", 
            user=self.user,
            publication_date=publication_date)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['publication_date'], book.publication_date)

    def test_serializer_will_return_isbn_10(self):
        isbn_10 = "8175257660"
        book = Book.objects.create(
            title="Serialize ISBN 10 Test Book", 
            user=self.user,
            isbn_10=isbn_10)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['isbn_10'], book.isbn_10)

    def test_serializer_will_return_isbn_13(self):
        isbn_13 = "9788175257665"
        book = Book.objects.create(
            title="Serialize ISBN 13 Test Book", 
            user=self.user,
            isbn_13=isbn_13)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['isbn_13'], book.isbn_13)

    def test_serializer_will_return_page_count(self):
        page_count = 214
        book = Book.objects.create(
            title="Serialize Page Count Test Book", 
            user=self.user,
            page_count=page_count)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['page_count'], book.page_count)

    def test_serializer_will_return_description(self):
        description = """Warbreaker is the story of two sisters, 
        who happen to be princesses, the God King one of them has to marry, 
        the lesser god who doesn&#39;t like his job, and the immortal who&#39;s 
        still trying to undo the mistakes he made hundreds of years ago."""
        book = Book.objects.create(
            title="Serialize Description Test Book", 
            user=self.user,
            description=description)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['description'], book.description)

    def test_serializer_will_return_current_status(self):
        current_status = Book.DISCARDED
        book = Book.objects.create(
            title="Serialize Current Status Test Book", 
            user=self.user,
            current_status=current_status)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['current_status'], book.current_status)

    def test_serializer_will_return_tags(self):
        user = User.objects.create(
            username='UserToTestTagRelationship', password='password')
        book = Book.objects.create(
            title="Book", user=user)
        tag = BookTag.objects.create(
            tag_name="fiction", user=user, book=book)

        book = Book.objects.get(id=book.id)
        serializer = BookSerializer(book)

        expected_tags = [tag.tag_name]
        self.assertEqual(serializer.data['id'], book.id)
        self.assertEqual(serializer.data['tags'], expected_tags)

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

class BookStatusSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="Book Tag Serializer User", password="password")
        self.token = str(self.user.auth_token)

    # BOOKSTATUS SERIALIZER
    def test_bookstatus_serializer_returns_expected_data(self):
        book = Book.objects.create(
            title="Status Serializer Test Book", user=self.user)
        date_one = pytz.utc.localize(datetime.datetime(2011, 1, 1))
        status_one = BookStatus.objects.create(
            status_code=Book.WANTTOREAD, 
            book=book, 
            user=self.user, 
            date=date_one
        )
        date_two = pytz.utc.localize(datetime.datetime(2011, 1, 2))
        status_two = BookStatus.objects.create(
            status_code=Book.CURRENT, 
            book=book, 
            user=self.user, 
            date=date_two
        )
        date_three = pytz.utc.localize(datetime.datetime(2011, 1, 3))
        status_three = BookStatus.objects.create(
            status_code=Book.COMPLETED, 
            book=book, 
            user=self.user, 
            date=date_three
        )

        expected_data = [
            {
                "id": status_one.id,
                "status_code": status_one.status_code,
                "book": book.id,
                "date": date_one.strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                "id": status_two.id,
                "status_code": status_two.status_code,
                "book": book.id,
                "date": date_two.strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            {
                "id": status_three.id,
                "status_code": status_three.status_code,
                "book": book.id,
                "date": date_three.strftime("%Y-%m-%dT%H:%M:%SZ")
            },
        ]

        bookstatus_list = BookStatus.objects.filter(user=self.user, book=book)
        serializer = BookStatusSerializer(bookstatus_list, many=True)

        self.assertEqual(serializer.data, expected_data)
