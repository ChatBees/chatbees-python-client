from http import HTTPStatus

import requests

__all__ = [
    "CollectionNotFound",
    "CollectionAlreadyExists",
    "NotAuthorized",
    "LimitExceeded",
    "ServerError",
    "APIError",
    "Unimplemented",
]


class CollectionNotFound(Exception):
    pass


class CollectionAlreadyExists(Exception):
    pass


class NotAuthorized(Exception):
    pass


class LimitExceeded(Exception):
    pass


class ServerError(Exception):
    pass


class APIError(Exception):
    pass


class Unimplemented(Exception):
    pass


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
            raise CollectionAlreadyExists(response.reason)
        case HTTPStatus.NOT_FOUND:
            raise CollectionNotFound(response.reason)
        case HTTPStatus.PAYMENT_REQUIRED:
            raise LimitExceeded(response.reason)
        case HTTPStatus.INTERNAL_SERVER_ERROR:
            raise ServerError(response.reason)
        case _:
            if response.status_code >= 300:
                raise APIError(
                    f"{response.status_code}: {response.reason} "
                    f"from {response.request.url}")
