from django.http import JsonResponse
from .models import Book
from openlib.views import get_details_for_key

import re


# Add a book key to the wish list, iff it's a real book, and not already added
def add(request):
    # Retrieve arguments
    try:
        key = request.GET['key']
    except KeyError:
        return JsonResponse({
            "status": "fail",
            "message": "error retrieving required argument: key"
        })

    # Normalize key value to start with /books/, to reduce duplicates
    # NOTE: someone could still add a non-normalized duplicate key via admin
    key_normalized = re.sub('^/b/', '/books/', key)

    # Check validity of key by calling 'details', return failure if it doesn't
    # TODO: consolidate this into a single check_key_validity function?
    details = get_details_for_key(key_normalized)

    if details['status'] != "success":
        return JsonResponse({
            "status": "fail",
            "message": "supplied book key does not exist in Open Library"
        })

    # Attempt to create new book in wish list
    # TODO: what exceptions could happen here?
    obj, created = Book.objects.get_or_create(key_text=key_normalized)

    if not created:
        return JsonResponse({
            "status": "fail",
            "message": "book already exists in wish list: %s" % key_normalized
        })

    return JsonResponse({
        "status": "success",
        "data": None
    })


# Add a book key to the wish list, iff it's a real book, and in the list
def remove(request):
    # Retrieve arguments
    try:
        key = request.GET['key']
    except KeyError:
        return JsonResponse({
            "status": "fail",
            "message": "error retrieving required argument: key"
        })

    # Normalize key value to start with /books/, to reduce duplicates
    # NOTE: someone could still add a non-normalized duplicate key via admin
    key_normalized = re.sub('^/b/', '/books/', key)

    # Attempt to remove book from wish list
    # TODO: what exceptions could happen here?
    try:
        b = Book.objects.get(key_text=key_normalized)
    except Book.DoesNotExist:
        pass
        # Technically this could be considered a successful removal, but, no
        return JsonResponse({
            "status": "fail",
            "message": "book not found in wish list"
        })

    try:
        deleted = b.delete()
    except:
        # TODO: what exceptions could we encounter here?
        return JsonResponse({
            "status": "fail",
            "message": "failed to delete book from wish list"
        })

    return JsonResponse({
        "status": "success",
        "data": {"key_normalized": key_normalized}
    })


# Get details for all books in wish list
def list_all(request):
    # TODO: add some exception handling here
    all_keys = Book.objects.order_by('key_text')

    if all_keys is None:
        return JsonResponse({
            "status": "fail",
            "message": "error getting book list",
        })

    # Return a list of items, each of which is the details for a single book
    data = dict()
    data['book_list'] = dict()
    for key in all_keys:
        openlib_result = get_details_for_key(key)['data']['openlib_result']
        details = 'no details found'  # Assume failure: there is a bad key in the wish list
        if 'result' in openlib_result:
            details = openlib_result['result']

        data['book_list'][str(key)] = details

    return JsonResponse({
        "status": "success",
        "data": data
    })
