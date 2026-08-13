from pathlib import Path
from uuid import UUID, uuid4

from typing import Optional, cast
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.user import User
from app.models.wilayah import GisWilayah
from app.schemas.farmer_schema import FarmerCreate, FarmerSchema, FarmerUpdate
from app.supports.json_response import JSONResponseHandler
from app.supports.user_update import serialize_user_ref, validate_user_update

router = APIRouter(prefix="/farmers", tags=["farmers"])

UPLOAD_ROOT = Path("uploads")
FARMER_PHOTO_DIR = UPLOAD_ROOT / "farmers"
ALLOWED_PHOTO_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_PHOTO_SIZE = 5 * 1024 * 1024
PHOTO_READ_CHUNK_SIZE = 1024 * 1024


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
    if kabupaten is None:
        raise HTTPException(status_code=400, detail="Kode kabupaten/kota tidak sesuai provinsi")
    kabupaten_parent_kode = cast(Optional[str], kabupaten.parent_kode)
    provinsi_kode = cast(Optional[str], provinsi.kode)
    if kabupaten_parent_kode != provinsi_kode:
        raise HTTPException(status_code=400, detail="Kode kabupaten/kota tidak sesuai provinsi")

    if kecamatan is None:
        raise HTTPException(status_code=400, detail="Kode kecamatan tidak sesuai kabupaten/kota")
    kecamatan_parent_kode = cast(Optional[str], kecamatan.parent_kode)
    kabupaten_kode = cast(Optional[str], kabupaten.kode)
    if kecamatan_parent_kode != kabupaten_kode:
        raise HTTPException(status_code=400, detail="Kode kecamatan tidak sesuai kabupaten/kota")

    if desa is None:
        raise HTTPException(status_code=400, detail="Kode desa/kelurahan tidak sesuai kecamatan")
    desa_parent_kode = cast(Optional[str], desa.parent_kode)
    kecamatan_kode = cast(Optional[str], kecamatan.kode)
    if desa_parent_kode != kecamatan_kode:
        raise HTTPException(status_code=400, detail="Kode desa/kelurahan tidak sesuai kecamatan")

    return {
        "provinsi": provinsi,
        "kabupaten_kota": kabupaten,
        "kecamatan": kecamatan,
        "desa_kelurahan": desa,
    }


def serialize_farmer(db: Session, farmer: Farmer):
    provinsi_kode = cast(Optional[str], farmer.provinsi_kode)
    kabupaten_kota_kode = cast(Optional[str], farmer.kabupaten_kota_kode)
    kecamatan_kode = cast(Optional[str], farmer.kecamatan_kode)
    desa_kelurahan_kode = cast(Optional[str], farmer.desa_kelurahan_kode)
    foto_path = cast(Optional[str], farmer.foto_path)
    user_update_id = cast(Optional[UUID], farmer.user_update_id)

    wilayah: dict[str, Optional[str]] = {
        cast(str, row.kode): cast(Optional[str], row.nama)
        for row in db.query(GisWilayah)
        .filter(
            GisWilayah.kode.in_(
                [
                    provinsi_kode,
                    kabupaten_kota_kode,
                    kecamatan_kode,
                    desa_kelurahan_kode,
                ]
            )
        )
        .all()
        if row.kode is not None
    }

    def get_wilayah_name(kode: Optional[str]) -> Optional[str]:
        if kode is None:
            return None
        return wilayah.get(kode)

    data = FarmerSchema.model_validate(farmer).model_dump()
    data["provinsi"] = get_wilayah_name(provinsi_kode)
    data["kabupaten_kota"] = get_wilayah_name(kabupaten_kota_kode)
    data["kecamatan"] = get_wilayah_name(kecamatan_kode)
    data["desa_kelurahan"] = get_wilayah_name(desa_kelurahan_kode)
    data["foto_url"] = f"/{foto_path}" if foto_path else None
    user_update = (
        db.query(User).filter(User.id == user_update_id).first()
        if user_update_id is not None
        else None
    )
    data["user_update"] = serialize_user_ref(user_update)
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

    written_size = 0
    try:
        with destination.open("wb") as output_file:
            while chunk := foto.file.read(PHOTO_READ_CHUNK_SIZE):
                written_size += len(chunk)
                if written_size > MAX_PHOTO_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="Ukuran foto maksimal 5 MB",
                    )
                output_file.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise

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
    return JSONResponseHandler.success_list(
        data=data,
        label="petani",
        message="Data petani berhasil diambil",
    )


@router.get("/{farmer_id}")
def get_farmer(farmer_id: UUID, db: Session = Depends(get_db)):
    data = serialize_farmer(db, get_farmer_or_404(db, farmer_id))
    return JSONResponseHandler.success(data=data, message="Data petani berhasil diambil")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_farmer(payload: FarmerCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    validate_farmer_wilayah(db, data)
    validate_user_update(db, data.get("user_update_id"))

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


@router.post("/with-foto", status_code=status.HTTP_201_CREATED)
def create_farmer_with_photo(
    nama: str = Form(...),
    nik: str = Form(...),
    alamat: str = Form(...),
    hp: Optional[str] = Form(default=None),
    desa_kelurahan_kode: str = Form(...),
    kecamatan_kode: str = Form(...),
    kabupaten_kota_kode: str = Form(...),
    provinsi_kode: str = Form(...),
    user_update_id: Optional[UUID] = Form(default=None),
    foto: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
):
    payload = FarmerCreate(
        nama=nama,
        nik=nik,
        alamat=alamat,
        hp=hp,
        desa_kelurahan_kode=desa_kelurahan_kode,
        kecamatan_kode=kecamatan_kode,
        kabupaten_kota_kode=kabupaten_kota_kode,
        provinsi_kode=provinsi_kode,
        user_update_id=user_update_id,
    )
    data = payload.model_dump()
    validate_farmer_wilayah(db, data)
    validate_user_update(db, data.get("user_update_id"))

    existing = db.query(Farmer).filter(Farmer.nik == data["nik"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="NIK petani sudah terdaftar")

    foto_path = save_farmer_photo(foto) if foto and foto.filename else None
    if foto_path:
        data["foto_path"] = foto_path

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

    if "user_update_id" in data:
        validate_user_update(db, data["user_update_id"])

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
    user_update_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    farmer = get_farmer_or_404(db, farmer_id)
    new_foto_path = save_farmer_photo(foto)
    current_foto_path = cast(Optional[str], farmer.foto_path)
    remove_farmer_photo(current_foto_path)

    validate_user_update(db, user_update_id)
    setattr(farmer, "foto_path", new_foto_path)
    if user_update_id is not None:
        setattr(farmer, "user_update_id", user_update_id)
    db.commit()
    db.refresh(farmer)

    return JSONResponseHandler.success(
        data=serialize_farmer(db, farmer),
        message="Foto petani berhasil diupload",
    )


@router.delete("/{farmer_id}/foto")
def delete_farmer_photo(
    farmer_id: UUID,
    user_update_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    farmer = get_farmer_or_404(db, farmer_id)
    current_foto_path = cast(Optional[str], farmer.foto_path)
    remove_farmer_photo(current_foto_path)
    validate_user_update(db, user_update_id)
    setattr(farmer, "foto_path", None)
    if user_update_id is not None:
        setattr(farmer, "user_update_id", user_update_id)
    db.commit()
    db.refresh(farmer)

    return JSONResponseHandler.success(
        data=serialize_farmer(db, farmer),
        message="Foto petani berhasil dihapus",
    )


@router.delete("/{farmer_id}")
def delete_farmer(farmer_id: UUID, db: Session = Depends(get_db)):
    farmer = get_farmer_or_404(db, farmer_id)
    current_foto_path = cast(Optional[str], farmer.foto_path)
    remove_farmer_photo(current_foto_path)
    db.delete(farmer)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data petani berhasil dihapus")
