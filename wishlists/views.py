from .models import Book
from openlib.views import get_details_for_key, format_success_response, \
    format_fail_response, format_error_response

import json
from json import JSONDecodeError
import re
import logging

logger = logging.getLogger('albert_challenge_project')


def add(request):
    """
    Add a book key to the wish list, iff it's a real book, and not in the list
    :param request: http request
    :return: JsonResponse
    """
    if request.method != 'POST':
        return format_fail_response(message="The request must be POST")

    # Retrieve arguments
    try:
        body = json.loads(request.body)
        key = body['key']
    except JSONDecodeError as e:
        message = "error decoding request body [%s]" % e
        return format_fail_response(message=message)
    except KeyError:
        message = "error retrieving required POST argument: key"
        return format_fail_response(message=message)

    # Normalize key value to start with /books/, to reduce duplicates
    # NOTE: someone could still add a non-normalized duplicate key via admin
    key_normalized = re.sub('^/b/', '/books/', key)

    # Check validity of key by calling 'details', return failure if it doesn't
    status, response = get_details_for_key(key_normalized)

    # Note that Open Library status is 'ok' instead of 'success'
    if status != "success" or response['status'] != "ok":
        message = "supplied book key does not exist in Open Library"
        return format_fail_response(message=message, status_code=403)

    # Attempt to create new book in wish list
    try:
        obj, created = Book.objects.get_or_create(key_text=key_normalized)
    except Exception as e:
        # HACK: bare except is bad, but I'd rather fail gracefully
        logger.warning("unknown error encountered adding book [%s]" % e)
        message = "unknown error encountered adding book"
        return format_fail_response(message=message)

    if not created:
        message = "book already exists in wish list: %s" % key_normalized
        return format_fail_response(message=message)

    return format_success_response(status_code=201)


def remove(request):
    """
    Remove a book key from the wish list, if it exists in the list
    :param request: http request
    :return: JsonResponse
    """
    if request.method != 'POST':
        return format_fail_response(message="The request must be POST")

    # Retrieve arguments
    try:
        body = json.loads(request.body)
        key = body['key']
    except JSONDecodeError as e:
        message = "error decoding request body [%s]" % e
        return format_fail_response(message=message)
    except KeyError:
        message = "error retrieving required POST argument: key"
        return format_fail_response(message=message)

    # Normalize key value to start with /books/, to reduce duplicates
    # NOTE: someone could still add a non-normalized duplicate key via admin
    key_normalized = re.sub('^/b/', '/books/', key)

    # Attempt to remove book from wish list
    try:
        b = Book.objects.get(key_text=key_normalized)
    except Book.DoesNotExist:
        # Technically this could be considered a successful removal, but, no
        message = "book not found in wish list"
        return format_fail_response(message=message, status_code=403)

    try:
        b.delete()
    except Exception as e:
        # HACK: bare except is bad, but I'd rather fail gracefully
        logger.warning("unknown error encountered deleting book [%s]" % e)
        message = "unknown error encountered deleting book"
        return format_fail_response(message=message)

    response_data = {"key_normalized": key_normalized}
    return format_success_response(data=response_data, status_code=200)


def list_all(request):
    """
    Get details for all books in wish list
    :param request: http request
    :return: JsonResponse
    """
    all_keys = Book.objects.order_by('key_text')

    if all_keys is None:
        return format_error_response("unexpected error getting book list")

    # Return a list of items, each of which is the details for a single book
    data = dict()
    data['book_list'] = dict()
    for key in all_keys:
        # Assume failure: there is a bad key in the wish list
        details = 'no details found'

        # Otherwise get the list result from the response
        status, response = get_details_for_key(key)
        if status == "success" and response is not None and \
                'result' in response:
            details = response['result']

        data['book_list'][str(key)] = details

    return format_success_response(data=data)
