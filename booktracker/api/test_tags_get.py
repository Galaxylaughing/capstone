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
        # create a book
        new_book = Book.objects.create(
            title="TagTestBook", user=self.user)
        # create some tags
        tag_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=new_book)
        tag_two = BookTag.objects.create(
            tag_name="fiction/fantasy", user=self.user, book=new_book)
        tag_three = BookTag.objects.create(
            tag_name="cool", user=self.user, book=new_book)

        expected_data = {
            "tags": [
                {
                    "tag_name": tag_one.tag_name,
                    "book_id": new_book.id
                },
                {
                    "tag_name": tag_two.tag_name,
                    "book_id": new_book.id
                },
                {
                    "tag_name": tag_three.tag_name,
                    "book_id": new_book.id
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tags')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data, expected_data)

        