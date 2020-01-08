from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book, BookTag
from .serializers import BookSerializer

from django.apps import apps
User = apps.get_model('userauth','User')


class GetBookTagsTest(APITestCase):
    """ Test module for getting a list of a User's BookTags """

    def setUp(self):
        self.user = User.objects.create(
            username="BookTagUser", password="password")
        self.token = str(self.user.auth_token)

    def test_can_access_a_users_booktags(self):
        new_book_one = Book.objects.create(
            title="TagTestBookOne", user=self.user)
        fiction_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=new_book_one)
        fantasy_one = BookTag.objects.create(
            tag_name="fiction/fantasy", user=self.user, book=new_book_one)
        cool_one = BookTag.objects.create(
            tag_name="cool", user=self.user, book=new_book_one)

        new_book_two = Book.objects.create(
            title="TagTestBookTwo", user=self.user)
        fiction_two = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=new_book_two)

        expected_data = {
            "tags": [
                {
                    "name": fiction_one.tag_name,
                    "books": [new_book_two.id, new_book_one.id]
                },
                {
                    "name": cool_one.tag_name,
                    "books": [new_book_one.id]
                },
                {
                    "name": fantasy_one.tag_name,
                    "books": [new_book_one.id]
                },
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tags')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_can_access_a_specific_users_booktags(self):
        new_book_one = Book.objects.create(
            title="TagTestBookOne", user=self.user)
        fiction_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=new_book_one)
        cool_one = BookTag.objects.create(
            tag_name="cool", user=self.user, book=new_book_one)

        new_book_two = Book.objects.create(
            title="TagTestBookTwo", user=self.user)
        fiction_two = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=new_book_two)
        
        # create another user
        other_user = User.objects.create(
            username="OtherBookTagUser", password="password")
        other_book = Book.objects.create(
            title="TagTestBook", user=other_user)
        other_tag = BookTag.objects.create(
            tag_name="fiction", user=other_user, book=other_book)

        expected_data = {
            "tags": [
                {
                    "name": fiction_one.tag_name,
                    "books": [new_book_two.id, new_book_one.id]
                },
                {
                    "name": cool_one.tag_name,
                    "books": [new_book_one.id]
                },
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tags')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_returns_empty_list_if_no_booktags(self):
        expected_data = {"tags": []}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tags')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
        
    def test_returns_error_if_unauthorized(self):
        # DON'T add token to header
        # get the API response
        url = reverse('tags')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
