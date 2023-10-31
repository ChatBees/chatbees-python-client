import json
from http import HTTPStatus

import requests

__all__ = [
    "CollectionNotFound",
    "CollectionAlreadyExists",
    "UnAuthorized",
    "LimitExceeded",
    "ServerError",
    "APIError",
    "Unimplemented",
]


class CollectionNotFound(Exception):
    pass


class CollectionAlreadyExists(Exception):
    pass


class UnAuthorized(Exception):
    pass


class LimitExceeded(Exception):
    pass


class ServerError(Exception):
    pass


class APIError(Exception):
    pass


class Unimplemented(Exception):
    pass


def _get_reason(response: requests.Response):
    try:
        reason = json.loads(response.content)
        return reason.get('detail')
    except Exception as e:
        pass
    return response.reason


def raise_for_error(response: requests.Response):
    """
    Converts and raises http errors into appropriate client-side exception

    :param response: HTTP response
    :return
    """
    match response.status_code:
        case HTTPStatus.OK:
            return
        case HTTPStatus.CONFLICT:
            raise CollectionAlreadyExists(_get_reason(response))
        case HTTPStatus.NOT_FOUND:
            raise CollectionNotFound(_get_reason(response))
        case HTTPStatus.PAYMENT_REQUIRED:
            raise LimitExceeded(_get_reason(response))
        case HTTPStatus.INTERNAL_SERVER_ERROR:
            raise ServerError(_get_reason(response))
        case HTTPStatus.UNAUTHORIZED:
            raise UnAuthorized(_get_reason(response))
        case _:
            if response.status_code >= 400:
                raise APIError(
                    f"{response.status_code}: {_get_reason(response)} "
                    f"from {response.request.url}")
