from client.collection_config import CollectionConfig


class NautilusDB:
    DEMO_ACCOUNT: str = "b487hc1om1"
    api_key: str = None
    account_name: str = DEMO_ACCOUNT

    @classmethod
    def validate_setup(cls):
        if cls.account_name is None:
            raise ValueError("Account is not set up, please run "
                             "`nautilus.init(account_name=<account_name>)`")

    @classmethod
    def get_base_url(cls):
        cls.validate_setup()
        return f"https://{cls.account_name}.execute-api.us-west-2.amazonaws.com/alpha"

    @classmethod
    def init(cls, api_key: str = None, account_name: str = DEMO_ACCOUNT):
        cls.api_key = api_key
        cls.account_name = account_name

    @classmethod
    def create_collection(
            cls,
            collection_name: str,
            config: CollectionConfig = CollectionConfig.file_upload()):
        config.validate()
        url = cls.get_base_url() + '/collections/create'



    @classmethod
    def list_collections(cls):
        pass

    @classmethod
    def delete_collection(cls):
        pass
