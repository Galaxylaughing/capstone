from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from django.utils import timezone
import datetime
import pytz

from rest_framework.authtoken.models import Token
from .models import Book, BookAuthor, Series, BookTag, BookStatus
from .serializers import BookSerializer, SeriesSerializer, BookTagSerializer, BookStatusSerializer

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
            requestUser = User.objects.get(
                auth_token__key=request.auth)
            title = request.data['title']
            authors = request.data['authors']
                        
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

            if 'publisher' in request.data:
                publisher = request.data['publisher']
            else:
                publisher = None

            if 'publication_date' in request.data:
                publication_date = request.data['publication_date']
            else:
                publication_date = None

            if 'isbn_10' in request.data:
                isbn_10 = request.data['isbn_10']
            else:
                isbn_10 = None
            if 'isbn_13' in request.data:
                isbn_13 = request.data['isbn_13']
            else:
                isbn_13 = None

            if 'page_count' in request.data:
                page_count = request.data['page_count']
            else:
                page_count = None
            if 'description' in request.data:
                description = request.data['description']
            else:
                description = None

            # make new book
            newBook = Book.objects.create(
                title=title, 
                user=requestUser, 
                position_in_series=position, 
                series=series,
                publisher=publisher,
                publication_date=publication_date,
                isbn_10=isbn_10,
                isbn_13=isbn_13,
                page_count=page_count,
                description=description)

            # make new authors
            for author in authors:
                BookAuthor.objects.create(
                    author_name=author, user=requestUser, book=newBook)

            if 'tags' in request.data:
                # make new tags
                tags = request.data['tags']
                for tag in tags:
                    BookTag.objects.create(
                        tag_name=tag, book=newBook, user=requestUser)

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
        request_user = User.objects.get(auth_token__key=request.auth)
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
                        author_name=author_name, user=request_user, book=book)

            # update tags if an tag key is received
            if "tags" in request.data:
                recieved_tags = request.data['tags']

                # remove any duplicates from input
                new_tags = []
                for tag in recieved_tags:
                    if tag not in new_tags:
                        new_tags.append(tag)

                # check existing tags against input
                existing_tags = BookTag.objects.filter(book=book, user=request_user)
                for booktag in existing_tags:
                    # check if new input contains this tag name
                    existing_tag = booktag.tag_name

                    if existing_tag in new_tags:
                        # remove this tag from new_tags
                        new_tags.remove(existing_tag)
                    else:
                        # remove this booktag entry
                        booktag.delete()

                # set new tags
                for booktag in new_tags:
                    BookTag.objects.create(
                        tag_name=booktag, user=request_user, book=book)

            # update series info if given any
            if 'position_in_series' in request.data:
                position_in_series = request.data['position_in_series']
                if position_in_series == -1 or position_in_series == "":
                    book.position_in_series = None
                else:
                    book.position_in_series = position_in_series
            if 'series' in request.data:
                series_id = request.data['series']
                if series_id == -1 or series_id == "":
                    book.series = None
                else:
                    series = Series.objects.get(id=series_id)
                    book.series = series

            if 'publisher' in request.data:
                book.publisher = request.data['publisher']
            if 'publication_date' in request.data:
                book.publication_date = request.data['publication_date']

            if 'isbn_10' in request.data:
                book.isbn_10 = request.data['isbn_10']
            if 'isbn_13' in request.data:
                book.isbn_13 = request.data['isbn_13']

            if 'page_count' in request.data:
                page_count = request.data['page_count']
                if page_count == -1 or page_count == "":
                    book.page_count = None
                else:
                    book.page_count = page_count

            if 'description' in request.data:
                book.description = request.data['description']

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
                if tag.book.id not in collected_tags[tag.tag_name]:
                    collected_tags[tag.tag_name].append(tag.book.id)
            else:
                collected_tags[tag.tag_name] = [tag.book.id]

        # organize into objects like
        # { 'name': tag_name, 'books': [...] }
        tag_list = []
        for tag_name in collected_tags:
            new_tag = {
                "tag_name": tag_name,
                "books": collected_tags[tag_name]
            }
            tag_list.append(new_tag)

        # add wrapper
        json = {
            "tags": tag_list
        }

        return Response(json, status=status.HTTP_200_OK)

@api_view(["PUT", "DELETE"])
def tag(request, tag_name):
    if request.method == "PUT":
        if 'new_name' in request.data and 'books' in request.data:
            new_name = request.data['new_name']
            new_books = request.data['books']
            request_user = User.objects.get(auth_token__key=request.auth)

            # find all occurrences of the provided tag name in the database
            matching_tags = BookTag.objects.filter(tag_name=tag_name, user=request_user)
            if matching_tags.count() > 0:
                if len(new_books) > 0:
                    updated_tag = {
                        "tag_name": new_name,
                        "books": []
                    }

                    for book_id in new_books:
                        matching_books = Book.objects.filter(id=book_id)
                        # if there's a matching book
                        if matching_books.count() > 0:
                            matching_book = matching_books[0]
                            matching_booktags = BookTag.objects.filter(tag_name=tag_name, user=request_user, book=matching_book)
                            # if there's an existing booktag for it
                            if matching_booktags.count() > 0:
                                matching_booktag = matching_booktags[0]
                                matching_booktag.tag_name = new_name
                                matching_booktag.save()
                                updated_tag["books"].append(matching_book.id)
                            # if there isn't an existing booktag
                            else:
                                new_booktag = BookTag.objects.create(tag_name=new_name, user=request_user, book=matching_book)
                                updated_tag["books"].append(matching_book.id)
                        # if there isn't a matching book
                        else:
                            error_message = { "error": "Could not find book with ID: %s" %(book_id) }
                            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
                        
                    for matching_tag in matching_tags:
                        # if that tag's book id is not also in new_books
                        if matching_tag.book.id not in new_books:
                            matching_tag.delete()

                    # add wrapper
                    json = {
                        "tags": [updated_tag]
                    }
                    return Response(json, status=status.HTTP_200_OK)
                # if new book list is empty, delete the tag instances
                else:
                    # serialize tags to be deleted
                    serializer = BookTagSerializer(matching_tags, many=True)
                    json = {
                        "tags": serializer.data
                    }
                    for tag in matching_tags:
                        tag.delete()
                    return Response(json, status=status.HTTP_200_OK)
            else:
                error_message = {
                    "error": "No tags match the name '%s'" %(tag_name)
                }
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_message = {
                "error": "new name or list of books was not provided"
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        request_user = User.objects.get(auth_token__key=request.auth)

        # find all occurrences of the provided tag name in the database
        matching_tags = BookTag.objects.filter(tag_name=tag_name, user=request_user)

        if matching_tags.count() > 0:
            # serialize tags to be deleted
            serializer = BookTagSerializer(matching_tags, many=True)
            json = {
                "tags": serializer.data
            }

            # for each matching tag, delete that tag
            for tag in matching_tags:
                tag.delete()

            return Response(json, status=status.HTTP_200_OK)
        else:
            error_message = {
                "error": "Could not find any tags matching the name '%s'" %(tag_name)
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST", "DELETE"])
def bookstatus(request, id):
    if request.method == "GET":
        book_id = id
        request_user = User.objects.get(auth_token__key=request.auth)
        matching_books = Book.objects.filter(user=request_user, id=book_id)
        
        if matching_books.count() > 0:
            matching_book = matching_books[0]
            matching_bookstatuses = BookStatus.objects.filter(user=request_user, book=matching_book)
            serializer = BookStatusSerializer(matching_bookstatuses, many=True)
            json = {
                'status_history': serializer.data
            }
            return Response(json, status=status.HTTP_200_OK)
        else:
            error_message = {
                "error": "Could not find book with ID: %s" %(book_id)
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "POST":
        book_id = id
        request_user = User.objects.get(auth_token__key=request.auth)
        matching_books = Book.objects.filter(user=request_user, id=book_id)

        if matching_books.count() > 0:
            matching_book = matching_books[0]

            if "status_code" in request.data and "date" in request.data:
                status_code = request.data["status_code"]
                date = request.data["date"]

                # from https://www.geeksforgeeks.org/python-check-if-element-is-present-in-tuple-of-tuples/
                if (any(status_code in i for i in Book.STATUS_CHOICES)):
                    try:
                        new_status = BookStatus.objects.create(
                            status_code=status_code,
                            date=date,
                            user=request_user,
                            book=matching_book)
                    except ValidationError as error:
                        error_message = {
                            "error": error.messages,
                        }
                        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

                    # update book's current status
                    matching_book.current_status = status_code
                    matching_book.current_status_date = date
                    matching_book.save()

                    serializer = BookStatusSerializer(new_status)
                    json = {
                        "status": serializer.data
                    }
                    return Response(json, status=status.HTTP_201_CREATED)
                else:
                    error_message = {
                        "error": "Invalid status code"
                    }
                    return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
            else:
                error_message = {
                    "error": "Invalid status parameters"
                }
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_message = {
                "error": "Could not find book with ID: %s" %(book_id)
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "DELETE":
        status_id = id
        request_user = User.objects.get(auth_token__key=request.auth)
        matching_statuses = BookStatus.objects.filter(id=status_id, user=request_user)

        if matching_statuses.count() > 0:
            matching_status = matching_statuses[0]

            serializer = BookStatusSerializer(matching_status)
            json = {
                "status": serializer.data
            }

            matching_status.delete()

            return Response(json, status=status.HTTP_200_OK)

        else:
            error_message = {
                "error": "Could not find status with ID: %s" %(status_id)
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)