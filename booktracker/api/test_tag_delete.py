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


class DeleteBookTagTest(APITestCase):
    """ Test module for deleting a User's BookTag """

    def setUp(self):
        self.user = User.objects.create(
            username="BookTagUser", password="password")
        self.token = str(self.user.auth_token)

    def test_can_delete_a_tag_by_name(self):
        """ should delete every instance of the tag name associated with the user """

        # make two books and give them a tag
        book_one = Book.objects.create(
            title="TagDeleteBookOne", user=self.user)
        book_two = Book.objects.create(
            title="TagDeleteBookTwo", user=self.user)

        tag_name = "mystery"
        tag_one = BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=book_one)
        tag_two = BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=book_two)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": tag_name})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "tags": [
                {
                    "tag_name": tag_two.tag_name,
                    "book": book_two.id
                },
                {
                    "tag_name": tag_one.tag_name,
                    "book": book_one.id
                },
            ]
        }
        self.assertEqual(response.data, expected_data)

        deleted_tag = BookTag.objects.filter(tag_name=tag_name)
        self.assertFalse(deleted_tag.exists())

    def test_user_can_only_delete_their_own_tags(self):
        # make two books and give them a tag
        book_one = Book.objects.create(
            title="TagDeleteBookOne", user=self.user)

        other_user = User.objects.create(
            username="TagDeleteUserTwo", password="password")
        other_book = Book.objects.create(
            title="TagDeleteBookTwo", user=other_user)

        tag_name = "mystery"
        tag_one = BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=book_one)
        tag_two = BookTag.objects.create(
            tag_name=tag_name, user=other_user, book=other_book)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": tag_name})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "tags": [
                {
                    "tag_name": tag_one.tag_name,
                    "book": book_one.id
                },
            ]
        }
        self.assertEqual(response.data, expected_data)

        deleted_tag = BookTag.objects.filter(tag_name=tag_name, user=self.user)
        self.assertFalse(deleted_tag.exists())

        undeleted_tags = BookTag.objects.filter(tag_name=tag_name, user=other_user)
        self.assertTrue(undeleted_tags.exists())

    def test_returns_error_if_no_tags_found(self):
        tag_name = "I don't exist"

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": tag_name})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_data = {
            "error": "Could not find any tags matching the name '%s'" %(tag_name)
        }
        self.assertEqual(response.data, expected_data)
