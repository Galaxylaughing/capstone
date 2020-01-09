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


class PutBookTagTest(APITestCase):
    """ Test module for modifying a User's BookTag """

    def setUp(self):
        self.user = User.objects.create(
            username="BookTagUser", password="password")
        self.token = str(self.user.auth_token)

    def test_can_change_tag_name(self):
        """ should change the tag_name for every instance of that tag_name in the database """
        
        book_one = Book.objects.create(
            title="PutTagTestBookOne", user=self.user)
        fiction_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_one)

        book_two = Book.objects.create(
            title="PutTagTestBookOne", user=self.user)
        fiction_two = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_two)

        data = {
            "new_name": "fantasy",
            "books": [book_one.id, book_two.id]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": fiction_one.tag_name})
        response = self.client.put(url, data, format='json')

        expected_data = {
            "tags": [{
                "tag_name": data["new_name"],
                "books": [book_one.id, book_two.id]
            }]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        updated_tag_one = BookTag.objects.get(id=fiction_one.id)
        self.assertEqual(updated_tag_one.tag_name, data["new_name"])
        updated_tag_two = BookTag.objects.get(id=fiction_two.id)
        self.assertEqual(updated_tag_two.tag_name, data["new_name"])

    def test_returns_unchanged_if_new_name_is_not_different(self):
        book_one = Book.objects.create(
            title="PutTagTestBookOne", user=self.user)
        fiction_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_one)

        data = {
            "new_name": fiction_one.tag_name,
            "books": [book_one.id]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": fiction_one.tag_name})
        response = self.client.put(url, data, format='json')

        expected_data = {
            "tags": [{
                "tag_name": data["new_name"],
                "books": [book_one.id]
            }]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_new_name_is_not_provided(self):
        book_one = Book.objects.create(
            title="PutTagTestBookOne", user=self.user)
        fiction_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_one)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": fiction_one.tag_name})
        response = self.client.put(url, format='json')

        expected_data = {
            "error": "new name or list of books was not provided"
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_user_can_only_modify_their_own_tags(self):
        book_one = Book.objects.create(
            title="PutTagTestBookOne", user=self.user)
        fiction_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_one)

        # create another user
        other_user = User.objects.create(
            username="PutTagTestUserTwo", password="password")
        other_book = Book.objects.create(
            title="PutTagTestBookTwo", user=other_user)
        other_tag = BookTag.objects.create(
            tag_name="fiction", user=other_user, book=other_book)

        new_name = "fantasy"
        data = {
            "new_name": new_name,
            "books": [book_one.id]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": fiction_one.tag_name})
        response = self.client.put(url, data, format='json')

        expected_data = {
            "tags": [{
                "tag_name": data["new_name"],
                "books": [book_one.id]
            }]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        updated_tag = BookTag.objects.get(id=fiction_one.id)
        self.assertEqual(updated_tag.tag_name, data["new_name"])

        not_updated_tag = BookTag.objects.get(id=other_tag.id)
        self.assertEqual(not_updated_tag.tag_name, other_tag.tag_name)

    def test_returns_error_if_no_tags_match(self):
        # create another user
        other_user = User.objects.create(
            username="PutTagTestUserTwo", password="password")
        other_book = Book.objects.create(
            title="PutTagTestBookTwo", user=other_user)
        other_tag = BookTag.objects.create(
            tag_name="science-fiction", user=other_user, book=other_book)

        data = {
            "new_name": other_tag.tag_name,
            "books": [other_book.id]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": other_tag.tag_name})
        response = self.client.put(url, data, format='json')

        expected_data = {
            "error": "No tags match the name '%s'" %(other_tag.tag_name)
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_unauthorized(self):
        book_one = Book.objects.create(
            title="PutTagTestBookOne", user=self.user)
        fiction_one = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_one)

        data = {
            "new_name": "thriller",
            "books": [book_one.id]
        }

        # DON'T add token to header
        url = reverse('tag', kwargs={"tag_name": fiction_one.tag_name})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_can_give_a_tag_a_different_book(self):
        book_one = Book.objects.create(
            title="UpdateTagBooksOne", user=self.user)
        book_two = Book.objects.create(
            title="UpdateTagBooksTwo", user=self.user)
        fiction = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_one)

        data = {
            "new_name": fiction.tag_name,
            "books": [book_two.id]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": fiction.tag_name})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        removed = BookTag.objects.filter(tag_name=fiction.tag_name, user=self.user, book=book_one)
        self.assertFalse(removed.exists())

        added = BookTag.objects.filter(tag_name=fiction.tag_name, user=self.user, book=book_two)
        self.assertTrue(added.exists())

        expected_data = {
            "tags": [{
                "tag_name": fiction.tag_name,
                "books": [book_two.id]
            }]
        }
        self.assertEqual(response.data, expected_data)

    def test_can_add_a_book_to_a_tag(self):
        book_one = Book.objects.create(
            title="UpdateTagBooksOne", user=self.user)
        book_two = Book.objects.create(
            title="UpdateTagBooksTwo", user=self.user)
        fiction = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_one)

        data = {
            "new_name": fiction.tag_name,
            "books": [book_one.id, book_two.id]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": fiction.tag_name})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        removed = BookTag.objects.filter(tag_name=fiction.tag_name, user=self.user, book=book_one)
        self.assertTrue(removed.exists())
        added = BookTag.objects.filter(tag_name=fiction.tag_name, user=self.user, book=book_two)
        self.assertTrue(added.exists())

        expected_data = {
            "tags": [{
                "tag_name": fiction.tag_name,
                "books": [book_one.id, book_two.id]
            }]
        }
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_cannot_find_book(self):
        book_one = Book.objects.create(
            title="UpdateTagBooksOne", user=self.user)
        fiction = BookTag.objects.create(
            tag_name="fiction", user=self.user, book=book_one)

        data = {
            "new_name": fiction.tag_name,
            "books": [999]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": fiction.tag_name})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        non_removed = BookTag.objects.filter(tag_name=fiction.tag_name, user=self.user, book=book_one)
        self.assertTrue(non_removed.exists())

        non_added = BookTag.objects.filter(tag_name=fiction.tag_name, user=self.user, book__id=999)
        self.assertFalse(non_added.exists())

        expected_data = {
            "error": "Could not find book with ID: %s" %(999)
        }
        self.assertEqual(response.data, expected_data)


        # another test: if you give an empty books list, it deletes the tag
    def test_will_delete_tag_if_given_empty_book_list(self):
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

        data = {
            "new_name": "something",
            "books": []
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('tag', kwargs={"tag_name": tag_name})
        response = self.client.put(url, data, format='json')

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
