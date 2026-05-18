import uuid

from sqlalchemy import Column, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class PlantingProductionNote(Base):
    __tablename__ = "planting_production_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    kode_produksi = Column(UUID(as_uuid=True), ForeignKey("planting_productions.id"), nullable=False, index=True)
    tanggal = Column(Date, nullable=False, index=True)
    catatan = Column(Text, nullable=False)
    user_update_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)


class OilProductionNote(Base):
    __tablename__ = "oil_production_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    kode_produksi = Column(UUID(as_uuid=True), ForeignKey("oil_productions.id"), nullable=False, index=True)
    tanggal = Column(Date, nullable=False, index=True)
    catatan = Column(Text, nullable=False)
    user_update_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
