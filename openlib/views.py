import json

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from urllib.error import HTTPError, URLError
import socket
import urllib.request
import logging

from urllib.parse import urlencode


# Call out to openlib with common checks for timeouts, etc
# TODO: Get rid of custom JSON body code here (status, message)? Perhaps add formatMessage function?
def try_get_external_url(url, timeout=5):

    logging.info("Trying external URL: %s" % url)

    # TODO: add python lib for retry
    req = urllib.request.Request(url)
    # json_response = try_n_times(urllib.request.urlopen, 3, .1, req, timeout=5)

    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
    except HTTPError as error:
        print('Data not retrieved because %s\nURL: %s', error, url)
        return {
            "status": "fail",
            "message": "error calling Open Library endpoint [%s]" % error,
            "openlib_url": url
        }
    except URLError as error:
        if isinstance(error.reason, socket.timeout):
            return {
                "status": "fail",
                "message": "error calling Open Library endpoint; socket timed out",
                "openlib_url": url
            }
        else:
            return {
                "status": "fail",
                "message": "Some other error calling Open Library endpoint",
                "openlib_url": url
            }

    openlib_result = json.loads(resp.read())

    if openlib_result['status'] != "ok":
        return {
            "status": "fail",
            "message": "Some other error calling Open Library endpoint",
            "openlib_url": url,
            "openlib_result": openlib_result
        }

    return {
        "status": "success",
        "message": "Open Library call successful",
        "openlib_url": url,
        "openlib_result": openlib_result
    }


# Separate function, so it can be called internally by wishlists, etc
# Get detailed book information for key
def get_details_for_key(key):
    url = 'http://openlibrary.org/api/get?'
    params_str = urlencode({'key': key})
    return try_get_external_url(url + params_str)


# Get details for given book key
def detail(request):
    # Retrieve arguments
    try:
        key = request.GET['key']
    except KeyError:
        data = {
            "status": "fail",
            "message": "error retrieving required argument: key"
        }
        return JsonResponse(data)

    data = get_details_for_key(key)

    # There isn't an explicit response for an invalid book key, but at this
    # point that's the most likely reason if status from Open Library is not ok
    if data['openlib_result']['status'] != 'ok':
        data['status'] = "fail"
        data['message'] = "error calling Open Library endpoint; is 'key' valid?"

    # Success!
    return JsonResponse(data)


# Search for a book based on title
def search(request):
    # Retrieve arguments
    try:
        title = request.GET['title']
    except KeyError:
        data = {
            "status": "fail",
            "message": "error retrieving required argument: title"
        }
        return JsonResponse(data)

    # Search on Open Library
    url = 'http://openlibrary.org/api/things?'
    params_str = urlencode({
        "query":
            # Open Library expects this query body to use double quotes instead of single
            json.dumps({
                "type": "/type/edition",
                "title~": title
            })
    })
    data = try_get_external_url(url + params_str)

    # There isn't an explicit response for an invalid book key, but at this
    # point that's the most likely reason if status from Open Library is not ok
    if data['openlib_result']['status'] != 'ok':
        data['status'] = "fail"
        data['message'] = "error calling Open Library endpoint; no match for 'title'?"

    # Success!
    return JsonResponse(data)
