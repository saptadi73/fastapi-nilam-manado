import uuid

from sqlalchemy import Column, Date, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class OilProduction(Base):
    __tablename__ = "oil_productions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    kode = Column(String(50), nullable=False, unique=True, index=True)
    tanggal_mulai = Column(Date, nullable=False)
    tanggal_akhir = Column(Date, nullable=True)
    aktual_tanggal_akhir = Column(Date, nullable=True)
    berat_kering_bahan = Column(Float, nullable=True)
    hasil_minyak = Column(Float, nullable=True)
    aktual_hasil_minyak = Column(Float, nullable=True)
    redaman = Column(Float, nullable=True)
    petani_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    lahan_id = Column(UUID(as_uuid=True), ForeignKey("lands.id"), nullable=True, index=True)
    status = Column(String(20), nullable=False, index=True)
    user_update_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
