from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.land_schema import LandOwnerSchema
from app.schemas.user_schema import UserRefSchema


class SalesProductBase(BaseModel):
    nama: str = Field(..., max_length=150)
    jenis: str = Field(..., max_length=20)
    harga: float = Field(..., ge=0)
    satuan: str = Field(..., max_length=50)
    deskripsi: Optional[str] = None
    user_update_id: Optional[UUID] = None


class SalesProductCreate(SalesProductBase):
    pass


class SalesProductUpdate(BaseModel):
    nama: Optional[str] = Field(default=None, max_length=150)
    jenis: Optional[str] = Field(default=None, max_length=20)
    harga: Optional[float] = Field(default=None, ge=0)
    satuan: Optional[str] = Field(default=None, max_length=50)
    deskripsi: Optional[str] = None
    user_update_id: Optional[UUID] = None


class SalesProductSchema(SalesProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_update: Optional[UserRefSchema] = None


class SalePartnerRefSchema(BaseModel):
    id: UUID
    nama: str
    pic: Optional[str] = None
    hp: Optional[str] = None
    email: Optional[str] = None


class SaleBase(BaseModel):
    nama: str = Field(..., max_length=150)
    tanggal: date
    deskripsi: Optional[str] = None
    produk_penjualan_id: UUID
    quantity: float = Field(..., gt=0)
    harga: float = Field(..., ge=0)
    penjual_id: UUID
    pembeli_id: UUID
    user_update_id: Optional[UUID] = None


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    nama: Optional[str] = Field(default=None, max_length=150)
    tanggal: Optional[date] = None
    deskripsi: Optional[str] = None
    produk_penjualan_id: Optional[UUID] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    harga: Optional[float] = Field(default=None, ge=0)
    penjual_id: Optional[UUID] = None
    pembeli_id: Optional[UUID] = None
    user_update_id: Optional[UUID] = None


class SaleSchema(SaleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sub_total: float
    produk_penjualan: Optional[SalesProductSchema] = None
    penjual: Optional[LandOwnerSchema] = None
    pembeli: Optional[SalePartnerRefSchema] = None
    user_update: Optional[UserRefSchema] = None
