import requests

from .exceptions import raise_for_error


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
        return f"https://{cls.account_name}.us-west-2.aws.nautilusdb.com"

    @classmethod
    def post(cls, url, data=None, files=None):
        resp = requests.post(
            url, data=data, files=files, headers=cls._construct_header())
        raise_for_error(resp)
        return resp

    @classmethod
    def get(cls, url, data=None):
        resp = requests.get(url, data=data, headers=cls._construct_header())
        raise_for_error(resp)
        return resp

    @classmethod
    def _construct_header(cls):
        return None if cls.api_key is None else {'api-key': cls.api_key}
