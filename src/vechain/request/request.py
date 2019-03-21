import lru
import json
import hashlib
import requests
from collections.abc import Generator
from jsonrpc.exceptions import JSONRPCDispatchException


from request.typing import *


def _generate_cache_key(value):
    '''
    Generates a cache key for the *args and **kwargs
    '''
    if is_bytes(value):
        return hashlib.md5(value).hexdigest()
    elif is_text(value):
        return _generate_cache_key(to_bytes(text=value))
    elif is_boolean(value) or is_null(value) or is_number(value):
        return _generate_cache_key(repr(value))
    elif is_dict(value):
        return _generate_cache_key((
            (key, value[key])
            for key
            in sorted(value.keys())
        ))
    elif is_list_like(value) or isinstance(value, Generator):
        return _generate_cache_key("".join((
            _generate_cache_key(item)
            for item
            in value
        )))
    else:
        raise TypeError("Cannot generate cache key for value {0} of type {1}".format(
            value,
            type(value),
        ))


def _remove_session(key, session):
    session.close()


_session_cache = lru.LRU(8, callback=_remove_session)


def _get_session(*args, **kwargs):
    '''
    request.Session Provides cookie persistence, connection-pooling, and configuration.
    '''
    cache_key = _generate_cache_key((args, kwargs))
    if cache_key not in _session_cache:
        _session_cache[cache_key] = requests.Session()
    return _session_cache[cache_key]


def post(endpoint_uri, data, **kwargs):
    session = _get_session(endpoint_uri)
    response = session.post(endpoint_uri, json=data, **kwargs)
    return response


def get(endpoint_uri, params, **kwargs):
    session = _get_session(endpoint_uri)
    response = session.get(endpoint_uri, params=params, **kwargs)
    return response


class Request(object):

    def __init__(self, endpoint):
        super(Request, self).__init__()
        self._endpoint = endpoint

    def __call__(self, parameter):
        if parameter is not None:
            return Request('%s/%s' % (self._endpoint, parameter))
        return self

    def __getattr__(self, resource):
        return Request('%s/%s' % (self._endpoint, resource))

    def make_request(self, method, params=None, data=None, **kwargs):
        headers = {
            "accept": "application/json",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        kwargs.setdefault('headers', headers)
        kwargs.setdefault('timeout', 10)
        try:
            response = method(self._endpoint, params=params,
                              data=data, **kwargs)
            response.raise_for_status()
            return json.loads(response.content)
        except requests.exceptions.ConnectionError:
            print("Unable to connect to Thor-Request server.")
        except requests.RequestException as e:
            print("Thor-Request server Err:", e)
            print(response.content)
            raise JSONRPCDispatchException(-32000,
                                           message=response.content.decode().strip('\n'))
        return None
