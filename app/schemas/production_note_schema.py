from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.planting_production_schema import PlantingProductionUserSchema


class ProductionNoteBase(BaseModel):
    kode_produksi: UUID
    tanggal: date
    catatan: str = Field(..., min_length=1)
    user_update_id: Optional[UUID] = None


class ProductionNoteCreate(ProductionNoteBase):
    pass


class ProductionNoteUpdate(BaseModel):
    kode_produksi: Optional[UUID] = None
    tanggal: Optional[date] = None
    catatan: Optional[str] = Field(default=None, min_length=1)
    user_update_id: Optional[UUID] = None


class ProductionNoteSchema(ProductionNoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_update: Optional[PlantingProductionUserSchema] = None
