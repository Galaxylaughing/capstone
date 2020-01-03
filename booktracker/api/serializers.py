# api/serializers.py
                             
from rest_framework import serializers
         
from .models import Book, BookAuthor


# class UserSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     username = serializers.CharField(max_length=100)

# class CommentSerializer(serializers.Serializer):
#     user = UserSerializer()
#     content = serializers.CharField(max_length=200)
#     created = serializers.DateTimeField()   
      
# class UserSerializer(serializers.ModelSerializer):
#     """ serializer for the User model """
#
#     """ pull hash_id field """
#     id = serializers.CharField(source='hash_id', read_only=True)
#
#     class Meta:
#         model = User
#         fields = ['id', 'username']


class BookSerializer(serializers.ModelSerializer):
    """ serializer for the Book model """

    # book_author = BookAuthorSerializer(bookauthor_set.all(), many=True)
    # print('firstbook', firstBook.bookauthor_set.all())

    # book = serializers.StringRelatedField(many=True)
    # authors = serializers.RelatedField(source='BookAuthor')

    # title = serializers.CharField(source='title')

    class Meta:
        model = Book
        fields = ['title']

class BookAuthorSerializer(serializers.ModelSerializer):
    """ serializer for the BookAuthor model """

    # books = PrimaryKeyRelatedField(queryset=Book.objects.all())
    # book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), many=True)
    book = BookSerializer()

    class Meta:
        model = BookAuthor
        fields = ['author_name', 'book']