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


class GetBookTagTest(APITestCase):
    """ Test module for getting the details of a User's BookTag """

    def setUp(self):
        self.user = User.objects.create(
            username="BookTagUser", password="password")
        self.token = str(self.user.auth_token)

    def test_can_get_details_for_existing_booktag(self):
        new_book = Book.objects.create(
            title="TagTestBook", user=self.user)
        tag_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=new_book)

        expected_data = {
            "tag": {
                "tag_name": tag_one.tag_name,
                "book": new_book.id
            }
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={'tag_id': tag_one.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_cannot_get_details_for_another_users_booktag(self):
        new_user = User.objects.create(
            username="AnotherBookTagUser", password="password")
        new_book = Book.objects.create(
            title="OtherUsersBook", user=new_user)
        new_tag = BookTag.objects.create(
            tag_name="OtherUsersTag", user=new_user, book=new_book)

        expected_data = {
            "error": "unauthorized"
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={'tag_id': new_tag.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_no_booktag_found(self):
        fake_tag = 999
        expected_data = {
            'error': "Could not find tag with ID: %s" %(fake_tag)
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={'tag_id': fake_tag})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_unauthorized(self):
        new_book = Book.objects.create(
            title="TagTestBook", user=self.user)
        tag_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=new_book)

        # DON'T set token in header
        url = reverse('tag', kwargs={'tag_id': tag_one.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        