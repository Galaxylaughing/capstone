from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Book
from .serializers import BookSerializer

from django.apps import apps
User = apps.get_model('userauth','User')


# Create your views here.
@api_view(["GET"])
def get_books(request):
    bookList = Book.objects.all()
    serializer = BookSerializer(bookList, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)