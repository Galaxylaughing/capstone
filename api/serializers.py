# api/serializers.py
                             
from rest_framework import serializers
         
from .models import Book, BookAuthor, Series, BookTag


class BookAuthorSerializer(serializers.ModelSerializer):
    """ serializer for the BookAuthor model """

    book = serializers.StringRelatedField()

    class Meta:
        model = BookAuthor
        fields = ['author_name', 'book']

class BookTagSerializer(serializers.ModelSerializer):
    """ serializer for the BookTag model """

    book = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BookTag
        fields = ['tag_name', 'book']

class BookSerializer(serializers.ModelSerializer):
    """ serializer for the Book model """

    authors = serializers.StringRelatedField(many=True)
    series = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Book
        fields = ['id', 
        'title', 
        'authors', 
        'position_in_series', 
        'series', 
        'publisher', 
        'publication_date', 
        'isbn_10', 
        'isbn_13', 
        'page_count',
        'description',
        'current_status',
        'tags']

class SeriesSerializer(serializers.ModelSerializer):
    """ serializer for the Series model """

    books = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Series
        fields = ['id', 'name', 'planned_count', 'books']
