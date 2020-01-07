# api/serializers.py
                             
from rest_framework import serializers
         
from .models import Book, BookAuthor, Series


class BookAuthorSerializer(serializers.ModelSerializer):
    """ serializer for the BookAuthor model """

    book = serializers.StringRelatedField()

    class Meta:
        model = BookAuthor
        fields = ['author_name', 'book']

class BookSerializer(serializers.ModelSerializer):
    """ serializer for the Book model """

    authors = serializers.StringRelatedField(many=True)
    series = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'position_in_series', 'series']

class SeriesSerializer(serializers.ModelSerializer):
    """ serializer for the Series model """

    books = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Series
        fields = ['id', 'name', 'planned_count', 'books']
