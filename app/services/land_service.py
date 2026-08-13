from pathlib import Path
from typing import Optional, cast
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.land import Land, LandCoordinate
from app.models.user import User
from app.models.wilayah import GisWilayah
from app.schemas.land_schema import LandCreate, LandSchema, LandUpdate
from app.supports.json_response import JSONResponseHandler
from app.supports.user_update import serialize_user_ref, validate_user_update

router = APIRouter(prefix="/lands", tags=["lands"])

UPLOAD_ROOT = Path("uploads")
LAND_PHOTO_DIR = UPLOAD_ROOT / "lands"
ALLOWED_PHOTO_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_PHOTO_SIZE = 5 * 1024 * 1024
PHOTO_READ_CHUNK_SIZE = 1024 * 1024
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
    provinsi_kode = cast(Optional[str], data.get("provinsi_kode"))
    kabupaten_kota_kode = cast(Optional[str], data.get("kabupaten_kota_kode"))
    kecamatan_kode = cast(Optional[str], data.get("kecamatan_kode"))
    desa_kelurahan_kode = cast(Optional[str], data.get("desa_kelurahan_kode"))

    provinsi = _get_wilayah(db, provinsi_kode, "provinsi")
    kabupaten = _get_wilayah(db, kabupaten_kota_kode, "kabupaten_kota")
    kecamatan = _get_wilayah(db, kecamatan_kode, "kecamatan")
    desa = _get_wilayah(db, desa_kelurahan_kode, "desa_kelurahan")

    if provinsi_kode and not provinsi:
        raise HTTPException(status_code=400, detail="Kode provinsi lahan tidak valid")
    if kabupaten_kota_kode and not kabupaten:
        raise HTTPException(status_code=400, detail="Kode kabupaten/kota lahan tidak valid")
    if kecamatan_kode and not kecamatan:
        raise HTTPException(status_code=400, detail="Kode kecamatan lahan tidak valid")
    if desa_kelurahan_kode and not desa:
        raise HTTPException(status_code=400, detail="Kode desa/kelurahan lahan tidak valid")

    if kabupaten is not None and provinsi is not None:
        kabupaten_parent_kode = cast(Optional[str], kabupaten.parent_kode)
        provinsi_kode = cast(Optional[str], provinsi.kode)
        if kabupaten_parent_kode != provinsi_kode:
            raise HTTPException(status_code=400, detail="Kode kabupaten/kota lahan tidak sesuai provinsi")
    if kecamatan is not None and kabupaten is not None:
        kecamatan_parent_kode = cast(Optional[str], kecamatan.parent_kode)
        kabupaten_kode = cast(Optional[str], kabupaten.kode)
        if kecamatan_parent_kode != kabupaten_kode:
            raise HTTPException(status_code=400, detail="Kode kecamatan lahan tidak sesuai kabupaten/kota")
    if desa is not None and kecamatan is not None:
        desa_parent_kode = cast(Optional[str], desa.parent_kode)
        kecamatan_kode = cast(Optional[str], kecamatan.kode)
        if desa_parent_kode != kecamatan_kode:
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
    pemilik_id = cast(UUID, land.pemilik_id)
    foto_path = cast(Optional[str], land.foto_path)
    provinsi_kode = cast(Optional[str], land.provinsi_kode)
    kabupaten_kota_kode = cast(Optional[str], land.kabupaten_kota_kode)
    kecamatan_kode = cast(Optional[str], land.kecamatan_kode)
    desa_kelurahan_kode = cast(Optional[str], land.desa_kelurahan_kode)
    user_update_id = cast(Optional[UUID], land.user_update_id)

    owner = db.query(Farmer).filter(Farmer.id == pemilik_id).first()
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
    data["foto_url"] = f"/{foto_path}" if foto_path else None
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

    data["provinsi"] = get_wilayah_name(provinsi_kode)
    data["kabupaten_kota"] = get_wilayah_name(kabupaten_kota_kode)
    data["kecamatan"] = get_wilayah_name(kecamatan_kode)
    data["desa_kelurahan"] = get_wilayah_name(desa_kelurahan_kode)
    user_update = (
        db.query(User).filter(User.id == user_update_id).first()
        if user_update_id is not None
        else None
    )
    data["user_update"] = serialize_user_ref(user_update)
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
    return JSONResponseHandler.success_list(
        data=data,
        label="lahan",
        message="Data lahan berhasil diambil",
    )


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
    validate_user_update(db, data.get("user_update_id"))

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

    if "user_update_id" in data:
        validate_user_update(db, data["user_update_id"])

    merged_regions = {
        "provinsi_kode": cast(Optional[str], data.get("provinsi_kode", land.provinsi_kode)),
        "kabupaten_kota_kode": cast(Optional[str], data.get("kabupaten_kota_kode", land.kabupaten_kota_kode)),
        "kecamatan_kode": cast(Optional[str], data.get("kecamatan_kode", land.kecamatan_kode)),
        "desa_kelurahan_kode": cast(Optional[str], data.get("desa_kelurahan_kode", land.desa_kelurahan_kode)),
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
    user_update_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    land = get_land_or_404(db, land_id)
    new_foto_path = save_land_photo(foto)
    current_foto_path = cast(Optional[str], land.foto_path)
    remove_land_photo(current_foto_path)

    validate_user_update(db, user_update_id)
    setattr(land, "foto_path", new_foto_path)
    if user_update_id is not None:
        setattr(land, "user_update_id", user_update_id)
    db.commit()
    db.refresh(land)

    return JSONResponseHandler.success(
        data=serialize_land(db, land),
        message="Foto lahan berhasil diupload",
    )


@router.delete("/{land_id}/foto")
def delete_land_photo(
    land_id: UUID,
    user_update_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    land = get_land_or_404(db, land_id)
    current_foto_path = cast(Optional[str], land.foto_path)
    remove_land_photo(current_foto_path)
    validate_user_update(db, user_update_id)
    setattr(land, "foto_path", None)
    if user_update_id is not None:
        setattr(land, "user_update_id", user_update_id)
    db.commit()
    db.refresh(land)

    return JSONResponseHandler.success(
        data=serialize_land(db, land),
        message="Foto lahan berhasil dihapus",
    )


@router.delete("/{land_id}")
def delete_land(land_id: UUID, db: Session = Depends(get_db)):
    land = get_land_or_404(db, land_id)
    current_foto_path = cast(Optional[str], land.foto_path)
    remove_land_photo(current_foto_path)
    db.delete(land)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data lahan berhasil dihapus")
