from sqlalchemy import Column, String

from app.models.base import Base


class GisWilayah(Base):
    __tablename__ = "gis_wilayah"

    kode = Column(String(10), primary_key=True, index=True)
    nama = Column(String(150), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    parent_kode = Column(String(10), nullable=True, index=True)
