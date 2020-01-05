from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest import skip


# Create your tests here.
from .models import Book, BookAuthor
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
            author_name="First Last", book=self.book)
        filteredBookAuthors = BookAuthor.objects.filter(
            author_name="First Last")

        self.assertEqual(BookAuthor.objects.count(), expectedCount)
        self.assertTrue(filteredBookAuthors.exists())

    def test_bookauthor_str_method(self):
        author_name = "M.K. Author"

        book_author = BookAuthor.objects.create(
            author_name=author_name, book=self.book)
        
        self.assertEqual(str(book_author), author_name)


class SerializerTests(TestCase):
    """ test module for BookSerializer """

    def setUp(self):
        self.user = User.objects.create(
            username='Bertie', password='password')

        self.firstBook = Book.objects.create(
            title="First Book", user=self.user)
        self.secondBook = Book.objects.create(
            title="Second Book", user=self.user)

        BookAuthor.objects.create(
            author_name="John Doe", book=self.firstBook)
        BookAuthor.objects.create(
            author_name='Jane Doe', book=self.firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", book=self.secondBook)

    def test_bookserializer_returns_expected_data(self):
        firstId = self.firstBook.id
        secondId = self.secondBook.id
        expected_data = [
            {
                'id': firstId,
                'title': 'First Book',
                'authors': [
                    'Jane Doe',
                    'John Doe'
                ]
            }, 
            {
                'id': secondId,
                'title': 'Second Book',
                'authors': [
                    'Jane Doe'
                ]
            }
        ]

        bookList = Book.objects.all()
        serializer = BookSerializer(bookList, many=True)

        self.assertEqual(serializer.data, expected_data)

    def test_bookauthorserializer_returns_expected_data(self):
        expected_data = [
            { 
                'author_name': 'John Doe',
                'book': 'First Book'
            },
            {
                'author_name': 'Jane Doe',
                'book': 'First Book'
            },
            { 
                'author_name': 'Jane Doe',
                'book': 'Second Book'
            }
        ]

        bookauthorList = BookAuthor.objects.all()
        serializer = BookAuthorSerializer(bookauthorList, many=True)

        self.assertEqual(serializer.data, expected_data)


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
        firstBook = Book.objects.create(
            title="First Book", user=self.user)
        secondBook = Book.objects.create(
            title="Second Book", user=self.user)

        # give the books some authors
        BookAuthor.objects.create(
            author_name="John Doe", book=firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", book=firstBook)
        BookAuthor.objects.create(
            author_name="Jane Doe", book=secondBook)

        firstId = firstBook.id
        secondId = secondBook.id
        expected_data = {
            'books': [
                {
                    'id': secondId,
                    'title': 'Second Book',
                    'authors': [
                        'Jane Doe'
                    ]
                },
                {
                    'id': firstId,
                    'title': 'First Book',
                    'authors': [
                        'Jane Doe', 
                        'John Doe'
                    ]
                }
            ]
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    @skip("TODO: unskip me again when XCode hand-testing done")
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
        # create a new user
        newUser = User.objects.create(
            username='Caspar', password='password')
        # get the user's token
        newUserToken = str(newUser.auth_token)

        # give the new user a book
        firstBook = Book.objects.create(
            title="First Book", user=newUser)
        BookAuthor.objects.create(
            author_name="Jane Doe", book=firstBook)

        # give the setup user a book
        secondBook = Book.objects.create(
            title="Second Book", user=self.user)
        BookAuthor.objects.create(
            author_name="John Doe", book=secondBook)

        firstId = firstBook.id
        expected_data = {
            "books": [
                {
                    'id': firstId,
                    'title': 'First Book',
                    'authors': [
                        'Jane Doe'
                    ]
                }
            ]
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + newUserToken)
        # get the API response
        url = reverse('books')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)


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
        firstBook = Book.objects.create(
            title="First Book", user=self.user)
        # give the book an author
        BookAuthor.objects.create(
            author_name="Jane Doe", book=firstBook)

        firstId = firstBook.id
        expected_data = {
            'book': {
                'id': firstId,
                'title': 'First Book',
                'authors': [
                    'Jane Doe'
                ]
            }
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': firstId})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
            author_name="Jane Doe", book=firstBook)

        firstId = firstBook.id
        
        # DON'T add token to header
        # get the API response
        url = reverse('book', kwargs={'book_id': firstId})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostBookTest(APITestCase):
    """ Test module for posting a book to the database """

    def setUp(self):
        # create a user
        username = 'Bertie'
        password = 'password'
        self.user = User.objects.create(
            username=username, password=password)
        # get the user's token
        self.token = str(self.user.auth_token)

    def test_can_add_a_valid_book(self):
        # make some post parameters
        title = 'New Book With Unique Title'
        data = f'title={title}&author=New Author&author=Other Author'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('books')
        # make request
        response = self.client.post(url, data, content_type='application/x-www-form-urlencoded')

        # find book in database
        newBook = Book.objects.get(title=title)
        # grab id
        newBookId = newBook.id
        # determine expected data
        expected_data = {
            'books': [{
                'id': newBookId,
                'title': title,
                'authors': [
                    'Other Author',
                    'New Author'
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)

    def test_cannot_add_a_book_without_authentication(self):
        # make some post parameters
        title = 'New Book With Unique Title'
        data = f'title={title}&author=New Author&author=Other Author'

        # DON'T request header
        # get url
        url = reverse('books')
        # make request
        response = self.client.post(url, data, content_type='application/x-www-form-urlencoded')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_cannot_add_invalid_book(self):
        # make some invalid post parameters
        data = f'author=New Author&author=Other Author'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('books')
        # make request
        response = self.client.post(url, data, content_type='application/x-www-form-urlencoded')

        expected_error = {
            "error": "Invalid book parameters"
        }
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)


class DeleteBookTests(APITestCase):
    """ test module for deleting a book """

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
        self.firstBook = Book.objects.create(
            title=self.title, user=self.user)
        # give the book an author
        self.author = "Jane Doe"
        BookAuthor.objects.create(
            author_name=self.author, book=self.firstBook)

    def test_can_delete_a_book(self):
        firstId = self.firstBook.id
        firstTitle = self.title
        firstAuthor = self.author
        expected_data = {
            'book': {
                'id': firstId,
                'title': firstTitle,
                'authors': [
                    firstAuthor
                ]
            }
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': firstId})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # check that I can't find it in database
        filteredBooks = Book.objects.filter(id=firstId)
        self.assertEqual(filteredBooks.count(), 0)

    def test_returns_error_if_invalid_bookid(self):
        fakeId = 999
        expected_data = {
            "error": "No book found with the ID: %s" %(fakeId)
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': fakeId})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_deletion_of_an_authors_only_book_deletes_author(self):
        # create new book
        title = "Unique Book"
        uniqueBook = Book.objects.create(
            title=title, user=self.user)
        uniqueBookId = uniqueBook.id
        # give the book an author
        uniqueAuthor = "Unique Author"
        uniqueBookAuthor = BookAuthor.objects.create(
            author_name=uniqueAuthor, book=uniqueBook)
        uniqueAuthorId = uniqueBookAuthor.id

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': uniqueBookId})
        response = self.client.delete(url, format='json')

        # check that I can't find the book in database
        filteredBooks = Book.objects.filter(id=uniqueBookId)
        self.assertEqual(filteredBooks.count(), 0)

        # check that I can't find the author in database
        filteredAuthors = BookAuthor.objects.filter(id=uniqueAuthorId)
        self.assertEqual(filteredAuthors.count(), 0)

    def test_user_cannot_delete_other_users_book(self):
        newUser = User.objects.create(
        username="New User", password="password")
        # give the user a book
        otherBook = Book.objects.create(
            title="Other User's Book", user=newUser)

        otherId = otherBook.id
        expected_data = {
            "error": "Users can only delete their own books; book %s belongs to user %s" %(otherId, newUser.id)
        }

        # add token to header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get the API response
        url = reverse('book', kwargs={'book_id': otherId})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)


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
        self.firstBook = Book.objects.create(
            title=self.title, user=self.user)
        self.book_id = self.firstBook.id
        # give the book two authors
        self.authorOne = "Jane Doe"
        BookAuthor.objects.create(
            author_name=self.authorOne, book=self.firstBook)
        self.authorTwo = "John Doe"
        BookAuthor.objects.create(
            author_name=self.authorTwo, book=self.firstBook)

    def test_can_update_with_all_fields_changed(self):
        """ if given all fields, and all are new, can update book """

        # make the parameters
        newTitle = 'New Book With Unique Title'
        data = f'title={newTitle}&author=New Author&author=Other Author'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, content_type='application/x-www-form-urlencoded')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': newTitle,
                'authors': [
                    'Other Author',
                    'New Author'
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updatedBook = Book.objects.get(id=self.book_id)
        self.assertEqual(updatedBook.title, newTitle)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updatedBook)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue("New Author" in author_values)
        self.assertTrue("Other Author" in author_values)

    def test_can_update_with_only_some_fields_changed(self):
        """ if given all fields, but only some are new, can update book """

        # make the parameters
        newTitle = 'New Book With Unique Title'
        authorOne = self.authorOne
        authorTwo = self.authorTwo
        data = f'title={newTitle}&author={authorOne}&author={authorTwo}'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, content_type='application/x-www-form-urlencoded')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': newTitle,
                'authors': [
                    authorTwo,
                    authorOne
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updatedBook = Book.objects.get(id=self.book_id)
        self.assertEqual(updatedBook.title, newTitle)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updatedBook)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(authorOne in author_values)
        self.assertTrue(authorTwo in author_values)

    def test_can_update_with_only_new_authors_provided(self):
        """ if given only the author field, and it is new, can update book """

        # make the parameters
        # not changing title
        authorOne = self.authorOne
        authorTwo = self.authorTwo
        data = f'author={authorOne}&author={authorTwo}'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, content_type='application/x-www-form-urlencoded')

        # determine expected data
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': self.title,
                'authors': [
                    authorTwo,
                    authorOne
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updatedBook = Book.objects.get(id=self.book_id)
        self.assertEqual(updatedBook.title, self.title)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updatedBook)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(authorOne in author_values)
        self.assertTrue(authorTwo in author_values)

    def test_can_update_with_only_new_title_provided(self):
        """ if given only the title field, and it is new, can update book """

        # make the parameters
        newTitle = 'New Book With Unique Title'
        data = f'title={newTitle}'

        # set request header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # get url
        url = reverse('book', kwargs={'book_id': self.book_id})
        # make request
        response = self.client.put(url, data, content_type='application/x-www-form-urlencoded')

        # determine expected data
        authorOne = self.authorOne
        authorTwo = self.authorTwo
        expected_data = {
            'books': [{
                'id': self.book_id,
                'title': newTitle,
                'authors': [
                    authorTwo,
                    authorOne
                ]
            }]
        }
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        # find book in database
        updatedBook = Book.objects.get(id=self.book_id)
        self.assertEqual(updatedBook.title, newTitle)

        # find authors of this book
        authors = BookAuthor.objects.filter(book=updatedBook)
        author_values = authors.values_list('author_name', flat=True)
        
        self.assertEqual(authors.count(), 2)
        self.assertTrue(authorOne in author_values)
        self.assertTrue(authorTwo in author_values)
