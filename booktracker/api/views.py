from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from .models import Book, BookAuthor, Series, BookTag
from .serializers import BookSerializer, SeriesSerializer, BookTagSerializer

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
        # print("\nPOSTING\n", request.body)

        if 'title' in request.data and 'authors' in request.data:
            # make new book
            title = request.data['title']
            requestUser = User.objects.get(
                auth_token__key=request.auth)

            if 'position_in_series' in request.data:
                position = request.data['position_in_series']
            else:
                position = None

            if 'series' in request.data:
                # find series by id
                series_id = request.data['series']
                series = Series.objects.get(id=series_id)
            else:
                series = None

            newBook = Book.objects.create(
                title=title, user=requestUser, position_in_series=position, series=series)

            # make new authors
            authors = request.data['authors']

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
        book_results = Book.objects.filter(id=book_id)

        if book_results.count() > 0:
            book = book_results[0]
            request_user = User.objects.get(auth_token__key=request.auth)

            if book.user.id == request_user.id:
                serializer = BookSerializer(book)
                json = {
                    "book": serializer.data
                }

                return Response(json, status=status.HTTP_200_OK)
            else:
                error_message = {
                    "error": "unauthorized"
                }
                return Response(error_message, status=status.HTTP_401_UNAUTHORIZED)
        
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
            "error": "Could not find book with ID: %s" %(book_id)
        }
        return Response(json, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        # print("\nPUTTING\n", request.body)
        filtered_books = Book.objects.filter(id=book_id)

        if len(filtered_books) > 0:
            book = filtered_books[0]

            # set new title if there is one
            if 'title' in request.data:
                new_title = request.data['title']
                book.title = new_title

            # update authors if an author key is received
            if "authors" in request.data:
                # check existing authors against input
                new_authors = request.data['authors']
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

            # update series info if given any
            if 'position_in_series' in request.data:
                book.position_in_series = request.data['position_in_series']
            if 'series' in request.data:
                series_id = request.data['series']
                series = Series.objects.get(id=series_id)
                book.series = series

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
        else:
            error_message = {
                "error": "Could not find book with ID: %s" %(book_id)
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def all_series(request):
    if request.method == "GET":
        # get user from token passed into request header
        request_user = User.objects.get(auth_token__key=request.auth)

        # # find all series associated with this user
        series_list = Series.objects.filter(user=request_user)

        # # serialize the series list
        serializer = SeriesSerializer(series_list, many=True)
        # add wrapper key
        json = {
            'series': serializer.data
        }

        return Response(json, status=status.HTTP_200_OK)

    elif request.method == "POST":
        # print("\nPOSTING\n", request.body)

        if 'name' in request.data and 'planned_count' in request.data:
            # make new series
            name = request.data['name']
            planned_count = request.data['planned_count']
            request_user = User.objects.get(auth_token__key=request.auth)
            new_series = Series.objects.create(
                name=name, planned_count=planned_count, user=request_user)
            
            # create response json
            serializer = SeriesSerializer(new_series)
            json = {
                "series": [serializer.data]
            }

            return Response(json, status=status.HTTP_201_CREATED)
        else:
            error_message = {"error": "Invalid series parameters"}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
def one_series(request, series_id):
    if request.method == "DELETE":
        filtered_series = Series.objects.filter(id=series_id)

        if len(filtered_series) > 0:
            series = filtered_series[0]

            # check that series belongs to user making the request
            requestUser = User.objects.get(auth_token__key=request.auth)
            if series.user.id == requestUser.id:
                serializer = SeriesSerializer(series)
                json = {
                    "series": serializer.data
                }

                series.delete()

                return Response(json, status=status.HTTP_200_OK)
            else:
                error_message = {
                    "error": "Users can only delete their own series; series %s belongs to user %s" %(series.id, series.user.id)
                }
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_message = {
                "error": "Could not find series with ID: %s" %(series_id)
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        # find the series by id
        filtered_series = Series.objects.filter(id=series_id)

        if len(filtered_series) > 0:
            series = filtered_series[0]

            # update series info if given any
            if 'name' in request.data:
                series.name = request.data['name']
            if 'planned_count' in request.data:
                series.planned_count = request.data['planned_count']

            # save updated series
            series.save()

            # serialize updated series
            updated_series = Series.objects.filter(id=series_id)[0]
            serializer = SeriesSerializer(updated_series)
            # add wrapper key
            json = {
                "series": [serializer.data]
            }

            return Response(json, status=status.HTTP_200_OK)
        else:
            error_message = {
                "error": "Could not find series with ID: %s" %(series_id)
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def tags(request):
    if request.method == "GET":
        request_user = User.objects.get(auth_token__key=request.auth)

        booktag_list = BookTag.objects.filter(user=request_user)
        # organize into list like
        # { 'tag_name': [...book_ids...] }
        collected_tags = {}
        for tag in booktag_list:
            if tag.tag_name in collected_tags:
                collected_tags[tag.tag_name].append(tag.book.id)
            else:
                collected_tags[tag.tag_name] = [tag.book.id]

        # organize into objects like
        # { 'name': tag_name, 'books': [...] }
        tag_list = []
        for tag_name in collected_tags:
            new_tag = {
                "name": tag_name,
                "books": collected_tags[tag_name]
            }
            tag_list.append(new_tag)

        # add wrapper
        json = {
            "tags": tag_list
        }

        return Response(json, status=status.HTTP_200_OK)

# @api_view(["GET"])
# def tag(request, tag_id):
    # if request.method == "GET":
    #     booktag_results = BookTag.objects.filter(id=tag_id)
    #     if booktag_results.count() > 0:
    #         booktag = booktag_results[0]

    #         request_user = User.objects.get(auth_token__key=request.auth)
    #         if booktag.user.id == request_user.id:
    #             serializer = BookTagSerializer(booktag)
    #             json = {
    #                 "tag": serializer.data
    #             }

    #             return Response(json, status=status.HTTP_200_OK)
    #         else:
    #             error_message = {
    #                 "error": "unauthorized"
    #             }
    #             return Response(error_message, status=status.HTTP_401_UNAUTHORIZED)
    #     else:
    #         error_message = {
    #             "error": "Could not find tag with ID: %s" %(tag_id)
    #         }
    #         return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
