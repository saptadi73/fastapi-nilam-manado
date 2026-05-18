import uuid

from sqlalchemy import Column, Date, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class SalesProduct(Base):
    __tablename__ = "sales_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nama = Column(String(150), nullable=False, unique=True, index=True)
    jenis = Column(String(20), nullable=False, index=True)
    harga = Column(Float, nullable=False)
    satuan = Column(String(50), nullable=False)
    deskripsi = Column(Text, nullable=True)


class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nama = Column(String(150), nullable=False, index=True)
    tanggal = Column(Date, nullable=False, index=True)
    deskripsi = Column(Text, nullable=True)
    produk_penjualan_id = Column(UUID(as_uuid=True), ForeignKey("sales_products.id"), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    harga = Column(Float, nullable=False)
    penjual_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    pembeli_id = Column(UUID(as_uuid=True), ForeignKey("partners.id"), nullable=False, index=True)
    sub_total = Column(Float, nullable=False)
