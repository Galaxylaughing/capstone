from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip

from .models import Book
from .serializers import BookSerializer

from django.apps import apps
User = apps.get_model('userauth','User')

class UpdateBookRatingTests(APITestCase):
    """ test module for updating a Book's rating field """

    def setUp(self):
        self.user = User.objects.create(
            username="Bertie Jr.", 
            password="password"
        )
        self.token = str(
          self.user.auth_token
        )
        self.book = Book.objects.create(
            title="Update Rating Field Test Book", 
            user=self.user
        )

    def test_can_update_book_rating_field_to_be_rated(self):
        new_rating = Book.THREE
        data = {
            "rating": new_rating
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('rating', kwargs={'book_id': self.book.id})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        self.assertEqual(response.data['books'][0]['id'], self.book.id)
        self.assertEqual(response.data['books'][0]['rating'], new_rating)

        # find book in database
        updated_book = Book.objects.get(id=self.book.id)
        self.assertEqual(updated_book.rating, new_rating)

    def test_can_update_book_rating_field_to_be_unrated(self):
        rated_book = Book.objects.create(
            title="Update Rating Field To Unrated Test Book", 
            user=self.user,
            rating=Book.FOUR
        )

        new_rating = Book.UNRATED
        data = {
            "rating": new_rating
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('rating', kwargs={'book_id': rated_book.id})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        self.assertEqual(response.data['books'][0]['id'], rated_book.id)
        self.assertEqual(response.data['books'][0]['rating'], new_rating)

        # find book in database
        updated_book = Book.objects.get(id=rated_book.id)
        self.assertEqual(updated_book.rating, new_rating)

    def test_returns_error_if_not_given_new_rating(self):
        new_rating = Book.TWO
        data = {
            "rating": new_rating
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('rating', kwargs={'book_id': self.book.id})
        response = self.client.put(url, format='json')

        # determine expected data
        expected_data = {
            'error': 'New Rating Not Provided'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_book_not_found(self):
        fake_id = 999
        new_rating = Book.TWO
        data = {
            "rating": new_rating
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('rating', kwargs={'book_id': fake_id})
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'error': 'Could not find book with ID: %s' %(fake_id)
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_returns_error_if_rating_invalid(self):
        rated_book = Book.objects.create(
            title="Won't Give Invalid Rating Test Book", 
            user=self.user,
            rating=Book.FOUR
        )

        new_rating = 20
        data = {
            "rating": new_rating
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('rating', kwargs={'book_id': rated_book.id})
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'error': '%s is not a valid rating' %(new_rating)
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_user_cannot_rate_other_users_book(self):
        other_user = User.objects.create(
            username="Other Rating User", 
            password="password"
        )
        other_users_book = Book.objects.create(
            title="Won't Give Rating To Other Users Book Test Book", 
            user=other_user,
            rating=Book.FOUR
        )

        new_rating = Book.THREE
        data = {
            "rating": new_rating
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('rating', kwargs={'book_id': other_users_book.id})
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'error': 'Could not find book with ID: %s' %(other_users_book.id)
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)