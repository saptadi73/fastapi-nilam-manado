from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.wilayah import GisWilayah
from app.schemas.wilayah_schema import WilayahSchema
from app.supports.json_response import JSONResponseHandler

router = APIRouter(prefix="/wilayah", tags=["wilayah"])


def list_wilayah(
    db: Session,
    level: str,
    parent_kode: Optional[str] = None,
    search: Optional[str] = None,
):
    query = db.query(GisWilayah).filter(GisWilayah.level == level)

    if parent_kode:
        query = query.filter(GisWilayah.parent_kode == parent_kode)

    if search:
        query = query.filter(GisWilayah.nama.ilike(f"%{search}%"))

    return query.order_by(GisWilayah.nama.asc()).all()


def serialize_wilayah(rows):
    return [WilayahSchema.model_validate(row).model_dump() for row in rows]


@router.get("/provinsi")
def get_provinsi(
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    data = serialize_wilayah(list_wilayah(db, "provinsi", search=search))
    return JSONResponseHandler.success_list(
        data=data,
        label="provinsi",
        message="Data provinsi berhasil diambil",
    )


@router.get("/kabupaten-kota")
def get_kabupaten_kota(
    provinsi_kode: str = Query(...),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    data = serialize_wilayah(
        list_wilayah(db, "kabupaten_kota", parent_kode=provinsi_kode, search=search)
    )
    return JSONResponseHandler.success_list(
        data=data,
        label="kabupaten/kota",
        message="Data kabupaten/kota berhasil diambil",
    )


@router.get("/kecamatan")
def get_kecamatan(
    kabupaten_kota_kode: str = Query(...),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    data = serialize_wilayah(
        list_wilayah(db, "kecamatan", parent_kode=kabupaten_kota_kode, search=search)
    )
    return JSONResponseHandler.success_list(
        data=data,
        label="kecamatan",
        message="Data kecamatan berhasil diambil",
    )


@router.get("/desa-kelurahan")
def get_desa_kelurahan(
    kecamatan_kode: str = Query(...),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    data = serialize_wilayah(
        list_wilayah(db, "desa_kelurahan", parent_kode=kecamatan_kode, search=search)
    )
    return JSONResponseHandler.success_list(
        data=data,
        label="desa/kelurahan",
        message="Data desa/kelurahan berhasil diambil",
    )
