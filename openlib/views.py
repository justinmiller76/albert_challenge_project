import json
from django.http import JsonResponse
import socket
from urllib.error import HTTPError, URLError
import urllib.request
from urllib.parse import urlencode
import logging
from retry import retry

logger = logging.getLogger('albert_challenge_project')


def format_response(status=None, status_code=None, message=None, data=None):
    """
    Supplies consistently-formatted body for responses
    :param status: status (success, fail, error)
    :param status_code: http status code
    :param message: response message
    :param data: additional data (sometimes optional)
    :return: JsonResponse with JSEND body
    (https://github.com/omniti-labs/jsend)
    """
    if status is None:
        raise ValueError("Missing required parameter: status")
    if status_code is None:
        raise ValueError("Missing required parameter: status_code")

    if status == "error" and message is None:
        raise ValueError("'message' must be supplied for status 'error'")

    body = {
        "status": status
    }

    # Even if data is empty, we include it per the spec for success/fail
    if status in ("success", "fail"):
        body['data'] = data
    elif status == "error" and data:
        body['data'] = data

    if message is not None:
        body['message'] = message

    return JsonResponse(body, status=status_code)


def format_success_response(status_code=200, data=None):
    """
    Convenience method for success response body
    :param status_code: http status code
    :param data: additional data (sometimes optional)
    :return: JsonResponse with JSEND body
    """
    return format_response(status="success", status_code=status_code,
                           data=data)


def format_fail_response(status_code=400, message=None, data=None):
    """
    Convenience method for fail response body
    Adding support for a (helpful) message body in fails, on top of JSEND
    :param status_code: http status code
    :param message: response message
    :param data: additional data (sometimes optional)
    :return: JsonResponse with JSEND body
    """
    return format_response(status="fail", status_code=status_code,
                           message=message, data=data)


def format_error_response(status_code=500, message=None, data=None):
    """
    Convenience method for error response body
    :param status_code: http status code
    :param message: response message
    :param data: additional data (sometimes optional)
    :return: JsonResponse with JSEND body
    """
    return format_response(status="error", status_code=status_code,
                           message=message, data=data)


# Retry 3 times in case resource is temporarily unavailable
@retry(tries=3, delay=1)
def try_get_external_url(url, timeout=5):
    """
    Call out to openlib with checks for timeouts, etc
    :param url: URL to query
    :param timeout: timeout for URL call
    :return: (status, response_body)
    """

    # logger.warning("Trying external URL: %s" % url)

    req = urllib.request.Request(url)

    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
    except HTTPError as error:
        logger.warning('HTTPError because %s\nURL: %s', error, url)
        return "error", None
    except URLError as error:
        if isinstance(error.reason, socket.timeout):
            logger.warning('Socket timeout because %s\nURL: %s', error, url)
            return "error", None
        else:
            logger.warning('URLError because %s\nURL: %s', error, url)
            return "error", None

    response_body = json.loads(resp.read())

    return "success", response_body


def get_details_for_key(key):
    """
    Get detailed book information for key
    Separate function, so it can be called internally by wishlists, etc
    :param key: book key
    :return: (status, response_body)
    """
    url = 'http://openlibrary.org/api/get?'
    params_str = urlencode({'key': key})
    return try_get_external_url(url + params_str)


def detail(request):
    """
    Get details for given book key
    :param request: http request
    :return: JsonResponse
    """
    # Retrieve arguments
    try:
        key = request.GET['key']
    except KeyError:
        message = "error retrieving required argument: key"
        return format_fail_response(message=message, data=None)

    status, response = get_details_for_key(key)

    # No data? Most likely a connection error (timeout, etc)
    if status == "error" or response is None:
        message = "internal error calling Open Library"
        return format_error_response(message=message)

    # Clearer labeling for response body
    response_data = {'openlib_result': response}

    if response['status'] != "ok":
        # There isn't an explicit response for an invalid book key, but at this
        # point that's the most likely reason if status from Open Library is
        # not ok
        message = "error calling Open Library; is 'key' value valid?"
        return format_fail_response(message=message, data=response_data)

    # Success!
    return format_success_response(data=response_data)


def search(request):
    """
    Search for a book based on title
    :param request: http request
    :return: JsonResponse
    """
    # Retrieve arguments
    try:
        title = request.GET['title']
    except KeyError:
        message = "error retrieving required argument: title"
        return format_fail_response(message=message)

    # Search on Open Library
    url = 'http://openlibrary.org/api/things?'
    params_str = urlencode({
        "query":
            # Open Lib expects double quotes (not single) for this query body
            json.dumps({
                "type": "/type/edition",
                "title~": title
            })
    })

    status, response = try_get_external_url(url + params_str)

    # No data? Most likely a connection error (timeout, etc)
    if status == "error" or response is None:
        message = "internal error calling Open Library"
        return format_error_response(message=message)

    # Clearer labeling for response body
    response_data = {'openlib_result': response}

    if response['status'] != "ok":
        # Not sure what would cause this, but we handle it
        message = "unknown error calling Open Library"
        return format_fail_response(message=message, data=response_data)

    # Success!
    return format_success_response(data=response_data)
