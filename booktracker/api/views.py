from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from rest_framework.authtoken.models import Token
from .models import Book, BookAuthor #TODO: remove BookAuthor when I remove `if`
from .serializers import BookSerializer

from django.apps import apps
User = apps.get_model('userauth','User')


# Create your views here.
@api_view(["GET", "POST"])
def books(request):
    if request.method == 'GET':
        # get user from token passed into request header
        requestUser = User.objects.get(auth_token__key=request.auth)

        # find all books associated with this user
        bookList = Book.objects.filter(user=requestUser)

        # TODO: remove; used for testing XCODE
        if bookList.count() == 0:
            firstBook = Book.objects.create(
                title="Orange Book", user=requestUser)
            BookAuthor.objects.create(
                author_name="John Doe", book=firstBook)
            BookAuthor.objects.create(
                author_name="Jane Doe", book=firstBook)

            secondBook = Book.objects.create(
                title="Squash Book", user=requestUser)
            BookAuthor.objects.create(
                author_name="Jane Doe", book=secondBook)

            thirdBook = Book.objects.create(
                title="Apple Book", user=requestUser)
            BookAuthor.objects.create(
                author_name="M.K. Doe", book=thirdBook)

            # alphabetical:
            # Apple, Orange, Squash

        # serialize the book list
        serializer = BookSerializer(bookList, many=True)
        # add wrapper key
        json = {
            'books': serializer.data
        }

        return Response(json, status=status.HTTP_200_OK)

    elif request.method == "POST":
        # print("\nPOSTING\n", request.body)
        # print("LISTS", request.POST.lists, "\n")
        # print("TITLES", request.POST.getlist('title'), "\n")
        # print("AUTHORS", request.POST.getlist('author'), "\n")

        if 'title' in request.data and 'author' in request.data:
            # make new book
            title = request.data['title']
            requestUser = User.objects.get(
                auth_token__key=request.auth)
            newBook = Book.objects.create(
                title=title, user=requestUser)

            # make new authors
            authors = request.POST.getlist('author')
            # if authors == []:
            #     authors = request.data['author']

            for author in authors:
                BookAuthor.objects.create(
                    author_name=author, book=newBook)

            # create response json
            serializer = BookSerializer(newBook)
            json = {
                'books': [serializer.data]
            }

            return Response(json, status=status.HTTP_201_CREATED)
        else:
            error_message = {"error": "Invalid book parameters"}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def book(request, book_id):
    if request.method == 'GET':
        # find book by ID; use .filter to avoid throwing error if not found
        book = Book.objects.filter(id=book_id)

        if book.count() > 0:
            # serialize the book
            serializer = BookSerializer(book[0])
            # add wrapper key
            json = {}
            json["book"] = serializer.data

            return Response(json, status=status.HTTP_200_OK)
        
        # else
        json = {
            "error": "No book found with the ID: %s" %(book_id)
        }
        return Response(json, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        # find book by ID; use .filter to avoid throwing error if not found
        filteredBook = Book.objects.filter(id=book_id)

        if filteredBook.count() > 0:
            book = filteredBook[0]
            serializer = BookSerializer(book)
            json = {
                "book": serializer.data
            }
            book.delete()
            return Response(json, status=status.HTTP_200_OK)
        
        # else
        json = {
            "error": "No book found with the ID: %s" %(book_id)
        }
        return Response(json, status=status.HTTP_400_BAD_REQUEST)
