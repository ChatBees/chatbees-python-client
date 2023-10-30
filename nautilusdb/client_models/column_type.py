from enum import Enum


class ColumnType(str, Enum):
    Boolean = "boolean"
    Int = "int"
    Long = "long"
    Float = "float"
    Double = "double"
    String = "string"
    Bytes = "bytes"

