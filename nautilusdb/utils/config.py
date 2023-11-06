import requests
import os

from .exceptions import raise_for_error

ENV_TEST_BASE_URL = os.environ.get("ENV_TEST_BASE_URL", "")

class Config:
    PUBLIC_ACCOUNT: str = "public"
    api_key: str = None
    account_name: str = PUBLIC_ACCOUNT

    @classmethod
    def validate_setup(cls):
        if cls.account_name is None or cls.account_name != cls.PUBLIC_ACCOUNT:
            raise ValueError("Only public account ('public') is supported.")

    @classmethod
    def get_base_url(cls):
        if ENV_TEST_BASE_URL != "":
            return ENV_TEST_BASE_URL
        return f"https://{cls.account_name}.us-west-2.aws.nautilusdb.com"

    @classmethod
    def post(cls, url, data=None, files=None):
        # Encode data if it is a string
        if data is not None and isinstance(data, str):
            data = data.encode('utf-8')
        resp = requests.post(
            url, data=data, files=files, headers=cls._construct_header())
        raise_for_error(resp)
        return resp

    @classmethod
    def get(cls, url: str, data=None):
        # Encode data if it is a string
        if data is not None and isinstance(data, str):
            data = data.encode('utf-8')
        resp = requests.get(url, data=data, headers=cls._construct_header())
        raise_for_error(resp)
        return resp

    @classmethod
    def _construct_header(cls):
        return None if cls.api_key is None else {'api-key': cls.api_key}
