from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book, BookAuthor, Series, BookTag, BookStatus
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

    def test_book_can_have_a_current_status(self):
        expectedCount = Book.objects.count() + 1
        
        new_book = Book.objects.create(
            title="Current Status Test Book", 
            user=self.user, 
            current_status=Book.COMPLETED)
        filteredBooks = Book.objects.filter(id=new_book.id)

        self.assertEqual(Book.objects.count(), expectedCount)
        self.assertTrue(filteredBooks.exists())
        self.assertEqual(filteredBooks[0].current_status, Book.COMPLETED)
        self.assertEqual(filteredBooks[0].get_current_status_display(), "Completed")


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
            author_name="First Last", user=self.user, book=self.book)
        filteredBookAuthors = BookAuthor.objects.filter(
            author_name="First Last")

        self.assertEqual(BookAuthor.objects.count(), expectedCount)
        self.assertTrue(filteredBookAuthors.exists())

    def test_bookauthor_str_method(self):
        author_name = "M.K. Author"

        book_author = BookAuthor.objects.create(
            author_name=author_name, user=self.user, book=self.book)
        
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

class BookTagTests(TestCase):
    """ Test module for the BookTag model """

    def setUp(self):
        self.user = User.objects.create(
            username="TagUser", password="password")
        self.book = Book.objects.create(
            title="TagBook", user=self.user)

    def test_booktag_can_be_created(self):
        expectedCount = BookTag.objects.count() + 1

        tag_name = "cool-tag"
        BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=self.book)

        self.assertEqual(BookTag.objects.count(), expectedCount)
        filteredBookTags = BookTag.objects.filter(
            tag_name=tag_name)
        self.assertTrue(filteredBookTags.exists())
        self.assertEqual(filteredBookTags[0].tag_name, tag_name)
        self.assertEqual(filteredBookTags[0].user, self.user)
        self.assertEqual(filteredBookTags[0].book, self.book)

    def test_booktag_does_not_restrict_character_set(self):
        expectedCount = BookTag.objects.count() + 1

        tag_name = "#MY:2cool_4_school/tag."
        BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=self.book)

        self.assertEqual(BookTag.objects.count(), expectedCount)

        filteredBookTags = BookTag.objects.filter(
            tag_name=tag_name)
        self.assertTrue(filteredBookTags.exists())
        self.assertEqual(filteredBookTags[0].tag_name, tag_name)
        self.assertEqual(filteredBookTags[0].user, self.user)
        self.assertEqual(filteredBookTags[0].book, self.book)

    def test_tag_is_deleted_if_user_is_deleted(self):
        # create tag
        new_user = User.objects.create(
            username="TagUserToBeDeleted", password="password")
        tag_name = "cool-tag"
        BookTag.objects.create(
            tag_name=tag_name, user=new_user, book=self.book)

        # delete the tag's user
        new_user.delete()

        # check that tag no longer exists
        filteredBookTags = BookTag.objects.filter(
            tag_name=tag_name)
        self.assertFalse(filteredBookTags.exists())

    def test_tag_is_deleted_if_associated_book_is_deleted(self):
        # each booktag only has one book; 
        # multiple booktag rows can refer to the same tag_name for other books

        # create tag
        new_book = Book.objects.create(
            title="TagBookToBeDeleted", user=self.user)
        tag_name = "cool-tag"
        BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=new_book)

        # delete the tag's book
        new_book.delete()

        # check that tag no longer exists
        filteredBookTags = BookTag.objects.filter(
            tag_name=tag_name)
        self.assertFalse(filteredBookTags.exists())

    def test_booktag_str_method(self):
        tag_name = "cool-tag"

        tag = BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=self.book)
        
        self.assertEqual(str(tag), tag_name)

class BookStatusTests(TestCase):
    """ Test module for the BookStatus model """

    def setUp(self):
        self.user = User.objects.create(
            username="StatusUser", password="password")
        self.book = Book.objects.create(
            title="BookStatus", user=self.user)

    def test_bookstatus_str_method(self):
        status_code = Book.CURRENT
        status = BookStatus.objects.create(
            status_code=status_code, user=self.user, book=self.book)

        self.assertEqual(str(status), status_code)

    def test_bookstatus_can_be_created(self):
        expected_count = BookStatus.objects.count() + 1

        status_code = Book.COMPLETED
        status = BookStatus.objects.create(
            status_code=status_code, user=self.user, book=self.book)

        self.assertEqual(BookStatus.objects.count(), expected_count)

        filtered_book_statuses = BookStatus.objects.filter(
            status_code=status_code, book=self.book)
        self.assertTrue(filtered_book_statuses.exists())
        self.assertEqual(filtered_book_statuses[0].status_code, status_code)
        self.assertEqual(filtered_book_statuses[0].user, self.user)
        self.assertEqual(filtered_book_statuses[0].book, self.book)
        
    def test_bookstatus_is_deleted_if_user_is_deleted(self):
        expected_count = BookStatus.objects.count() + 1

        new_user = User.objects.create(
            username="Status User to Be Deleted", password="password")
        new_book = Book.objects.create(
            title="Status Book of User to Be Deleted", user=new_user)
        status_code = Book.COMPLETED
        status = BookStatus.objects.create(
            status_code=status_code, user=new_user, book=new_book)
        self.assertEqual(BookStatus.objects.count(), expected_count)

        new_user.delete()

        self.assertEqual(BookStatus.objects.count(), expected_count - 1)
