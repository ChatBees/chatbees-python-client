from typing import List, Dict

from nautilusdb.client_models.column_type import ColumnType
from nautilusdb.utils.config import Config
from nautilusdb.utils.exceptions import Unimplemented
from nautilusdb.client_models.vector import Vector
from nautilusdb.server_models.api import UpsertRequest, UpsertResponse


class Collection:
    """
    A Collection is a named vector search index with a fixed embedding dimension.

    Usage:
        import nautilusdb as ndb
        collection =  ndb.create_collection(ndb.
    """
    name: str
    dimension: int
    description: str
    metadata_columns: Dict[str, ColumnType]

    def __init__(self,
                 name: str,
                 dimension: int = 0,
                 description: str = "",
                 metadata_columns: Dict[str, ColumnType] = None):
        """
        Creates a Collection object

        :param name: Name of the collection
        :param dimension: Dimension of the vectors in this Collection. ALl
                          vectors in a Collection have the same dimension.
        :param description: Description of the collection
        :param metadata_columns: A set of metadata columns associated with
                                 vectors in this collection.
                                     Key: Column name
                                     Value: Column type (avro primitive type)
        """
        self.name = name
        self.dimension = dimension
        self.description = description
        self.metadata_columns = metadata_columns

    def upsert_vector(self, vectors: List[Vector]) -> int:
        """
        Upserts a list of vectors.

        For every vector in the list:
        - If a vector with the same ID already exists in the collection,
          it will be replaced with the provided vector
        - If a vector with the same ID does not exist in the collection, the
          provided vector will be created.

        :param vectors: A list of vectors to create or update
        :return: The number of vectors created or updated
        """
        url = f'{Config.get_base_url()}/vectors/upsert'
        req = UpsertRequest(collection_name=self.name,
                            vectors=[v.to_api_vector() for v in vectors])
        resp = Config.post(url=url, data=req.model_dump_json())
        resp = UpsertResponse.model_validate_json(resp.json())
        return resp.upsert_count

    def delete_vector(self, vector_ids=List[str]):
        """
        Deletes vectors specified by the given list of vector IDs from the
        collection.

        :param vector_ids: IDs of vectors to delete
        :return:
        """
        raise Unimplemented("delete_vector is not yet implemented")
