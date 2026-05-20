import uuid

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nama = Column(String(150), nullable=False, index=True)
    alamat = Column(Text, nullable=False)
    hp = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)
    pic = Column(String(150), nullable=True)
    web = Column(String(255), nullable=True)
    kecamatan_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    kabupaten_kota_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    provinsi_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    user_update_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
