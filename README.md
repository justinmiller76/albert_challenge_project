# albert_challenge_project

This is a simple backend engineering case study for my Albert job application python challenge. It supplies endpoints
that allow users to search for books using the Open Library API in order to get details about a specific book.

Additionally, it also supplies endpoints for a global “wish list” to which we can add and remove books we like, and
retrieve a detailed listing of books that are in the wish list.

~~Detailed documentation is in the "docs" directory.~~

###Quick Start
1. Download the repository locally
1. Navigate to the directory in a shell, and create a virtualenv using Python3 as its base, example `virtualenv -p /Library/Frameworks/Python.framework/Versions/3.7/bin/python3 venv`
1. To enter the virtualenv, run `source venv/bin/activate`
1. Install necessary packages into the virtualenv by running `pip install -r requirements.txt` 
1. To create the wishlist model, run `python manage.py migrate`
1. If you'd like to be able to use the admin panel, run `python manage.py createsuperuser`
1. Start the server by running `python manage.py runserver`
1. Use your client of choice (eg [Postman](https://www.getpostman.com)) to 
interact with the endpoints at http://127.0.0.1:8000/

###Endpoints
The endpoints fall into two categories:
1. `/openlib` - Open Library calls
    1. `/openlib/search` - searches for books that match parameter `title`
        1. eg `http://127.0.0.1:8000/openlib/search?title=Lord+of+the+Rings`
    1. `/openlib/details` - gets detailed information about book matching parameter `key`
        1. eg `http://127.0.0.1:8000/openlib/detail?key=/books/OL7668717M`
1. `/wishlist` - wish list functionality
    1. `/wishlist/add` - add book to wish list specified by parameter `key`
    iff it exists in the Open Library and is not already in the wish list
        1. eg `http://127.0.0.1:8000/wishlist/add?key=/books/OL26793280M`
        1. NOTE: this function auto-expands keys starting with `/b/` to start with `/books/`
    1. `/wishlist/remove` - remove book from wish list specified by parameter `key`
        1. eg `http://127.0.0.1:8000/wishlist/remove?key=/books/OL26793280M`
    1. `/wishlist/list_all` - return a list of all books in the wish list, with detailed information supplied by Open Library
        1. eg `http://127.0.0.1:8000/wishlist/list_all`

###Endpoint Responses
The endpoints all return a [JSEND](https://github.com/omniti-labs/jsend) structured-result.
####Example Success
http://127.0.0.1:8000/openlib/search?title=Lord+of+the+Rings
```
{
    "status": "success",
    "data": {
        "openlib_result": {
            "status": "ok",
            "result": [
                "/books/OL26793280M",
                "/books/OL3328599M",
                "/books/OL8773280M",
                "/books/OL8773281M",
    <...>
}
```
####Example Failure
http://127.0.0.1:8000/wishlist/add?key=/books/OL26793280M
```json
{
    "status": "fail",
    "message": "book already exists in wish list: /books/OL26793280M"
}
```
