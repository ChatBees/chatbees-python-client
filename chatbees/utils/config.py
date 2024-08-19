import requests
import os

from .exceptions import raise_for_error

ENV_TEST_BASE_URL = os.environ.get("ENV_TEST_BASE_URL", "")

class Config:
    api_key: str
    account_id: str
    PUBLIC_NAMESPACE: str = "public"
    namespace: str = PUBLIC_NAMESPACE

    @classmethod
    def validate_setup(cls):
        if cls.account_id is None or cls.account_id == "":
            raise ValueError("Please input your account id.")

    @classmethod
    def get_base_url(cls):
        if ENV_TEST_BASE_URL == 'preprod':
            return f"https://{cls.account_id}.preprod.aws.chatbees.ai"
        if ENV_TEST_BASE_URL.find("localhost") >= 0:
            return ENV_TEST_BASE_URL
        return f"https://{cls.account_id}.us-west-2.aws.chatbees.ai"

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
