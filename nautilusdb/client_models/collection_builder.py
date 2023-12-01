from typing import Dict

from nautilusdb.client_models.collection import Collection
from nautilusdb.client_models.column_type import ColumnType

__all__ = ["CollectionBuilder"]


class CollectionBuilder:
    name: str
    dimension: int
    description: str
    metadata_columns: Dict[str, ColumnType]

    def __init__(self):
        self.name = ""
        self.dimension = 0
        self.description = ""
        self.metadata_columns = {}

    @classmethod
    def openai_ada_002(cls, name: str = "") -> "CollectionBuilder":
        """
        Canned collection config for embeddings generated with OpenAI's
        text-embedding-ada-002 model.

        :return:
        """
        return CollectionBuilder().set_dimension(1536).set_name(name)

    @classmethod
    def question_answer(cls, name: str = "") -> "CollectionBuilder":
        """
        Canned collection config that is compatible with Q/A API.

        :return:
        """
        return (CollectionBuilder()
                .set_name(name)
                .set_dimension(1536)
                .set_description('This is a demo collection. Embeddings are '
                                 'generated using OpenAI ada_002 server_models')
                .add_metadata_column('TEXT', ColumnType.String)
                .add_metadata_column('TOKENS', ColumnType.Int)
                .add_metadata_column('PAGE', ColumnType.Int)
                .add_metadata_column('FILENAME', ColumnType.String))

    def set_dimension(self, dimension: int) -> "CollectionBuilder":
        self.dimension = dimension
        return self

    def set_name(self, name: str) -> "CollectionBuilder":
        self.name = name
        return self

    def set_description(self, description: str) -> "CollectionBuilder":
        self.description = description
        return self

    def add_metadata_column(
        self,
        column_name: str,
        column_type: ColumnType
        ) -> "CollectionBuilder":
        if self.metadata_columns is None:
            self.metadata_columns = {}
        self.metadata_columns[column_name] = column_type
        return self

    def build(self) -> Collection:
        if self.name is None or self.name == "":
            raise ValueError("Collection must have a name")
        if self.dimension is None or self.dimension <= 0:
            raise ValueError("Collection must have dimension > 0")
        return Collection(
            name=self.name,
            dimension=self.dimension,
            description=self.description,
            metadata_columns=self.metadata_columns)
