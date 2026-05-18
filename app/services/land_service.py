from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.land import Land, LandCoordinate
from app.models.wilayah import GisWilayah
from app.schemas.land_schema import LandCreate, LandSchema, LandUpdate
from app.supports.json_response import JSONResponseHandler

router = APIRouter(prefix="/lands", tags=["lands"])

UPLOAD_ROOT = Path("uploads")
LAND_PHOTO_DIR = UPLOAD_ROOT / "lands"
ALLOWED_PHOTO_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_KEPEMILIKAN = {"hak milik", "sewa", "pinjam"}


def get_land_or_404(db: Session, land_id: UUID):
    land = db.query(Land).filter(Land.id == land_id).first()
    if not land:
        raise HTTPException(status_code=404, detail="Lahan tidak ditemukan")
    return land


def validate_kepemilikan(kepemilikan: str):
    value = kepemilikan.lower().strip()
    if value not in ALLOWED_KEPEMILIKAN:
        raise HTTPException(
            status_code=400,
            detail="Kepemilikan harus salah satu dari: hak milik, sewa, pinjam",
        )
    return value


def validate_farmer_exists(db: Session, farmer_id: UUID):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=400, detail="Pemilik petani tidak ditemukan")
    return farmer


def validate_land_code_unique(db: Session, kode: str, land_id: Optional[UUID] = None):
    query = db.query(Land).filter(Land.kode == kode)
    if land_id:
        query = query.filter(Land.id != land_id)
    if query.first():
        raise HTTPException(status_code=400, detail="Kode lahan sudah terdaftar")


def _get_wilayah(db: Session, kode: Optional[str], level: str):
    if not kode:
        return None
    return (
        db.query(GisWilayah)
        .filter(GisWilayah.kode == kode, GisWilayah.level == level)
        .first()
    )


def validate_land_regions(db: Session, data: dict):
    provinsi = _get_wilayah(db, data.get("provinsi_kode"), "provinsi")
    kabupaten = _get_wilayah(db, data.get("kabupaten_kota_kode"), "kabupaten_kota")
    kecamatan = _get_wilayah(db, data.get("kecamatan_kode"), "kecamatan")
    desa = _get_wilayah(db, data.get("desa_kelurahan_kode"), "desa_kelurahan")

    if data.get("provinsi_kode") and not provinsi:
        raise HTTPException(status_code=400, detail="Kode provinsi lahan tidak valid")
    if data.get("kabupaten_kota_kode") and not kabupaten:
        raise HTTPException(status_code=400, detail="Kode kabupaten/kota lahan tidak valid")
    if data.get("kecamatan_kode") and not kecamatan:
        raise HTTPException(status_code=400, detail="Kode kecamatan lahan tidak valid")
    if data.get("desa_kelurahan_kode") and not desa:
        raise HTTPException(status_code=400, detail="Kode desa/kelurahan lahan tidak valid")

    if kabupaten and provinsi and kabupaten.parent_kode != provinsi.kode:
        raise HTTPException(status_code=400, detail="Kode kabupaten/kota lahan tidak sesuai provinsi")
    if kecamatan and kabupaten and kecamatan.parent_kode != kabupaten.kode:
        raise HTTPException(status_code=400, detail="Kode kecamatan lahan tidak sesuai kabupaten/kota")
    if desa and kecamatan and desa.parent_kode != kecamatan.kode:
        raise HTTPException(status_code=400, detail="Kode desa/kelurahan lahan tidak sesuai kecamatan")


def normalize_coordinates(coordinates):
    result = []
    for index, point in enumerate(coordinates or [], start=1):
        data = point.model_dump()
        data["urutan"] = data["urutan"] or index
        result.append(data)
    return sorted(result, key=lambda item: item["urutan"])


def replace_land_coordinates(db: Session, land: Land, coordinates):
    db.query(LandCoordinate).filter(LandCoordinate.land_id == land.id).delete()
    for point in normalize_coordinates(coordinates):
        db.add(LandCoordinate(land_id=land.id, **point))


def serialize_land(db: Session, land: Land):
    data = LandSchema.model_validate(land).model_dump()
    owner = db.query(Farmer).filter(Farmer.id == land.pemilik_id).first()
    data["pemilik_nama"] = owner.nama if owner else None
    data["pemilik"] = (
        {
            "id": owner.id,
            "nama": owner.nama,
            "nik": owner.nik,
            "hp": owner.hp,
        }
        if owner
        else None
    )
    data["foto_url"] = f"/{land.foto_path}" if land.foto_path else None
    wilayah = {
        row.kode: row.nama
        for row in db.query(GisWilayah)
        .filter(
            GisWilayah.kode.in_(
                [
                    land.provinsi_kode,
                    land.kabupaten_kota_kode,
                    land.kecamatan_kode,
                    land.desa_kelurahan_kode,
                ]
            )
        )
        .all()
    }
    data["provinsi"] = wilayah.get(land.provinsi_kode)
    data["kabupaten_kota"] = wilayah.get(land.kabupaten_kota_kode)
    data["kecamatan"] = wilayah.get(land.kecamatan_kode)
    data["desa_kelurahan"] = wilayah.get(land.desa_kelurahan_kode)
    return data


def save_land_photo(foto: UploadFile):
    if foto.content_type not in ALLOWED_PHOTO_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Foto harus berformat JPG, PNG, atau WEBP",
        )

    LAND_PHOTO_DIR.mkdir(parents=True, exist_ok=True)

    original_suffix = Path(foto.filename or "").suffix.lower()
    suffix = original_suffix if original_suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"
    filename = f"{uuid4().hex}{suffix}"
    destination = LAND_PHOTO_DIR / filename

    with destination.open("wb") as output_file:
        while chunk := foto.file.read(1024 * 1024):
            output_file.write(chunk)

    return destination.as_posix()


def remove_land_photo(foto_path: Optional[str]):
    if not foto_path:
        return

    path = Path(foto_path)
    if path.exists() and path.is_file():
        path.unlink()


@router.get("")
def list_lands(
    search: Optional[str] = Query(default=None),
    pemilik_id: Optional[UUID] = Query(default=None),
    provinsi_kode: Optional[str] = Query(default=None),
    kabupaten_kota_kode: Optional[str] = Query(default=None),
    kecamatan_kode: Optional[str] = Query(default=None),
    desa_kelurahan_kode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Land)

    if search:
        query = query.filter(Land.kode.ilike(f"%{search}%"))

    if pemilik_id:
        query = query.filter(Land.pemilik_id == pemilik_id)

    if provinsi_kode:
        query = query.filter(Land.provinsi_kode == provinsi_kode)

    if kabupaten_kota_kode:
        query = query.filter(Land.kabupaten_kota_kode == kabupaten_kota_kode)

    if kecamatan_kode:
        query = query.filter(Land.kecamatan_kode == kecamatan_kode)

    if desa_kelurahan_kode:
        query = query.filter(Land.desa_kelurahan_kode == desa_kelurahan_kode)

    lands = query.order_by(Land.kode.asc()).all()
    data = [serialize_land(db, land) for land in lands]
    return JSONResponseHandler.success(data=data, message="Data lahan berhasil diambil")


@router.get("/{land_id}")
def get_land(land_id: UUID, db: Session = Depends(get_db)):
    data = serialize_land(db, get_land_or_404(db, land_id))
    return JSONResponseHandler.success(data=data, message="Data lahan berhasil diambil")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_land(payload: LandCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"koordinat"})
    data["kepemilikan"] = validate_kepemilikan(data["kepemilikan"])
    validate_farmer_exists(db, data["pemilik_id"])
    validate_land_code_unique(db, data["kode"])
    validate_land_regions(db, data)

    land = Land(**data)
    db.add(land)
    db.flush()
    replace_land_coordinates(db, land, payload.koordinat)
    db.commit()
    db.refresh(land)

    return JSONResponseHandler.success(
        data=serialize_land(db, land),
        message="Data lahan berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{land_id}")
def update_land(
    land_id: UUID,
    payload: LandUpdate,
    db: Session = Depends(get_db),
):
    land = get_land_or_404(db, land_id)
    data = payload.model_dump(exclude_unset=True, exclude={"koordinat"})

    if "kepemilikan" in data:
        data["kepemilikan"] = validate_kepemilikan(data["kepemilikan"])

    if "pemilik_id" in data:
        validate_farmer_exists(db, data["pemilik_id"])

    if "kode" in data:
        validate_land_code_unique(db, data["kode"], land_id=land_id)

    merged_regions = {
        "provinsi_kode": data.get("provinsi_kode", land.provinsi_kode),
        "kabupaten_kota_kode": data.get("kabupaten_kota_kode", land.kabupaten_kota_kode),
        "kecamatan_kode": data.get("kecamatan_kode", land.kecamatan_kode),
        "desa_kelurahan_kode": data.get("desa_kelurahan_kode", land.desa_kelurahan_kode),
    }
    validate_land_regions(db, merged_regions)

    for key, value in data.items():
        setattr(land, key, value)

    if payload.koordinat is not None:
        replace_land_coordinates(db, land, payload.koordinat)

    db.commit()
    db.refresh(land)

    return JSONResponseHandler.success(
        data=serialize_land(db, land),
        message="Data lahan berhasil diperbarui",
    )


@router.post("/{land_id}/foto")
def upload_land_photo(
    land_id: UUID,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    land = get_land_or_404(db, land_id)
    new_foto_path = save_land_photo(foto)
    remove_land_photo(land.foto_path)

    land.foto_path = new_foto_path
    db.commit()
    db.refresh(land)

    return JSONResponseHandler.success(
        data=serialize_land(db, land),
        message="Foto lahan berhasil diupload",
    )


@router.delete("/{land_id}/foto")
def delete_land_photo(land_id: UUID, db: Session = Depends(get_db)):
    land = get_land_or_404(db, land_id)
    remove_land_photo(land.foto_path)
    land.foto_path = None
    db.commit()
    db.refresh(land)

    return JSONResponseHandler.success(
        data=serialize_land(db, land),
        message="Foto lahan berhasil dihapus",
    )


@router.delete("/{land_id}")
def delete_land(land_id: UUID, db: Session = Depends(get_db)):
    land = get_land_or_404(db, land_id)
    remove_land_photo(land.foto_path)
    db.delete(land)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data lahan berhasil dihapus")
