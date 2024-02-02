import contextlib
import os
from urllib import parse

import requests


def is_url(path):
    parsed_value = parse.urlparse(path)
    return parsed_value.scheme in ("http", "https")


def validate_url_file(url):
    with contextlib.suppress(Exception):
        resp = requests.request('HEAD', url)
        nbytes = int(resp.headers.get("Content-Length"))
        if nbytes > 9_500_000:
            raise ValueError(f"File {url} exceeds size limit 9.5MB, "
                             f"actual size {nbytes} bytes")


def validate_file(path: str):
    nbyte = os.path.getsize(path)
    if nbyte > 9_500_000:
        raise ValueError(f"File {path} exceeds size limit 9.5MB, actual size "
                         f"{nbyte} bytes")