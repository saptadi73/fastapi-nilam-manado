from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.wilayah import GisWilayah
from app.schemas.farmer_schema import FarmerCreate, FarmerSchema, FarmerUpdate
from app.supports.json_response import JSONResponseHandler

router = APIRouter(prefix="/farmers", tags=["farmers"])


def _get_wilayah(db: Session, kode: str, level: str):
    return (
        db.query(GisWilayah)
        .filter(GisWilayah.kode == kode, GisWilayah.level == level)
        .first()
    )


def validate_farmer_wilayah(db: Session, data: dict):
    provinsi = _get_wilayah(db, data["provinsi_kode"], "provinsi")
    kabupaten = _get_wilayah(db, data["kabupaten_kota_kode"], "kabupaten_kota")
    kecamatan = _get_wilayah(db, data["kecamatan_kode"], "kecamatan")
    desa = _get_wilayah(db, data["desa_kelurahan_kode"], "desa_kelurahan")

    if not provinsi:
        raise HTTPException(status_code=400, detail="Kode provinsi tidak valid")
    if not kabupaten or kabupaten.parent_kode != provinsi.kode:
        raise HTTPException(status_code=400, detail="Kode kabupaten/kota tidak sesuai provinsi")
    if not kecamatan or kecamatan.parent_kode != kabupaten.kode:
        raise HTTPException(status_code=400, detail="Kode kecamatan tidak sesuai kabupaten/kota")
    if not desa or desa.parent_kode != kecamatan.kode:
        raise HTTPException(status_code=400, detail="Kode desa/kelurahan tidak sesuai kecamatan")

    return {
        "provinsi": provinsi,
        "kabupaten_kota": kabupaten,
        "kecamatan": kecamatan,
        "desa_kelurahan": desa,
    }


def serialize_farmer(db: Session, farmer: Farmer):
    wilayah = {
        row.kode: row.nama
        for row in db.query(GisWilayah)
        .filter(
            GisWilayah.kode.in_(
                [
                    farmer.provinsi_kode,
                    farmer.kabupaten_kota_kode,
                    farmer.kecamatan_kode,
                    farmer.desa_kelurahan_kode,
                ]
            )
        )
        .all()
    }
    data = FarmerSchema.model_validate(farmer).model_dump()
    data["provinsi"] = wilayah.get(farmer.provinsi_kode)
    data["kabupaten_kota"] = wilayah.get(farmer.kabupaten_kota_kode)
    data["kecamatan"] = wilayah.get(farmer.kecamatan_kode)
    data["desa_kelurahan"] = wilayah.get(farmer.desa_kelurahan_kode)
    return data


def get_farmer_or_404(db: Session, farmer_id: int):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Petani tidak ditemukan")
    return farmer


@router.get("")
def list_farmers(
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Farmer)
    if search:
        query = query.filter(
            (Farmer.nama.ilike(f"%{search}%")) | (Farmer.nik.ilike(f"%{search}%"))
        )

    farmers = query.order_by(Farmer.nama.asc()).all()
    data = [serialize_farmer(db, farmer) for farmer in farmers]
    return JSONResponseHandler.success(data=data, message="Data petani berhasil diambil")


@router.get("/{farmer_id}")
def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    data = serialize_farmer(db, get_farmer_or_404(db, farmer_id))
    return JSONResponseHandler.success(data=data, message="Data petani berhasil diambil")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_farmer(payload: FarmerCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    validate_farmer_wilayah(db, data)

    existing = db.query(Farmer).filter(Farmer.nik == data["nik"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="NIK petani sudah terdaftar")

    farmer = Farmer(**data)
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return JSONResponseHandler.success(
        data=serialize_farmer(db, farmer),
        message="Data petani berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{farmer_id}")
def update_farmer(
    farmer_id: int,
    payload: FarmerUpdate,
    db: Session = Depends(get_db),
):
    farmer = get_farmer_or_404(db, farmer_id)
    data = payload.model_dump(exclude_unset=True)

    merged = {
        "provinsi_kode": data.get("provinsi_kode", farmer.provinsi_kode),
        "kabupaten_kota_kode": data.get("kabupaten_kota_kode", farmer.kabupaten_kota_kode),
        "kecamatan_kode": data.get("kecamatan_kode", farmer.kecamatan_kode),
        "desa_kelurahan_kode": data.get("desa_kelurahan_kode", farmer.desa_kelurahan_kode),
    }
    validate_farmer_wilayah(db, merged)

    if "nik" in data:
        existing = db.query(Farmer).filter(Farmer.nik == data["nik"], Farmer.id != farmer_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="NIK petani sudah terdaftar")

    for key, value in data.items():
        setattr(farmer, key, value)

    db.commit()
    db.refresh(farmer)
    return JSONResponseHandler.success(
        data=serialize_farmer(db, farmer),
        message="Data petani berhasil diperbarui",
    )


@router.delete("/{farmer_id}")
def delete_farmer(farmer_id: int, db: Session = Depends(get_db)):
    farmer = get_farmer_or_404(db, farmer_id)
    db.delete(farmer)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data petani berhasil dihapus")
