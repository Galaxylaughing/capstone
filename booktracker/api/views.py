from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from .models import Book, BookAuthor #TODO: remove BookAuthor when I remove `if`
from .serializers import BookSerializer

from django.apps import apps
User = apps.get_model('userauth','User')


# Create your views here.
@api_view(["GET"])
def get_books(request):
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
    json = {}
    json["books"] = serializer.data

    return Response(json, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_book(request, book_id):
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
    json = {}
    json["error"] = "No book found with the ID: %s" %(book_id)
    return Response(json, status=status.HTTP_400_BAD_REQUEST)