from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.land_schema import LandOwnerSchema
from app.schemas.planting_production_schema import PlantingProductionUserSchema


class FinancingProductBase(BaseModel):
    nama: str = Field(..., max_length=150)
    deskripsi: Optional[str] = None


class FinancingProductCreate(FinancingProductBase):
    pass


class FinancingProductUpdate(BaseModel):
    nama: Optional[str] = Field(default=None, max_length=150)
    deskripsi: Optional[str] = None


class FinancingProductSchema(FinancingProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class FinancingProductionRefSchema(BaseModel):
    id: UUID
    kode: str


class FinancingPartnerRefSchema(BaseModel):
    id: UUID
    nama: str
    pic: Optional[str] = None


class FinancingBase(BaseModel):
    nama: str = Field(..., max_length=150)
    tanggal: date
    deskripsi: Optional[str] = None
    produk_id: UUID
    harga: float = Field(..., ge=0)
    quantity: float = Field(..., gt=0)
    petani_id: UUID
    partner_id: Optional[UUID] = None
    planting_production_id: Optional[UUID] = None
    oil_production_id: Optional[UUID] = None
    paid_by: Optional[str] = Field(default=None, max_length=100)
    user_update_id: Optional[UUID] = None


class FinancingCreate(FinancingBase):
    pass


class FinancingUpdate(BaseModel):
    nama: Optional[str] = Field(default=None, max_length=150)
    tanggal: Optional[date] = None
    deskripsi: Optional[str] = None
    produk_id: Optional[UUID] = None
    harga: Optional[float] = Field(default=None, ge=0)
    quantity: Optional[float] = Field(default=None, gt=0)
    petani_id: Optional[UUID] = None
    partner_id: Optional[UUID] = None
    planting_production_id: Optional[UUID] = None
    oil_production_id: Optional[UUID] = None
    paid_by: Optional[str] = Field(default=None, max_length=100)
    user_update_id: Optional[UUID] = None


class FinancingSchema(FinancingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sub_total: float
    produk: Optional[FinancingProductSchema] = None
    petani: Optional[LandOwnerSchema] = None
    partner: Optional[FinancingPartnerRefSchema] = None
    planting_production: Optional[FinancingProductionRefSchema] = None
    oil_production: Optional[FinancingProductionRefSchema] = None
    user_update: Optional[PlantingProductionUserSchema] = None
