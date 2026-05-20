from typing import Optional
from pydantic import BaseModel, ConfigDict


class WilayahSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kode: str
    nama: str
    level: str
    parent_kode: Optional[str] = None
