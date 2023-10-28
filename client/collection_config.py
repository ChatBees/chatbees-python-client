from enum import Enum
from typing import Dict

from models.index import ColumnType


class CollectionConfig:
    dimension: int
    description: str
    metadata_columns: Dict[str, ColumnType]
    def __init__(self):
        pass
    @classmethod
    def openai_ada_002(cls):
        return CollectionConfig().set_dimension(1536)

    @classmethod
    def file_upload(cls):
        """
        Canned collection config that supports file upload

        :return:
        """
        return (CollectionConfig()
        .set_dimension(1536)
        .set_description('This is a demo collection. '
                         'Embeddings are generated using OpenAI ada_002 models')
        .add_metadata_column('text', ColumnType.String)
        .add_metadata_column('tokens', ColumnType.Int)
        .add_metadata_column('filename', ColumnType.Int))

    def set_dimension(self, dimension: int):
        self.dimension = dimension
        return self

    def set_description(self, description: str):
        self.description = description
        return self

    def add_metadata_column(self, column_name: str, column_type: ColumnType):
        if self.metadata_columns is None:
            self.metadata_columns = dict()
        self.metadata_columns[column_name] = column_type
        return self

    def validate(self):
        if self.dimension is None or self.dimension <= 0:
            raise ValueError("Collection must have dimension > 0")
        return self
