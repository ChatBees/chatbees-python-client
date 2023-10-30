from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel


class Vector(BaseModel):
    id: str
    embedding: Optional[List[float]] = None
    metas: Optional[Dict[str, Any]] = None
