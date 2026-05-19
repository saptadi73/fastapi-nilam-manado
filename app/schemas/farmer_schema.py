from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user_schema import UserRefSchema


class FarmerBase(BaseModel):
    nama: str = Field(..., max_length=150)
    nik: str = Field(..., min_length=16, max_length=16)
    alamat: str = Field(..., max_length=255)
    hp: Optional[str] = Field(default=None, max_length=30)
    desa_kelurahan_kode: str = Field(..., max_length=10)
    kecamatan_kode: str = Field(..., max_length=10)
    kabupaten_kota_kode: str = Field(..., max_length=10)
    provinsi_kode: str = Field(..., max_length=10)
    user_update_id: Optional[UUID] = None


class FarmerCreate(FarmerBase):
    pass


class FarmerUpdate(BaseModel):
    nama: Optional[str] = Field(default=None, max_length=150)
    nik: Optional[str] = Field(default=None, min_length=16, max_length=16)
    alamat: Optional[str] = Field(default=None, max_length=255)
    hp: Optional[str] = Field(default=None, max_length=30)
    desa_kelurahan_kode: Optional[str] = Field(default=None, max_length=10)
    kecamatan_kode: Optional[str] = Field(default=None, max_length=10)
    kabupaten_kota_kode: Optional[str] = Field(default=None, max_length=10)
    provinsi_kode: Optional[str] = Field(default=None, max_length=10)
    user_update_id: Optional[UUID] = None


class FarmerSchema(FarmerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    foto_path: Optional[str] = None
    desa_kelurahan: Optional[str] = None
    kecamatan: Optional[str] = None
    kabupaten_kota: Optional[str] = None
    provinsi: Optional[str] = None
    foto_url: Optional[str] = None
    user_update: Optional[UserRefSchema] = None
