import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nama = Column(String(150), nullable=False, index=True)
    nik = Column(String(16), nullable=False, unique=True, index=True)
    alamat = Column(String(255), nullable=False)
    hp = Column(String(30), nullable=True)
    foto_path = Column(String(255), nullable=True)
    desa_kelurahan_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    kecamatan_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    kabupaten_kota_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    provinsi_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
