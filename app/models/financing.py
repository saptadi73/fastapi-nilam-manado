import uuid

from sqlalchemy import Column, Date, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class FinancingProduct(Base):
    __tablename__ = "financing_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nama = Column(String(150), nullable=False, unique=True, index=True)
    harga = Column(Float, nullable=False)
    satuan = Column(String(50), nullable=False)
    deskripsi = Column(Text, nullable=True)


class Financing(Base):
    __tablename__ = "financings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nama = Column(String(150), nullable=False, index=True)
    tanggal = Column(Date, nullable=False, index=True)
    deskripsi = Column(Text, nullable=True)
    produk_id = Column(UUID(as_uuid=True), ForeignKey("financing_products.id"), nullable=False, index=True)
    harga = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    petani_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id"), nullable=True, index=True)
    planting_production_id = Column(UUID(as_uuid=True), ForeignKey("planting_productions.id"), nullable=True, index=True)
    oil_production_id = Column(UUID(as_uuid=True), ForeignKey("oil_productions.id"), nullable=True, index=True)
    sub_total = Column(Float, nullable=False)
    paid_by = Column(String(100), nullable=True)
    user_update_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
