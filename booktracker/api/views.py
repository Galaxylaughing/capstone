from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from .models import Book
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

    # allBooks = Book.objects.all()
    serializer = BookSerializer(bookList, many=True)
    # [
    #   {
    #       'title': 'First Book',
    #       'authors': [
    #           'Jane Doe',
    #           'John Doe'
    #       ]
    #   }, 
    #   {
    #       'title': 'Second Book',
    #       'authors': [
    #           'Jane Doe'
    #       ]
    #   }
    # ]

    return Response(serializer.data, status=status.HTTP_200_OK)