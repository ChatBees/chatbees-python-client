from enum import Enum

__all__ = ["ColumnType"]


class ColumnType(str, Enum):
    """
    Metadata column data types supported by NautilusDB (avro primitive types).

    You can find the definition of each data type in
    https://avro.apache.org/docs/1.11.1/specification/#primitive-types
    """
    Boolean = "boolean"
    Int = "int"
    Long = "long"
    Float = "float"
    Double = "double"
    String = "string"
    Bytes = "bytes"
