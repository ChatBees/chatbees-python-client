import requests
import os

from .exceptions import raise_for_error

ENV_TEST_BASE_URL = os.environ.get("ENV_TEST_BASE_URL", "")

class Config:
    PUBLIC_ACCOUNT: str = "public"
    PUBLIC_NAMESPACE: str = "public"
    api_key: str = None
    namespace: str = PUBLIC_NAMESPACE
    account_name: str = PUBLIC_ACCOUNT

    @classmethod
    def validate_setup(cls):
        if cls.account_name is None or cls.account_name != cls.PUBLIC_ACCOUNT:
            raise ValueError("Only public account ('public') is supported.")

    @classmethod
    def get_base_url(cls):
        if ENV_TEST_BASE_URL != "":
            return ENV_TEST_BASE_URL
        return f"https://{cls.account_name}.us-west-2.aws.chatbees.ai"

    @classmethod
    def post(cls, url, data=None, files=None, enforce_api_key=True):
        if enforce_api_key and (cls.api_key is None or cls.api_key == ""):
            raise ValueError(f"API key is required for using ChatBees, current config {cls.api_key}")
        # Encode data if it is a string
        if data is not None and isinstance(data, str):
            data = data.encode('utf-8')
        resp = requests.post(
            url, data=data, files=files, headers=cls._construct_header())
        raise_for_error(resp)
        return resp

    @classmethod
    def get(cls, url: str):
        if cls.api_key is None or cls.api_key == "":
            raise ValueError("API key is required for using ChatBees")

        resp = requests.get(url, headers=cls._construct_header())
        raise_for_error(resp)
        return resp

    @classmethod
    def _construct_header(cls):
        return None if cls.api_key is None else {'api-key': cls.api_key}
