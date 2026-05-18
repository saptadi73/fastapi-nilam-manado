from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LandCoordinateBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    urutan: Optional[int] = Field(default=None, ge=1)


class LandCoordinateSchema(LandCoordinateBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class LandBase(BaseModel):
    kode: str = Field(..., max_length=50)
    luas: float = Field(..., gt=0)
    elevasi: Optional[float] = None
    kepemilikan: str = Field(..., max_length=20)
    pemilik_id: UUID
    desa_kelurahan_kode: Optional[str] = Field(default=None, max_length=10)
    kecamatan_kode: Optional[str] = Field(default=None, max_length=10)
    kabupaten_kota_kode: Optional[str] = Field(default=None, max_length=10)
    provinsi_kode: Optional[str] = Field(default=None, max_length=10)


class LandOwnerSchema(BaseModel):
    id: UUID
    nama: str
    nik: str
    hp: Optional[str] = None


class LandCreate(LandBase):
    koordinat: List[LandCoordinateBase] = Field(default_factory=list)


class LandUpdate(BaseModel):
    kode: Optional[str] = Field(default=None, max_length=50)
    luas: Optional[float] = Field(default=None, gt=0)
    elevasi: Optional[float] = None
    kepemilikan: Optional[str] = Field(default=None, max_length=20)
    pemilik_id: Optional[UUID] = None
    desa_kelurahan_kode: Optional[str] = Field(default=None, max_length=10)
    kecamatan_kode: Optional[str] = Field(default=None, max_length=10)
    kabupaten_kota_kode: Optional[str] = Field(default=None, max_length=10)
    provinsi_kode: Optional[str] = Field(default=None, max_length=10)
    koordinat: Optional[List[LandCoordinateBase]] = None


class LandSchema(LandBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    foto_path: Optional[str] = None
    foto_url: Optional[str] = None
    pemilik_nama: Optional[str] = None
    pemilik: Optional[LandOwnerSchema] = None
    desa_kelurahan: Optional[str] = None
    kecamatan: Optional[str] = None
    kabupaten_kota: Optional[str] = None
    provinsi: Optional[str] = None
    koordinat: List[LandCoordinateSchema] = Field(default_factory=list)
