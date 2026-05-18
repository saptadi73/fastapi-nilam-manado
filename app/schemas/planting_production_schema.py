from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.land_schema import LandOwnerSchema


class PlantingProductionLandSchema(BaseModel):
    id: UUID
    kode: str
    luas: float
    elevasi: Optional[float] = None


class PlantingProductionUserSchema(BaseModel):
    id: UUID
    name: Optional[str] = None
    email: Optional[str] = None


class PlantingProductionBase(BaseModel):
    kode: str = Field(..., max_length=50)
    tanggal_mulai: date
    tanggal_akhir: Optional[date] = None
    aktual_tanggal_akhir: Optional[date] = None
    luas_garapan: float = Field(..., gt=0)
    jarak_tanam: Optional[str] = Field(default=None, max_length=50)
    jumlah_batang: Optional[int] = Field(default=None, ge=0)
    hasil_produksi_basah: Optional[float] = Field(default=None, ge=0)
    aktual_hasil_produksi_basah: Optional[float] = Field(default=None, ge=0)
    aktual_hasil_produksi_kering: Optional[float] = Field(default=None, ge=0)
    varietas_bibit: Optional[str] = Field(default=None, max_length=100)
    sumber_bibit: Optional[str] = Field(default=None, max_length=150)
    cara_tanam: Optional[str] = Field(default=None, max_length=150)
    perawatan: Optional[str] = None
    pupuk: Optional[str] = None
    musim_tanam: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(..., max_length=20)
    petani_id: UUID
    lahan_id: Optional[UUID] = None
    user_update_id: Optional[UUID] = None


class PlantingProductionCreate(PlantingProductionBase):
    pass


class PlantingProductionUpdate(BaseModel):
    kode: Optional[str] = Field(default=None, max_length=50)
    tanggal_mulai: Optional[date] = None
    tanggal_akhir: Optional[date] = None
    aktual_tanggal_akhir: Optional[date] = None
    luas_garapan: Optional[float] = Field(default=None, gt=0)
    jarak_tanam: Optional[str] = Field(default=None, max_length=50)
    jumlah_batang: Optional[int] = Field(default=None, ge=0)
    hasil_produksi_basah: Optional[float] = Field(default=None, ge=0)
    aktual_hasil_produksi_basah: Optional[float] = Field(default=None, ge=0)
    aktual_hasil_produksi_kering: Optional[float] = Field(default=None, ge=0)
    varietas_bibit: Optional[str] = Field(default=None, max_length=100)
    sumber_bibit: Optional[str] = Field(default=None, max_length=150)
    cara_tanam: Optional[str] = Field(default=None, max_length=150)
    perawatan: Optional[str] = None
    pupuk: Optional[str] = None
    musim_tanam: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default=None, max_length=20)
    petani_id: Optional[UUID] = None
    lahan_id: Optional[UUID] = None
    user_update_id: Optional[UUID] = None


class PlantingProductionSchema(PlantingProductionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rasio_berat_kering_ke_basah: Optional[float] = None
    rasio_luas_garapan_ke_hasil_kering: Optional[float] = None
    petani: Optional[LandOwnerSchema] = None
    lahan: Optional[PlantingProductionLandSchema] = None
    user_update: Optional[PlantingProductionUserSchema] = None
