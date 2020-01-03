# api/serializers.py
                             
from rest_framework import serializers
         
from .models import Book, BookAuthor


class BookAuthorSerializer(serializers.ModelSerializer):
    """ serializer for the BookAuthor model """

    # books = PrimaryKeyRelatedField(queryset=Book.objects.all())
    # book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), many=True)
    # book = BookSerializer()

    class Meta:
        model = BookAuthor
        fields = ['author_name']

class BookSerializer(serializers.ModelSerializer):
    """ serializer for the Book model """

    bookauthor_set = BookAuthorSerializer(BookAuthor.objects.all(), many=True)
    # print('firstbook', firstBook.bookauthor_set.all())

    # book = serializers.StringRelatedField(many=True)
    # authors = serializers.RelatedField(source='BookAuthor')


    class Meta:
        model = Book
        fields = ['title', 'bookauthor_set']
