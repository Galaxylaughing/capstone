from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from .models import Book, BookAuthor, Series
from .serializers import BookSerializer, SeriesSerializer

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

        # serialize the book list
        serializer = BookSerializer(bookList, many=True)
        # add wrapper key
        json = {
            'books': serializer.data
        }

        return Response(json, status=status.HTTP_200_OK)

    elif request.method == "POST":
        if 'title' in request.data and 'author' in request.data:
            # make new book
            title = request.data['title']
            requestUser = User.objects.get(
                auth_token__key=request.auth)
            newBook = Book.objects.create(
                title=title, user=requestUser)

            # make new authors
            authors = request.POST.getlist('author')

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


@api_view(["GET", "DELETE", "PUT"])
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
        # find the user making the request
        requestUser = User.objects.get(
            auth_token__key=request.auth)
        requestUserId = requestUser.id
        # find book by ID; use .filter to avoid throwing error if not found
        filteredBook = Book.objects.filter(id=book_id)

        if filteredBook.count() > 0:
            book = filteredBook[0]
            # check that book belongs to user making the request
            if book.user.id == requestUserId:
                serializer = BookSerializer(book)
                json = {
                    "book": serializer.data
                }
                book.delete()
                return Response(json, status=status.HTTP_200_OK)
            else:
                json = {
                    "error": "Users can only delete their own books; book %s belongs to user %s" %(book.id, book.user.id)
                }
                return Response(json, status=status.HTTP_400_BAD_REQUEST)
        
        # else
        json = {
            "error": "No book found with the ID: %s" %(book_id)
        }
        return Response(json, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        # print("\nPATCHING\n", request.body)
        # print("LISTS", request.POST.lists, "\n")
        # print("TITLES", request.POST.getlist('title'), "\n")
        # print("AUTHORS", request.POST.getlist('author'), "\n")

        # find book by ID; use .filter to avoid throwing error if not found
        book = Book.objects.filter(id=book_id)[0]

        # set new title if there is one
        new_titles = request.POST.getlist('title')
        if len(new_titles) > 0:
            book.title = new_titles[0]

        # update authors if an author key is received
        if "author" in request.data:
            # check existing authors against input
            new_authors = request.POST.getlist('author')
            existing_authors = BookAuthor.objects.filter(book=book)
            for bookauthor in existing_authors:
                # check if new input contains this author name
                existing_author_name = bookauthor.author_name

                if existing_author_name in new_authors:
                    # remove this author from new_authors
                    new_authors.remove(existing_author_name)
                else:
                    # remove this bookauthor entry
                    bookauthor.delete()

            # set new authors
            for author_name in new_authors:
                BookAuthor.objects.create(
                    author_name=author_name, book=book)

        # save updated book
        book.save()

        # serialize updated book
        updated_book = Book.objects.filter(id=book_id)
        # serialize the book
        serializer = BookSerializer(updated_book[0])
        # add wrapper key
        json = {
            "books": [serializer.data]
        }
        return Response(json, status=status.HTTP_200_OK)


@api_view(["GET"])
def series(request):
    # get user from token passed into request header
    request_user = User.objects.get(auth_token__key=request.auth)

    # # find all series associated with this user
    series_list = Series.objects.filter(user=request_user)

    # TODO: remove when manual XCode testing of series endpoint is done
    if series_list.count() == 0:
        # make series:
            # no titles
        Series.objects.create(
            name="The Name of the Wind", planned_count=3, user=request_user)
            # one title
        song_of_ice_and_fire = Series.objects.create(
            name="A Song of Ice and Fire", planned_count=6, user=request_user)
            # two titles
        way_of_kings = Series.objects.create(
            name="The Stormlight Archive", planned_count=10, user=request_user)
        # give some of them books
        Book.objects.create(
            title="A Game of Thrones", user=request_user, series=song_of_ice_and_fire)
        Book.objects.create(
            title="The Way of Kings", user=request_user, series=way_of_kings)
        Book.objects.create(
            title="Words of Radiance", user=request_user, series=way_of_kings)

    # # serialize the series list
    serializer = SeriesSerializer(series_list, many=True)
    # add wrapper key
    json = {
        'series': serializer.data
    }

    return Response(json, status=status.HTTP_200_OK)
