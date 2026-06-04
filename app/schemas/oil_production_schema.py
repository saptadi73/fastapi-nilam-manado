from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.land_schema import LandOwnerSchema
from app.schemas.planting_production_schema import PlantingProductionLandSchema, PlantingProductionUserSchema


class OilProductionBase(BaseModel):
    kode: str = Field(..., max_length=50)
    tanggal_mulai: date
    tanggal_akhir: Optional[date] = None
    aktual_tanggal_akhir: Optional[date] = None
    berat_kering_bahan: Optional[float] = Field(default=None, ge=0)
    hasil_minyak: Optional[float] = Field(default=None, ge=0)
    aktual_hasil_minyak: Optional[float] = Field(default=None, ge=0)
    tempat_penyulingan: Optional[str] = Field(default=None, max_length=255)
    harga_penyulingan_per_kg: Optional[float] = Field(default=None, ge=0)
    petani_id: UUID
    lahan_id: Optional[UUID] = None
    status: str = Field(..., max_length=20)
    user_update_id: Optional[UUID] = None


class OilProductionCreate(OilProductionBase):
    pass


class OilProductionUpdate(BaseModel):
    kode: Optional[str] = Field(default=None, max_length=50)
    tanggal_mulai: Optional[date] = None
    tanggal_akhir: Optional[date] = None
    aktual_tanggal_akhir: Optional[date] = None
    berat_kering_bahan: Optional[float] = Field(default=None, ge=0)
    hasil_minyak: Optional[float] = Field(default=None, ge=0)
    aktual_hasil_minyak: Optional[float] = Field(default=None, ge=0)
    tempat_penyulingan: Optional[str] = Field(default=None, max_length=255)
    harga_penyulingan_per_kg: Optional[float] = Field(default=None, ge=0)
    petani_id: Optional[UUID] = None
    lahan_id: Optional[UUID] = None
    status: Optional[str] = Field(default=None, max_length=20)
    user_update_id: Optional[UUID] = None


class OilProductionSchema(OilProductionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    redaman: Optional[float] = None
    petani: Optional[LandOwnerSchema] = None
    lahan: Optional[PlantingProductionLandSchema] = None
    user_update: Optional[PlantingProductionUserSchema] = None
