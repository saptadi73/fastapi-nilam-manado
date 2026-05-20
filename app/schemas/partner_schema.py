from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user_schema import UserRefSchema


class PartnerBase(BaseModel):
    nama: str = Field(..., max_length=150)
    alamat: str = Field(..., max_length=2000)
    hp: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=150)
    pic: Optional[str] = Field(default=None, max_length=150)
    web: Optional[str] = Field(default=None, max_length=255)
    kecamatan_kode: str = Field(..., max_length=10)
    kabupaten_kota_kode: str = Field(..., max_length=10)
    provinsi_kode: str = Field(..., max_length=10)
    user_update_id: Optional[UUID] = None


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(BaseModel):
    nama: Optional[str] = Field(default=None, max_length=150)
    alamat: Optional[str] = Field(default=None, max_length=2000)
    hp: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=150)
    pic: Optional[str] = Field(default=None, max_length=150)
    web: Optional[str] = Field(default=None, max_length=255)
    kecamatan_kode: Optional[str] = Field(default=None, max_length=10)
    kabupaten_kota_kode: Optional[str] = Field(default=None, max_length=10)
    provinsi_kode: Optional[str] = Field(default=None, max_length=10)
    user_update_id: Optional[UUID] = None


class PartnerSchema(PartnerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kecamatan: Optional[str] = None
    kabupaten_kota: Optional[str] = None
    provinsi: Optional[str] = None
    user_update: Optional[UserRefSchema] = None
