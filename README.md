# capstone-api

# Project Overview

This is the back-end of my capstone project, the details of which can be found [here](https://gist.github.com/Galaxylaughing/52fbe0aea39b01cd202cfce2dd982ae5). 
The front-end can be found [here](https://github.com/Galaxylaughing/capstone-ios).

# Installation

## The Python Environment

You should initiate a new environment for the project, using something like `python -m venv env` to create the environment and `source env/bin/activate` to start it. You can deactivate this environment with `deactivate`.

## Dependencies

The dependencies for this project are listed in `requirements.txt`. They are as follows:

* asgiref==3.2.3
* dj-database-url==0.5.0
* Django==3.0.1
* djangorestframework==3.11.0
* gunicorn==20.0.4
* psycopg2==2.8.4
* python-dotenv==0.10.3
* pytz==2019.3
* sqlparse==0.3.0

Additionally, this project uses python 3 and may not run as expected with python 2.

You can install these with `$ pip install requirements.txt`.

### Installing the Dependencies

#### Django and Django REST Framework

Inside the environment, you will need to install Django and the Djano REST Framework:

* `$ pip install django`
* `$ pip install djangorestframework`

#### The .env File

Run `$ pip install python-dotenv`. The package details are [here](https://pypi.org/project/python-dotenv/). A brief description of its use is [here](https://preslav.me/2019/01/09/dotenv-files-python/).

Add a .env file to your root directory and include the following keys:

```
SECRET_KEY=<secret_key>

DATABASE_NAME=<database_name>
DATABASE_USER=<username>
DATABASE_PASS=<password>

ENVIRONMENT=PROD # or TEST if not in production
```

See the section on PostgresQL for information about the `DATABASE_...` keys.

Once you have dotenv installed, add these lines to the top of the project (booktracker)'s `settings.py` file:

```
from dotenv import load_dotenv
load_dotenv()
```

Rememebr to add the .env file to your .gitignore.

#### PostgresQL

If you wish to run this app with a local database, you will also need set up Django to run with PostgresQL.

##### The PostgresQL Database Adapter

You will need to install the PostgresQL database adapter, psycopg2, using:
* `$ pip install psycopg2`

If this fails, you may need to run `$ export LIBRARY_PATH=/usr/local/Cellar/openssl/1.0.2s/lib` and run `pip install psycopg2` again.

##### The PostgresQL Database

Then, you need a database. You can use `$ createdb <database_name>` or the psql command line shell. 
If you get an error like `psql: FATAL:  database "<username>" does not exist`, run `$ createdb`.

Once the database exists, open the psql shell with `$ psql`, select the newly-created database with `\c <database_name>`, and execute these commands:
* `CREATE ROLE <username> WITH LOGIN PASSWORD '<password>';`
* `GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <username>;`
* `ALTER USER <uername> CREATEDB;`

Remember to add your username, password, and database name to your .env file.

##### Django's Connection to the PostgresQL Database

Inside the project (booktracker)'s `settings.py` file, you will see a section like so:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("DATABASE_NAME"),
        'USER': os.environ.get("DATABASE_USER"),
        'PASSWORD': os.environ.get("DATABASE_USER"),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

If your .env file is set up, you have nothing more to do. Otherwise, enter your database name, username, and password here.

#### Other dependencies.

* [gunicorn](https://pypi.org/project/gunicorn/) can be installed with `$ pip install gunicorn`.
* [dj-database-url](https://pypi.org/project/dj-database-url/) can be installed with `$ pip install dj-database-url`.

If any other of the packages listed in requirements.txt were not installed when you installed Django and the Django REST Framework, go ahead and install them similarly.

### Migrations

You will need to remember to run the migrations.

* check migrations
  * `$ python manage.py check`
  * `$ python manage.py showmigrations`
* run migrations
  * `$ python manage.py migrate`

### Linting Errors in VSCode

If you use VSCode and your linter insists you have unresolved imports, you may need to add:

```json
{
    "python.pythonPath": "/path/to/your/venv/bin/python",
}
```

to your VSCode workplace settings, as per [this stackoverflow answer](https://stackoverflow.com/questions/53939751/pylint-unresolved-import-error-in-visual-studio-code).

# Running the API

This API is deployed to Heroku [here](booktrackerapi.herokuapp.com/). 
There is no root path url set up, so you should see a "Not Found" page at this link. 
The endpoints for the API and their use are described below in the section "Using the API".

To run the API off your local database, set up above, 
you can use the command `$ manage.py runserver` or `$ python manage.py runserver`.

This command optionally takes a url to run on. To run on your local wifi, if you are working on a Mac, click on the wifi icon in your nav bar and click "Open Network Preferences" (the last menu choice). This should open System Preferences to your Network prefences.

If you are connected to wifi, you will see a section "status: Connected" followed by a details about the network you are currently connected to, such as:

```
Wi-Fi is connected to ada-seattle and has the IP address 172.24.48.78.
```

Copy this IP address and append `<IP_address>:8000` to the `runserver` command, like so: `$ manage.py runserver 172.24.48.78:8000`. This will run the API locally at this address. 

Running the API on your local wifi will allow you to run the [LibAwesome](https://github.com/Galaxylaughing/capstone-ios) iOS app on your physical iOS device and still connect to your local database. Otherwise, you can only run the local database through the simulator on your MacOS machine.

In order to complete this local-database-wifi setup, you must add the address your constructed to the XCode project. You can refer to the more verbose instructions in the [LibAwesome](https://github.com/Galaxylaughing/capstone-ios) README or the more concise instructions here:

* open the XCode project
* open the Constants.swift file
* You will see a section with the title "API URLS". One of these looks like this: `let API_HOST = "https://booktrackerapi.herokuapp.com/"`. Comment out this line and add `let API_HOST = "http://<your_IP_address>:8000/"` instead. Comment out your added line and un-comment the original to switch back to using Heroku.

# Using the API

The booktracker API offers the following endpoints:

| endpoint              | HTTP method       | app      | associated view method |
| --------------------- | ----------------- | -------- | ---------------------- |
| `helloworld/`         | GET               | userauth | views.helloworld       |
| `signup/`             | POST              | userauth | views.signup           |
| `auth-token/`         | --                | userauth | --                     |
| `books/`              | GET, POST         | api      | views.books            |
| `books/<book_id>/`    | GET, PUT, DELETE  | api      | views.book             |
| `series/`             | GET, POST         | api      | views.all_series       |
| `series/<series_id>/` | PUT, DELETE       | api      | views.one_series       |
| `tags/`               | GET               | api      | views.tags             |
| `tags/<tag_name>/`    | PUT, DELETE       | api      | views.tag              |
| `status/<id>/`        | GET, POST, DELETE | api      | views.bookstatus       |
| `rating/<book_id>/`   | PUT               | api      | views.rating           |

Bear in mind, every endpoint requires a final slash. 
In other words, `books/<book_id>/` will work but `books/book_id` will not.

## Token Authentication and the `signup` and `auth-token` endpoints

With the exception of the `helloworld/` endpoint and the `signup/` endpoint, all of the API's endpoints require token authentication. This section will describe the associated endpoints and how the authentication flow works.

### `signup/`

To obtain a token, a user needs to use the signup/ endpoint to create a User instance in the database. 
This endpoint takes a JSON hash with two keys, a username and a password.

```python
{
  'username': 'example username',
  'password': 'example password'
}
```

In the case of a successful response, the endpoint will return a response code of 201 CREATED and a hash of the username and generated user id.

There are various error codes that may be returned in the case of an unsuccessful response:

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 403 FORBIDDEN | `Account already exists` | if the username is already associated with a user |
| 400 BAD REQUEST | `Error: username is missing or empty` | if the username key is blank or null |
|  | `Error: password is missing or empty` | if the password key is blank or null |
|  | `Errors: username is missing or empty, password is missing or empty` | if both username and password are blank or null |

### `auth-token/`

This endpoint takes a username and password, like the signup/ endpoint. 
Instead of creating a User, this endpoint assigns them a token, which it returns if successful.

This endpoint is thus effectively the login endpoint. 
The token can be cached for the duration of a customer's session and deleted when they logout. 
This API does not have a dedicated logout/ url; 
the service using this API must delete the cached token to simulate logging out. 

Once the user has recieved a token, it can be passed in to the authenticated API endpoints. This is done by adding a header field with the key `Authorization` and the value `Token <token>`. The word "Token" followed by a space (followed by the recieved token) is required.

## `books/` endpoint

This endpoint can be accessed with two methods, GET and POST.

### GET `books/`

This endpoint takes a user's token and returns a list of book instances associated with that user.

#### Success

This data is returned in the following format:

```json
{
  "books": [
    {
      "id": "<id>",
      "title": "<title>",
      "authors": [
          "<author_name>",
          "<author_name>"
      ],
      //...
    },
    {
      //...
    }
  ]
}
```

A valid book will always have at least this information. Books may additionally have:

* 'series' (the ID of a series instance in the database), Integer,
* 'position_in_series', Integer,
* 'publisher', String,
* 'publication_date', String,
* 'isbn_10', String,
* 'isbn_13', String,
* 'page_count', Integer,
* 'description', String,
* 'rating', Integer,
* 'current_status', (the code associated with a Status enum), String,
* 'current_status_date', Datetime,
* 'tags', Array of Strings

This endpoint will return:

```json
{
  "books": [] 
}
```

if there are no books associated with the given user.

If given authors that don't yet exist, this operation will create new author instances.

#### Failure

If no token is given, the endpoint will return 401 UNAUTHORIZED.

### POST `books/`

This endpoint takes a user's token and a JSON hash of all the data necessary to create a book instance in the database.

At minimum, the endpoint requires a title and an array of author names.

```json
{
  "title": "<title>",
  "authors": [
    "<author_name>"
  ]
}
```

The endpoint can also be given:

* key: "tags", value: array of strings representing tag names,
* key: "series", value: integer representing the id of an existing series,
* key: "position_in_series", value: integer representing the position in the series the this book holds,
* key: "publisher", value: a String representing the name of the publishing company,
* key: "publication_date", value: a String representing the date of the publication,
* key: "isbn_10", value: a String representing an ISBN-10,
* key: "isbn_13", value: a String representing an ISBN-13,
* key: "page_count", value: an Integer
* key: "description", value: a String

#### Success

If successful, the endpoint will return a status code of 201 CREATED and the serialized data of the book it created:

```json
{
  "books": [
    {
      // book data
    }
  ]
}
```

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | | if the endpoint was not given the required minimum of a title and at least one author |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

## `books/<book_id>/` endpoint

This endpoint can be access with three methods, GET, PUT, or DELETE.

### GET `books/<book_id>/`

This endpoint takes the user's token and the ID of a book associated with that user and returns a serialization of that book's information.

#### Success

If successful, the endpoint returns something like the following:

```json
{
    "book": {
        "id": "<id>",
        "title": "<title>",
        "authors": [
            "<author name>"
        ],
        "position_in_series": "<int>",
        "series": "<int>",
        "publisher": "<publisher>",
        "publication_date": "<publication date>",
        "isbn_10": "<isbn 10>",
        "isbn_13": "<isbn 13>",
        "page_count": "<int>",
        "description": "<description>",
        "current_status": "<status code>",
        "current_status_date": "<date in the format %Y-%m-%dT%H:%M:%SZ>",
        "rating": "<int from 0 through 5>",
        "tags": [
          "<tag name>"
        ]
    }
}
```

The id, title, and authors fields will always be returned. The other fields are optional, and will be returned as a default value or as null.

Refer to the status/ endpoint for details on what is meant by 'status_code'.

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `No book found with the ID: <id>` | if no book exists with the provided ID |
| 401 UNAUTHORIZED | `unauthorized` | if the book with the provided ID belongs to a different user or the user's token was invalid or missing. |

### PUT `books/<book_id>/`

This endpoint takes a user's token and a book's ID. 
It also takes a body with any parameter the user of the endpoint wishes to update as a key.

For instance, the following would update only the title field and associated tags.

```json
{
    "title": "<new_title>",
    "tags": ["<tag>", "<tag>"]
}
```

To unassociated a book from a series or to remove the book's position in series or its page count, pass in an empty string or a -1 for either or all of these values. For example:

```json
{
    "series": -1,
    "position_in_series": -1,
    "page_count": -1
}
```

This will set these values to null.

#### Success

If successful, the book's full data will be returned with the response code 200 OK.

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `Could not find book with ID: <id>` | if no book exists with the provided ID |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

### DELETE `books/<book_id>/`

This endpoint takes a user's token and a book ID and it deletes a book from the database. This operation is non-reversable.

#### Success

If successful, the endpoint will return the serialized data of the deleted book and the status code 200 OK.

If an author's only book is deleted, this operation will delete that author instance as well.

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `Could not find book with ID: <id>` | if no book exists with the provided ID |
|  | `Users can only delete their own books; book <book_id> belongs to user <user_id>"` | the book with the id provided belongs to another user |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

## `series/` endpoint

This endpoint can be accessed with two methods, GET and POST.

### GET `series/`

This endpoint takes the user's token returns all the series associated with that user.

#### Success

If successful, the endpoint will return a status of 200 OK and a serialization of the series information.

```json
{
  "series": [
    {
      "id": "<series_id>",
      "name": "<series_name>",
      "planned_count": "<planned_count>",
      "books": [
        "<book_two_id>", 
        "<book_one_id>"
      ]
    },
    {
      //...
    }
  ]
}
```

A series does not necessarily have a planned_count or any books associated with it.

##### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

### POST `series/`

This endpoint takes the user's token and a JSON hash of all the data necessary to create a new series: a name and a planned_count.

```json
{
  "name": "<series name>",
  "planned_count": "<int>"
}
```

The planned_count key is required, but an empty string or a -1 can be given to set this field to null in the database.

#### Success

If successful, the endpoint will return a serialization of the newly created series and the status 201 CREATED.

```json
{
  "series": [
    {
      "id": "<new_series_id>",
      "name": "<series_name>",
      "planned_count": "<series_count>",
      "books": []
    }
  ]
}
```

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `Invalid series parameters` | the endpoint was not given the required fields for creating a new series |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

## `series/<series_id>/` endpoint

This endpoint can be accessed with two methods, PUT and DELETE.

### PUT `series/<series_id>/`

This endpoint is simlar to the PUT books/<book_id>/ endpoint. This endpoint requires a token, a series id, and a JSON hash of what fields to modify on that series.

It will return a 200 OK and the full data of the modified series if successful, a 401 UNAUTHORIZED if given an invalid token or no token, and 400 BAD REQUEST if given an invalid series ID.

### DELETE `series/<series_id>/`

This endpoint is simlar to the DELETE books/<book_id>/ endpoint. This endpoint requires a token and a series id and it deletes the given series from the database.

If successful, it will return 200 OK and the serialized data of the deleted series. The endpoint will return 401 UNAUTHORIZED if given an invalid token or no token, and 400 BAD REQUEST if given an invalid series ID or an ID that does not match the user associated with the provided token.

## `tags/` endpoint

This endpoint can be accessed with one methods, GET.

### GET `tags/`

This endpoint takes the user's token and returns a serialization of all the tags associated with the user.

#### Success

If successful, the endpoint will return 200 OK and a "tags" key that has the value of an array of hashes, where each hash contains the tag name and all book ids associated with that tag name.

```json
{
  "tags": [
    {
      "tag_name": "<tag_name>",
      "books": ["<book_id>", "<book_id>"]
    },
    {
      "tag_name": "<tag_name>",
      "books": ["<book_id>"]
    },
    {
      "tag_name": "<tag_name>",
      "books": ["<book_id>"]
    },
  ]
}
```

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

## `tags/<tag_name>/` endpoint

This endpoint can be accessed with two methods, PUT and DELETE.

note: tags are stored in the database as a degenerated many-to-many table, so each row in the BookTag table is a single instance of a tag's use: it contains the tag_name, book FK, and user FK. all tag endpoints that modify a tag do so based off of the tag's name, and find every row of the database with that tag_name and effect them.

### PUT `tags/<tag_name>/`

This endpoint requires a user's token, the name of the tag to update, and a JSON hash containing the fields and their values that should be updated for that tag name.

For example, this could be sent to the endpoint `tags/fiction/` to change the tag name to "fantasy" and assign it only to the books with the ids 3 and 8.

```json
{
  "new_name": "fantasy",
  "books": ["3", "8"]
}
```

If this tag was already assigned to book 2, that book would be removed from the tag because it was not passed in.

If the endpoint is passed an empty booklist, it will delete the tag.

Both the new_name field and the books field must be passed in. If the tag name should not be changed, the existing tag name should be passed into the new_name field.

#### Success

If successful, the endpoint will return 200 OK and the data of the updated tag, as follows:

```json
{
  "tags": [
    {
      "tag_name": "<tag_name>",
      "books": ["<book_id>", "<book_id>"]
    }
  ]
}
```

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `new name or list of books was not provided` | if one of the required fields was not provided in the request body |
|  | `No tags match the name '<tag_name>'` | if the endpoint is given a tag name that does not exist |
|  | `Could not find book with ID: '<id>'` | if the endpoint was given a book id in the "books" field that could not be found in the database |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

#### Nested Tags

Nested tags are marked in the database as a single string with each nested component separated by two underscores, like `fiction__fantasy`.

If a tag name is given which has been used as the top-level tag in a nested tag, all instances of that substring will be modified. So if `fiction` is passed in with a new name of `Fiction`, the tag `fiction__fantasy` will become `Fiction__fantasy` automatically.

### DELETE `tags/<tag_name>/`

This endpoint takes a user's token and a tag's name.

#### Success

The endpoint deletes the associated tag and returns a 200 OK and the data of each deleted tag row if successful.

For example:

```json
{
  "tags": [
    {
        "tag_name": "<tag_name>",
        "book": "<book_id_one>"
    },
    {
        "tag_name": "<tag_name>",
        "book": "<book_id_two>"
    }
  ]
}
```

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `Could not find any tags matching the name '<tag_name>'` | if given an nonexistant tag name |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

## `status/<id>/` endpoint

This endpoint can be accessed with three methods, GET, POST, and DELETE.

For GET and POST, the `<id>` parameter corresponds to a book ID. For DELETE, the `<id>` parameter corresponds to the ID of the status row to be deleted.

### GET `status/<id>/`

This endpoint requires a user's token and a book ID.

#### Success

If successful, this endpoint returns 200 OK and a JSON hash listing all of the status rows associated with the given book ID.

```json
{
  "status_history": [
    {
      "id": "<status_id>",
      "status_code": "<status_code>",
      "book": "<book_id_two>",
      "date": "<date in the format %Y-%m-%dT%H:%M:%SZ>",
    },
    {
      "id": "<status_id>",
      "status_code": "<status_code>",
      "book": "<book_id_two>",
      "date": "<date in the format %Y-%m-%dT%H:%M:%SZ>",
    },
  ]
}
```

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `Could not find book with ID: <id>` | if the book with the provided ID does not exist or belongs to a different user than the one whose token was used to make the request |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

### POST `status/<id>/`

This endpoint requires a user's token, the ID of the book that the created status should be associated with, and a JSON hash containing keys for the status code and the date of the status.

For example:

```json
{
  "status_code": "<status_code>",
  "date": "<iso_formatted_date>"
}
```

The date value should be in ISO 8601 format.

The status code should be one of the following: `WTR`, `CURR`, `COMP`, `PAUS`, or `DNF`. These codes correspond to the following statuses:

| status code | status name       |
| ----------- | ----------------- |
| WTR         | Want to Read      |
| CURR        | Currently Reading |
| COMP        | Completed         |
| PAUS        | Paused            |
| DNF         | Discarded         |

These status codes are the only valid values for the status_code key.

#### Success

If successful, the endpoint will return 201 CREATED and the data of the new status.

```json
{
  "status_code": "<status_code>",
  "book": "<book_id>",
  "date": "<date in the format %Y-%m-%dT%H:%M:%SZ>"
}
```

If the newly-created status has a date that is more recent than the current_status_date field on the associated book, that book's current_Status field and current_status_date will be updated to match the newly-created status.

If the newly-created status has a date that is further in the past than the current_status_date on the associated book, the current_status and current_status_date fields on the book will not be altered.

#### Failure
    
| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `Invalid status parameters` | the endpoint did not recieve both a "status_code and a "date" key in the body of the request |
|  | `Invalid status code` | the status code given to the endpoint is not one of the 5 valid codes listed above |
|  | `“Date” value has an invalid format. It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.` | the format of the date string given to the endpoint was not compatible with the format expected by the database |
|  | `Could not find book with ID: <id>` | if the book id given to the endpoint does not exist or is associated with a different user |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

### DELETE `status/<id>/`

This endpoint takes a user's token and the ID of the status instance to be deleted.

#### Success

If successful, this endpoint returns 200 OK and the data of the deleted status row.

```json
{
  "id": "<id>",
  "status_code": "<status_code>",
  "book": "<book_id>",
  "date": "<date in the format %Y-%m-%dT%H:%M:%SZ>"
}
```

If the status that was deleted matches the current_status and current_status_date on the associated book, the endpoint will retrieve the next-most-recent status from the database and update the current_status and current_status_date fields on the book appropriately.

If the status that was deleted was older than the current_Status and current_status_Date on the associated book, these fields on the book will not be altered.

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `Could not find status with ID: <id>` | if the status with the given ID does not exist in the database |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |

## `rating/<book_id>/` endpoint

This endpoint can be accessed with one methods, PUT.

### PUT `rating/<book_id>/`

This endpoint requires a user's token, the ID of the book whose rating should be updated, and a JSON hash containing a key "rating" and the value of that the book's rating field should be changed to.

```json
{
  "rating": "<new_rating>"
}
```

Valid ratings are the integers 0, 1, 2, 3, 4, and 5. This field cannot be null on the book and defaults to a value of 0, which may be treated as 'unrated'.

#### Success

If successful, the endpoint will return 200 OK and the full data of the associated book, and this data will include the modified rating field.

#### Failure

| code | error message | why you would get this failure |
| ---- | ------------- | ------- |
| 400 BAD REQUEST | `Could not find book with ID: <id>` | if the book with the given ID does not exist or belongs to a different user |
| | `<value> is not a valid rating` | if the value given for the "rating" key in the request body was noe an integer from 0 through 5 |
| | `New Rating Not Provided` | if the "rating" key was not present in the request body |
| 401 UNAUTHORIZED | | if the user's token was invalid or missing. |
