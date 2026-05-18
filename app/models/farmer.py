from sqlalchemy import Column, ForeignKey, Integer, String

from app.models.base import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(150), nullable=False, index=True)
    nik = Column(String(16), nullable=False, unique=True, index=True)
    alamat = Column(String(255), nullable=False)
    hp = Column(String(30), nullable=True)
    desa_kelurahan_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    kecamatan_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    kabupaten_kota_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
    provinsi_kode = Column(String(10), ForeignKey("gis_wilayah.kode"), nullable=False, index=True)
