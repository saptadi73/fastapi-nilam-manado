import uuid

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class PlantingProduction(Base):
    __tablename__ = "planting_productions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    kode = Column(String(50), nullable=False, unique=True, index=True)
    tanggal_mulai = Column(Date, nullable=False)
    tanggal_akhir = Column(Date, nullable=True)
    aktual_tanggal_akhir = Column(Date, nullable=True)
    luas_garapan = Column(Float, nullable=False)
    jarak_tanam = Column(String(50), nullable=True)
    jumlah_batang = Column(Integer, nullable=True)
    hasil_produksi_basah = Column(Float, nullable=True)
    aktual_hasil_produksi_basah = Column(Float, nullable=True)
    aktual_hasil_produksi_kering = Column(Float, nullable=True)
    varietas_bibit = Column(String(100), nullable=True)
    sumber_bibit = Column(String(150), nullable=True)
    cara_tanam = Column(String(150), nullable=True)
    perawatan = Column(Text, nullable=True)
    pupuk = Column(Text, nullable=True)
    musim_tanam = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, index=True)
    petani_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    lahan_id = Column(UUID(as_uuid=True), ForeignKey("lands.id"), nullable=True, index=True)
    rasio_berat_kering_ke_basah = Column(Float, nullable=True)
    rasio_luas_garapan_ke_hasil_kering = Column(Float, nullable=True)
    user_update_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
