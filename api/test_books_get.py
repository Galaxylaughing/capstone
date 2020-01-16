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
        book_one = Book.objects.create(
            title="First Book", user=self.user)
        book_two = Book.objects.create(
            title="Second Book", user=self.user)

        # give the books some authors
        book_one_author_one = BookAuthor.objects.create(
            author_name="John Doe", 
            user=self.user, 
            book=book_one)
        book_one_author_two = BookAuthor.objects.create(
            author_name="Jane Doe", 
            user=self.user, 
            book=book_one)
        book_two_author_one = BookAuthor.objects.create(
            author_name="Jane Doe",
            user=self.user, 
            book=book_two)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['books'][1]['id'], book_one.id)
        self.assertEqual(response.data['books'][1]['title'], book_one.title)
        self.assertEqual(response.data['books'][1]['authors'][0], book_one_author_two.author_name)
        self.assertEqual(response.data['books'][1]['authors'][1], book_one_author_one.author_name)

        self.assertEqual(response.data['books'][0]['id'], book_two.id)
        self.assertEqual(response.data['books'][0]['title'], book_two.title)
        self.assertEqual(response.data['books'][0]['authors'][0], book_two_author_one.author_name)

    def test_returns_empty_list_if_no_books(self):
        expected_data = {"books": []}

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
        
    def test_returns_error_if_unauthorized(self):
        # DON'T add token to header
        # get the API response
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_access_a_specific_users_books(self):
        new_user = User.objects.create(
            username='Caspar', 
            password='password')
        new_user_token = str(new_user.auth_token)

        # give the new user a book
        publisher = "Tor"
        publication_date = "2010-10-10"
        isbn_10 = "8175257660"
        isbn_13 = "9788175257665"
        page_count = 717
        new_book = Book.objects.create(
            title="First Book", 
            user=new_user,
            publisher=publisher,
            publication_date=publication_date,
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            page_count=page_count)
        new_author = BookAuthor.objects.create(
            author_name="Jane Doe", 
            user=new_user, 
            book=new_book)

        # give the setup user a book
        old_book = Book.objects.create(
            title="Second Book", 
            user=self.user)
        BookAuthor.objects.create(
            author_name="John Doe", 
            user=self.user, 
            book=old_book)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + new_user_token)
        url = reverse('books')
        response = self.client.get(url, format='json')

        # new user should only see their book
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['books'][0]['id'], new_book.id)
        self.assertEqual(response.data['books'][0]['title'], new_book.title)
        self.assertEqual(response.data['books'][0]['publisher'], new_book.publisher)
        self.assertEqual(response.data['books'][0]['publication_date'], new_book.publication_date)
        self.assertEqual(response.data['books'][0]['isbn_10'], new_book.isbn_10)
        self.assertEqual(response.data['books'][0]['isbn_13'], new_book.isbn_13)
        self.assertEqual(response.data['books'][0]['page_count'], new_book.page_count)
        self.assertEqual(response.data['books'][0]['authors'][0], new_author.author_name)
