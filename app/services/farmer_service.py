from pathlib import Path
from uuid import UUID, uuid4

from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.wilayah import GisWilayah
from app.schemas.farmer_schema import FarmerCreate, FarmerSchema, FarmerUpdate
from app.supports.json_response import JSONResponseHandler

router = APIRouter(prefix="/farmers", tags=["farmers"])

UPLOAD_ROOT = Path("uploads")
FARMER_PHOTO_DIR = UPLOAD_ROOT / "farmers"
ALLOWED_PHOTO_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


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
    data["foto_url"] = f"/{farmer.foto_path}" if farmer.foto_path else None
    return data


def get_farmer_or_404(db: Session, farmer_id: UUID):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Petani tidak ditemukan")
    return farmer


def save_farmer_photo(foto: UploadFile):
    if foto.content_type not in ALLOWED_PHOTO_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Foto harus berformat JPG, PNG, atau WEBP",
        )

    FARMER_PHOTO_DIR.mkdir(parents=True, exist_ok=True)

    original_suffix = Path(foto.filename or "").suffix.lower()
    suffix = original_suffix if original_suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"
    filename = f"{uuid4().hex}{suffix}"
    destination = FARMER_PHOTO_DIR / filename

    with destination.open("wb") as output_file:
        while chunk := foto.file.read(1024 * 1024):
            output_file.write(chunk)

    return destination.as_posix()


def remove_farmer_photo(foto_path: Optional[str]):
    if not foto_path:
        return

    path = Path(foto_path)
    if path.exists() and path.is_file():
        path.unlink()


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
def get_farmer(farmer_id: UUID, db: Session = Depends(get_db)):
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
    farmer_id: UUID,
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


@router.post("/{farmer_id}/foto")
def upload_farmer_photo(
    farmer_id: UUID,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    farmer = get_farmer_or_404(db, farmer_id)
    new_foto_path = save_farmer_photo(foto)
    remove_farmer_photo(farmer.foto_path)

    farmer.foto_path = new_foto_path
    db.commit()
    db.refresh(farmer)

    return JSONResponseHandler.success(
        data=serialize_farmer(db, farmer),
        message="Foto petani berhasil diupload",
    )


@router.delete("/{farmer_id}/foto")
def delete_farmer_photo(farmer_id: UUID, db: Session = Depends(get_db)):
    farmer = get_farmer_or_404(db, farmer_id)
    remove_farmer_photo(farmer.foto_path)
    farmer.foto_path = None
    db.commit()
    db.refresh(farmer)

    return JSONResponseHandler.success(
        data=serialize_farmer(db, farmer),
        message="Foto petani berhasil dihapus",
    )


@router.delete("/{farmer_id}")
def delete_farmer(farmer_id: UUID, db: Session = Depends(get_db)):
    farmer = get_farmer_or_404(db, farmer_id)
    remove_farmer_photo(farmer.foto_path)
    db.delete(farmer)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data petani berhasil dihapus")
