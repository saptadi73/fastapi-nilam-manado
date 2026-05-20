import uuid

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Land(Base):
    __tablename__ = "lands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    kode = Column(String(50), nullable=False, unique=True, index=True)
    luas = Column(Float, nullable=False)
    elevasi = Column(Float, nullable=True)
    kepemilikan = Column(String(20), nullable=False, index=True)
    pemilik_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    foto_path = Column(String(255), nullable=True)
    desa_kelurahan_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=True, index=True)
    kecamatan_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=True, index=True)
    kabupaten_kota_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=True, index=True)
    provinsi_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=True, index=True)
    user_update_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    koordinat = relationship(
        "LandCoordinate",
        back_populates="lahan",
        cascade="all, delete-orphan",
        order_by="LandCoordinate.urutan",
    )


class LandCoordinate(Base):
    __tablename__ = "land_coordinates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    land_id = Column(UUID(as_uuid=True), ForeignKey("lands.id", ondelete="CASCADE"), nullable=False, index=True)
    urutan = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    lahan = relationship("Land", back_populates="koordinat")
