# albert_challenge_project

This is a simple backend engineering case study for my Albert job application python challenge. It supplies endpoints
that allow users to search for books using the Open Library API in order to get details about a specific book.

Additionally, it also supplies endpoints for a global “wish list” to which we can add and remove books we like, and
retrieve a detailed listing of books that are in the wish list.

### Quick Start
1. Download the repository locally
1. Navigate to the directory in a shell, and create a virtualenv using Python3 as its base, example `virtualenv -p python3 venv`
1. To enter the virtualenv, run `source venv/bin/activate`
1. Install necessary packages into the virtualenv by running `pip install -r requirements.txt` 
1. To create the wishlist model, run `python manage.py migrate`
1. If you'd like to be able to use the admin panel, run `python manage.py createsuperuser`
1. Start the server by running `python manage.py runserver`
1. Use your client of choice (eg [Postman](https://www.getpostman.com)) to 
interact with the endpoints at http://127.0.0.1:8000/

### Endpoint Usage
The endpoints fall into two categories:
1. `/openlib` - Open Library calls
    1. `/openlib/search` - GET - searches for books that match parameter `title`
        1. eg `http://127.0.0.1:8000/openlib/search?title=Lord+of+the+Rings`
    1. `/openlib/details` - GET - gets detailed information about book matching parameter `key`
        1. eg `http://127.0.0.1:8000/openlib/detail?key=/books/OL7668717M`
1. `/wishlist` - wish list functionality
    1. `/wishlist/add` - POST - add book to wish list specified by parameter `key`
    iff it exists in the Open Library and is not already in the wish list
        1. eg POST body `{ "key": "/b/OL26793280M" }`
        1. NOTE: this function auto-expands keys starting with `/b/` to start with `/books/`
    1. `/wishlist/remove` - POST - remove book from wish list specified by parameter `key`
        1. eg POST body `{ "key": "/b/OL26793280M" }`
    1. `/wishlist/list_all` - GET - no parameters - return a list of all books in the wish list, 
    with detailed information supplied by Open Library
        1. eg `http://127.0.0.1:8000/wishlist/list_all`
        1. The response body includes a date->book_list section, which is a dictionary containing one entry
         per book key, and each entry containing the details for that book, stored in a dictionary.
            1. If an invalid book key is somehow added to the wish list, say via admin, then the 
            value for that book in the response body is the string "no details found" instead of the 
            details dictionary.
            

### Endpoint Responses
The endpoints all return a [JSEND](https://github.com/omniti-labs/jsend) structured-result.
One slight modification is that the "fail" responses may include a message, for 
extra help debugging the failure.

The endpoints also return some http status codes for compatibility, and hopefully not to
be confusing alongside the JSEND response body.
#### Example Success
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
#### Example Failure
http://127.0.0.1:8000/wishlist/add + `{ "key": "/b/OL26793280M" }`
```json
{
    "status": "fail",
    "message": "book already exists in wish list: /books/OL26793280M"
}
```
### Notes
#### Admin
As mentioned above, a typical admin panel can be found at http://127.0.0.1:8000/admin/. 
You can tweak the wish list of Books manually here. Note that when you add a book here, there is no verification
of the validity of a `key_text` value for a Book, as there is when you call the `/wishlist/add` endpoint.

#### Limitations
* Currently there is no limit to the number of books that can be added to a wish list. Accordingly, calls to the 
`/wishlist/list_all` endpoint could become slow due to a single call being made to Open Library for each book.
* Attempts have been made to deal with real-world scenarios like timeouts from third-party API’s, but edge cases 
likely remain.