from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book, BookAuthor, Series, BookTag
from .serializers import BookSerializer, BookAuthorSerializer

from django.apps import apps
User = apps.get_model('userauth','User')


class GetBookDetailsTest(APITestCase):
    """ Test module for getting the details of a specific book """

    def setUp(self):
        # create a user
        username = 'Bertie'
        password = 'password'
        self.user = User.objects.create(
            username=username, password=password)
        # get the user's token
        self.token = str(self.user.auth_token)

    def test_can_get_details_for_existing_book(self):
        # give the user a book
        publisher = "Tor"
        publication_date = "2010-10-10"
        isbn_10 = "8175257660"
        isbn_13 = "9788175257665"
        page_count = 717
        description = """Warbreaker is the story of two sisters, 
        who happen to be princesses, the God King one of them has to marry, 
        the lesser god who doesn&#39;t like his job, and the immortal who&#39;s 
        still trying to undo the mistakes he made hundreds of years ago."""

        firstBook = Book.objects.create(
            title="First Book", 
            user=self.user,
            position_in_series=1,
            publisher=publisher,
            publication_date=publication_date,
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            page_count=page_count,
            description=description)

        # give the book an author
        BookAuthor.objects.create(
            author_name="Jane Doe", user=self.user, book=firstBook)

        firstId = firstBook.id
        expected_data = {
            'book': {
                'id': firstId,
                'title': 'First Book',
                'authors': [
                    'Jane Doe'
                ],
                'position_in_series': 1,
                'series': None,
                'publisher': publisher,
                'publication_date': publication_date,
                'isbn_10': isbn_10,
                'isbn_13': isbn_13,
                'page_count': page_count,
                'description': description,
                'tags': []
            }
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': firstId})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_cannot_get_details_for_another_users_book(self):
        new_user = User.objects.create(
            username="New User", password="password")
        new_book = Book.objects.create(
            title="New User's Book", user=new_user)

        expected_data = {
            "error": "unauthorized"
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': new_book.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_no_book_found(self):
        fakeId = 999
        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': fakeId})
        response = self.client.get(url, format='json')

        error_message = "No book found with the ID: %s" %(fakeId)
        expected_data = {
            'error': error_message
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)
        
    def test_returns_error_if_unauthorized(self):
        # give the user a book
        firstBook = Book.objects.create(
            title="First Book", user=self.user)
        # give the book an author
        BookAuthor.objects.create(
            author_name="Jane Doe", user=self.user, book=firstBook)

        firstId = firstBook.id
        
        # DON'T add token to header
        # get the API response
        url = reverse('book', kwargs={'book_id': firstId})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_get_title(self):
        book = Book.objects.create(
            title="Title Test Book", 
            user=self.user)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['title'], book.title)

    def test_can_get_author(self):
        book = Book.objects.create(
            title="Author Test Book", 
            user=self.user)

        author = BookAuthor.objects.create(
            author_name="Jane Doe", 
            user=self.user, 
            book=book)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['authors'][0], author.author_name)

    def test_can_get_multiple_authors(self):
        book = Book.objects.create(
            title="Authors Test Book", 
            user=self.user)

        author_one = BookAuthor.objects.create(
            author_name="Jane Doe", 
            user=self.user, 
            book=book)
        author_two = BookAuthor.objects.create(
            author_name="John James", 
            user=self.user, 
            book=book)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['authors'][0], author_two.author_name)
        self.assertEqual(response.data['book']['authors'][1], author_one.author_name)

    def test_can_get_position_in_series(self):
        position = 1
        book = Book.objects.create(
            title="Position Test Book", 
            user=self.user,
            position_in_series=position)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['position_in_series'], position)

    def test_can_get_series(self):
        series_name = "Series-Book Test Series"
        series = Series.objects.create(
            name=series_name, 
            planned_count=3, 
            user=self.user)
        book = Book.objects.create(
            title="Series Test Book", 
            user=self.user,
            series=series)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['series'], series.id)

    def test_can_get_publisher(self):
        publisher = "Tor"
        book = Book.objects.create(
            title="Publisher Test Book", 
            user=self.user,
            publisher=publisher)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['publisher'], publisher)

    def test_can_get_publication_date(self):
        publication_date = "2010-10-10"
        book = Book.objects.create(
            title="Publication Date Test Book", 
            user=self.user,
            publication_date=publication_date)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['publication_date'], publication_date)

    def test_can_get_isbn_10(self):
        isbn_10 = "8175257660"
        book = Book.objects.create(
            title="ISBN 10 Test Book", 
            user=self.user,
            isbn_10=isbn_10)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['isbn_10'], isbn_10)

    def test_can_get_isbn_13(self):
        isbn_13 = "9788175257665"
        book = Book.objects.create(
            title="ISBN 13 Test Book", 
            user=self.user,
            isbn_13=isbn_13)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['isbn_13'], isbn_13)

    def test_can_get_description(self):
        description = """Warbreaker is the story of two sisters, 
        who happen to be princesses, the God King one of them has to marry, 
        the lesser god who doesn&#39;t like his job, and the immortal who&#39;s 
        still trying to undo the mistakes he made hundreds of years ago."""
        book = Book.objects.create(
            title="Description Test Book", 
            user=self.user,
            description=description)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['description'], description)

    def test_can_get_tag(self):
        book = Book.objects.create(
            title="Tag Test Book", 
            user=self.user)

        tag = BookTag.objects.create(
            tag_name="fiction", 
            user=self.user, 
            book=book)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['tags'][0], tag.tag_name)

    def test_can_get_multiple_tags(self):
        book = Book.objects.create(
            title="Tags Test Book", 
            user=self.user)

        tag_one = BookTag.objects.create(
            tag_name="fiction", 
            user=self.user, 
            book=book)
        tag_two = BookTag.objects.create(
            tag_name="non-fiction", 
            user=self.user, 
            book=book)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['tags'][0], tag_two.tag_name)
        self.assertEqual(response.data['book']['tags'][1], tag_one.tag_name)

    def test_can_get_current_status(self):
        book = Book.objects.create(
            title="Current Status Test Book", 
            user=self.user,
            current_status=Book.CURRENT)

        book_id = book.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book_id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['id'], book.id)
        self.assertEqual(response.data['book']['current_status'], Book.CURRENT)
