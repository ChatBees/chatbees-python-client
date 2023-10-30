from enum import Enum
from typing import Dict

from client_models.collection import Collection
from client_models.column_type import ColumnType


class CollectionBuilder:
    name: str
    dimension: int
    description: str
    metadata_columns: Dict[str, ColumnType]

    def __init__(self):
        self.name = ""
        self.dimension = 0
        self.description = ""
        self.metadata_columns = dict()

    @classmethod
    def openai_ada_002(cls) -> "CollectionBuilder":
        """
        Canned collection config

        :return:
        """
        return CollectionBuilder().set_dimension(1536)

    @classmethod
    def file_upload(cls) -> "CollectionBuilder":
        """
        Canned collection config that supports file upload

        :return:
        """
        return (CollectionBuilder()
                .set_dimension(1536)
                .set_description('This is a demo collection. Embeddings are '
                                 'generated using OpenAI ada_002 server_models')
                .add_metadata_column('text', ColumnType.String)
                .add_metadata_column('tokens', ColumnType.Int)
                .add_metadata_column('filename', ColumnType.Int))

    def set_dimension(self, dimension: int) -> "CollectionBuilder":
        self.dimension = dimension
        return self

    def set_name(self, name: str) -> "CollectionBuilder":
        self.name = name
        return self

    def set_description(self, description: str) -> "CollectionBuilder":
        self.description = description
        return self

    def add_metadata_column(self,
                            column_name: str,
                            column_type: ColumnType) -> "CollectionBuilder":
        if self.metadata_columns is None:
            self.metadata_columns = dict()
        self.metadata_columns[column_name] = column_type
        return self

    def build(self) -> Collection:
        if self.name is None or self.name == "":
            raise ValueError("Collection must have a name")
        if self.dimension is None or self.dimension <= 0:
            raise ValueError("Collection must have dimension > 0")
        return Collection(self.name,
                          self.dimension,
                          self.description,
                          self.metadata_columns)


if __name__ == '__main__':
    collection = CollectionBuilder.file_upload().set_name("My file").build()
