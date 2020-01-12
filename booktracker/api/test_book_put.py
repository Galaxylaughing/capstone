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


class UpdateBookTests(APITestCase):
    """ test module for updating a book """

    def setUp(self):
        # create a user
        username = 'Bertie'
        password = 'password'
        self.user = User.objects.create(
            username=username, password=password)
        # get the user's token
        self.token = str(self.user.auth_token)
        # give the user a book
        self.title = "First Book"
        self.first_book = Book.objects.create(
            title=self.title, user=self.user)
        self.book_id = self.first_book.id
        # give the book two authors
        self.author_one = "Jane Doe"
        BookAuthor.objects.create(
            author_name=self.author_one, user=self.user, book=self.first_book)
        self.author_two = "John Doe"
        BookAuthor.objects.create(
            author_name=self.author_two, user=self.user, book=self.first_book)

    def test_can_update_with_all_fields_changed(self):
        """ if given all fields, and all are new, can update book """
        # make the parameters
        new_title = 'New Book With Unique Title'
        author_one = "New Author"
        author_two = "Other Author"
        tag_one = "fantasy"
        tag_two = "horror"
        data = {
            "title": new_title,
            "authors": [author_one, author_two],
            "tags": [tag_one, tag_two]
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # should have generated two bookauthor rows
        filtered_authors_one = BookAuthor.objects.filter(author_name=author_one, book=self.first_book)
        filtered_authors_two = BookAuthor.objects.filter(author_name=author_two, book=self.first_book)
        self.assertTrue(filtered_authors_one.exists())
        self.assertTrue(filtered_authors_two.exists())
        self.assertEqual(filtered_authors_one[0].author_name, author_one)
        self.assertEqual(filtered_authors_two[0].author_name, author_two)
        # should have generated two booktag row
        filtered_tags_one = BookTag.objects.filter(tag_name=tag_one, user=self.user, book=self.first_book)
        filtered_tags_two = BookTag.objects.filter(tag_name=tag_two, user=self.user, book=self.first_book)
        self.assertTrue(filtered_tags_one.exists())
        self.assertTrue(filtered_tags_two.exists())
        self.assertEqual(filtered_tags_one[0].tag_name, tag_one)
        self.assertEqual(filtered_tags_two[0].tag_name, tag_two)
        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': new_title,
                'authors': [
                    author_two,
                    author_one
                ],
                'position_in_series': None,
                'series': None,
                'tags': [filtered_tags_two[0].tag_name, filtered_tags_one[0].tag_name]
            }]
        }
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, new_title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue("New Author" in author_values)
        self.assertTrue("Other Author" in author_values)

    def test_can_update_with_only_some_fields_changed(self):
        """ if given all fields, but only some are new, can update book """
        # make the parameters
        new_title = 'New Book With Unique Title'
        author_one = self.author_one
        author_two = self.author_two
        data = {
            "title": new_title,
            "authors": [author_one, author_two]
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': new_title,
                'authors': [
                    author_two,
                    author_one
                ],
                'position_in_series': None,
                'series': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, new_title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(author_one in author_values)
        self.assertTrue(author_two in author_values)

    def test_can_update_with_only_new_authors_provided(self):
        """ if given only the author field, and it is new, can update book """
        # make the parameters
        # not changing title
        author_one = self.author_one
        author_two = self.author_two
        data = {
            "authors": [author_one, author_two]
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': self.title,
                'authors': [
                    author_two,
                    author_one
                ],
                'position_in_series': None,
                'series': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, self.title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(author_one in author_values)
        self.assertTrue(author_two in author_values)

    def test_can_update_with_only_new_title_provided(self):
        """ if given only the title field, and it is new, can update book """
        # make the parameters
        new_title = 'New Book With Unique Title'
        data = {
            "title": new_title
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        author_one = self.author_one
        author_two = self.author_two
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': new_title,
                'authors': [
                    author_two,
                    author_one
                ],
                'position_in_series': None,
                'series': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, new_title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(author_one in author_values)
        self.assertTrue(author_two in author_values)

    def test_can_update_a_book_to_have_series(self):
        """ if given only the series fields, and it is new, can update book """
        series = Series.objects.create(
            name="Cool Series", planned_count=3, user=self.user)
        series_id = series.id

        # make the parameters
        data = {
            "position_in_series": 1,
            "series": series_id
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        title = self.title
        author_one = self.author_one
        author_two = self.author_two
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': title,
                'authors': [
                    author_two,
                    author_one
                ],
                'position_in_series': 1,
                'series': series_id,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updated_book)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(author_one in author_values)
        self.assertTrue(author_two in author_values)

        # find the series infor
        self.assertEqual(updated_book.position_in_series, 1)
        self.assertEqual(updated_book.series, series)

    def test_returns_error_if_book_not_found(self):
        fake_id = 999

        # make the parameters
        new_title = 'New Book With Unique Title'
        data = {
            "title": new_title
        }

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': fake_id})
        # make request
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'error': 'Could not find book with ID: %s' %(fake_id)
        }
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.title, self.first_book.title)
        
    def test_will_not_create_a_tag_that_already_exists(self):
        # create new book
        book = Book.objects.create(
            title="A New Book That Already Has A Tag", user=self.user)
        tag_name = "fantasy"
        BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=book)

        filtered_tags_before = BookTag.objects.filter(tag_name=tag_name, user=self.user, book=book)
        self.assertTrue(filtered_tags_before.exists())
        self.assertEqual(filtered_tags_before.count(), 1)

        # make the parameters
        data = {
            "tags": [tag_name]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book.id})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # should NOT have generated a booktag row
        filtered_tags_after = BookTag.objects.filter(tag_name=tag_name, user=self.user, book=book)

        self.assertTrue(filtered_tags_after.exists())
        self.assertEqual(filtered_tags_after.count(), 1)
        
        # determine expected data
        expected_data = {
            'books': [{
                'id': book.id,
                'title': book.title,
                'authors': [],
                'position_in_series': None,
                'series': None,
                'tags': [tag_name]
            }]
        }
        self.assertEqual(response.data, expected_data)

    def test_will_not_create_duplicate_tags(self):
        # create new book
        book = Book.objects.create(
            title="A New Book That Already Has A Tag", user=self.user)
        tag_name = "fantasy"

        # make the parameters
        data = {
            "tags": [tag_name, tag_name]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book.id})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # should NOT have generated a booktag row
        filtered_tags_after = BookTag.objects.filter(tag_name=tag_name, user=self.user, book=book)

        self.assertTrue(filtered_tags_after.exists())
        self.assertEqual(filtered_tags_after.count(), 1)
        
        # determine expected data
        expected_data = {
            'books': [{
                'id': book.id,
                'title': book.title,
                'authors': [],
                'position_in_series': None,
                'series': None,
                'tags': [tag_name]
            }]
        }
        self.assertEqual(response.data, expected_data)

    def test_will_remove_tags(self):
        # create new book
        book = Book.objects.create(
            title="A New Book That Already Has A Tag", user=self.user)
        tag_name = "fantasy"
        BookTag.objects.create(
            tag_name=tag_name, user=self.user, book=book)

        filtered_tags_before = BookTag.objects.filter(tag_name=tag_name, user=self.user, book=book)
        self.assertTrue(filtered_tags_before.exists())
        self.assertEqual(filtered_tags_before.count(), 1)

        new_tag_name = "fiction"
        # make the parameters
        data = {
            "tags": [new_tag_name]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': book.id})
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        all_tags_for_book = BookTag.objects.filter(user=self.user, book=book)
        self.assertEqual(all_tags_for_book.count(), 1)
        
        # should have generated a booktag row
        filtered_tags_after = BookTag.objects.filter(tag_name=new_tag_name, user=self.user, book=book)
        self.assertTrue(filtered_tags_after.exists())
        self.assertEqual(filtered_tags_after.count(), 1)

        # should have removed old tag
        filtered_tags_after_2 = BookTag.objects.filter(tag_name=tag_name, user=self.user, book=book)
        self.assertFalse(filtered_tags_after_2.exists())

        # determine expected data
        expected_data = {
            'books': [{
                'id': book.id,
                'title': book.title,
                'authors': [],
                'position_in_series': None,
                'series': None,
                'tags': [new_tag_name]
            }]
        }
        self.assertEqual(response.data, expected_data)

    def test_will_remove_series_if_given_negative_one(self):
        series = Series.objects.create(
            name="Cool Series", planned_count=3, user=self.user)
        newBook = Book.objects.create(
            title="test series removing", user=self.user, series=series)

        # make the parameters
        data = {
            "series": -1
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': newBook.id})
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': newBook.id,
                'title': newBook.title,
                'authors': [],
                'position_in_series': None,
                'series': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.series, None)

    def test_will_remove_series_if_given_empty_string(self):
        series = Series.objects.create(
            name="Cool Series", planned_count=3, user=self.user)
        newBook = Book.objects.create(
            title="test series removing", user=self.user, series=series)

        # make the parameters
        data = {
            "series": ""
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': newBook.id})
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': newBook.id,
                'title': newBook.title,
                'authors': [],
                'position_in_series': None,
                'series': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.series, None)

    def test_will_remove_position_if_given_negative_one(self):
        newBook = Book.objects.create(
            title="test series removing", user=self.user)

        # make the parameters
        data = {
            "position_in_series": -1
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': newBook.id})
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': newBook.id,
                'title': newBook.title,
                'authors': [],
                'position_in_series': None,
                'series': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.position_in_series, None)

    def test_will_remove_position_if_given_empty_string(self):
        newBook = Book.objects.create(
            title="test series removing", user=self.user)

        # make the parameters
        data = {
            "position_in_series": ""
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('book', kwargs={'book_id': newBook.id})
        response = self.client.put(url, data, format='json')

        # determine expected data
        expected_data = {
            'books': [{
                'id': newBook.id,
                'title': newBook.title,
                'authors': [],
                'position_in_series': None,
                'series': None,
                'tags': []
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updated_book = Book.objects.get(id=self.book_id)
        self.assertEqual(updated_book.position_in_series, None)