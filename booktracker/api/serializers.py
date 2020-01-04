# api/serializers.py
                             
from rest_framework import serializers
         
from .models import Book, BookAuthor


class BookAuthorSerializer(serializers.ModelSerializer):
    """ serializer for the BookAuthor model """

    book = serializers.StringRelatedField()

    class Meta:
        model = BookAuthor
        fields = ['author_name', 'book']

class BookSerializer(serializers.ModelSerializer):
    """ serializer for the Book model """

    authors = serializers.StringRelatedField(many=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors']
