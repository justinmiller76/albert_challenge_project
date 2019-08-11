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
1. Use your client of choice (eg [Postman](https://www.getpostman.com)) to interact with the endpoints at http://127.0.0.1:8000/

