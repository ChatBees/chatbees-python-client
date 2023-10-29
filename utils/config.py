import requests

from utils.exceptions import raise_for_error


class Config:
    DEMO_ACCOUNT: str = "public"
    api_key: str = None
    account_name: str = DEMO_ACCOUNT

    @classmethod
    def validate_setup(cls):
        if cls.account_name is None:
            raise ValueError("Account is not set up, please run "
                             "`nautilus.init(account_name=<account_name>)`")

    @classmethod
    def get_base_url(cls):
        Config.validate_setup()
        return f"https://{cls.account_name}.us-west-2.aws.nautilusdb.com"

    @classmethod
    def post(cls, url, data=None):
        resp = requests.post(url, data=data, headers=cls._construct_header())
        raise_for_error(resp)
        return resp


    @classmethod
    def get(cls, url, data=None):
        resp = requests.get(url, data=data, headers=cls._construct_header())
        raise_for_error(resp)
        return resp

    @classmethod
    def _construct_header(cls):
        return None if cls.api_key is None else {'api_key': cls.api_key}
