from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.land import Land
from app.models.oil_production import OilProduction
from app.models.user import User
from app.schemas.oil_production_schema import (
    OilProductionCreate,
    OilProductionSchema,
    OilProductionUpdate,
)
from app.supports.json_response import JSONResponseHandler

router = APIRouter(prefix="/oil-productions", tags=["oil-productions"])

ALLOWED_STATUSES = {"rencana", "berjalan", "selesai"}


def get_oil_production_or_404(db: Session, production_id: UUID):
    production = db.query(OilProduction).filter(OilProduction.id == production_id).first()
    if not production:
        raise HTTPException(status_code=404, detail="Produksi minyak tidak ditemukan")
    return production


def validate_status(value: str):
    status_value = value.lower().strip()
    if status_value not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Status harus salah satu dari: rencana, berjalan, selesai",
        )
    return status_value


def validate_oil_code_unique(db: Session, kode: str, production_id: Optional[UUID] = None):
    query = db.query(OilProduction).filter(OilProduction.kode == kode)
    if production_id:
        query = query.filter(OilProduction.id != production_id)
    if query.first():
        raise HTTPException(status_code=400, detail="Kode produksi minyak sudah terdaftar")


def validate_farmer_exists(db: Session, farmer_id: UUID):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=400, detail="Petani tidak ditemukan")
    return farmer


def validate_land(db: Session, land_id: Optional[UUID], farmer_id: UUID):
    if not land_id:
        return None

    land = db.query(Land).filter(Land.id == land_id).first()
    if not land:
        raise HTTPException(status_code=400, detail="Lahan tidak ditemukan")
    if land.pemilik_id != farmer_id:
        raise HTTPException(status_code=400, detail="Lahan tidak sesuai petani")
    return land


def validate_user_update(db: Session, user_id: Optional[UUID]):
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User update tidak ditemukan")
    return user


def calculate_redaman(data: dict):
    dry_weight = data.get("berat_kering_bahan")
    oil_weight = data.get("aktual_hasil_minyak")
    data["redaman"] = oil_weight / dry_weight if oil_weight is not None and dry_weight else None
    return data


def validate_finished_required_fields(data: dict):
    if data.get("status") != "selesai":
        return

    required_fields = {
        "aktual_tanggal_akhir": "Aktual tanggal akhir",
        "berat_kering_bahan": "Berat kering bahan",
        "aktual_hasil_minyak": "Aktual hasil minyak",
    }
    missing = [label for field, label in required_fields.items() if data.get(field) is None]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Status selesai membutuhkan data: {', '.join(missing)}",
        )


def serialize_oil_production(db: Session, production: OilProduction):
    data = OilProductionSchema.model_validate(production).model_dump()
    farmer = db.query(Farmer).filter(Farmer.id == production.petani_id).first()
    land = db.query(Land).filter(Land.id == production.lahan_id).first() if production.lahan_id else None
    user_update = (
        db.query(User).filter(User.id == production.user_update_id).first()
        if production.user_update_id
        else None
    )

    data["petani"] = (
        {"id": farmer.id, "nama": farmer.nama, "nik": farmer.nik, "hp": farmer.hp}
        if farmer
        else None
    )
    data["lahan"] = (
        {"id": land.id, "kode": land.kode, "luas": land.luas, "elevasi": land.elevasi}
        if land
        else None
    )
    data["user_update"] = (
        {"id": user_update.id, "name": user_update.name, "email": user_update.email}
        if user_update
        else None
    )
    return data


@router.get("")
def list_oil_productions(
    search: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    petani_id: Optional[UUID] = Query(default=None),
    lahan_id: Optional[UUID] = Query(default=None),
    kabupaten_kota_kode: Optional[str] = Query(default=None),
    kecamatan_kode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(OilProduction)

    if kabupaten_kota_kode or kecamatan_kode:
        query = query.join(Farmer, OilProduction.petani_id == Farmer.id)

    if search:
        query = query.filter(OilProduction.kode.ilike(f"%{search}%"))

    if status_filter:
        query = query.filter(OilProduction.status == validate_status(status_filter))

    if petani_id:
        query = query.filter(OilProduction.petani_id == petani_id)

    if lahan_id:
        query = query.filter(OilProduction.lahan_id == lahan_id)

    if kabupaten_kota_kode:
        query = query.filter(Farmer.kabupaten_kota_kode == kabupaten_kota_kode)

    if kecamatan_kode:
        query = query.filter(Farmer.kecamatan_kode == kecamatan_kode)

    productions = query.order_by(OilProduction.tanggal_mulai.desc()).all()
    data = [serialize_oil_production(db, production) for production in productions]
    return JSONResponseHandler.success(data=data, message="Data produksi minyak berhasil diambil")


@router.get("/{production_id}")
def get_oil_production(production_id: UUID, db: Session = Depends(get_db)):
    data = serialize_oil_production(db, get_oil_production_or_404(db, production_id))
    return JSONResponseHandler.success(data=data, message="Data produksi minyak berhasil diambil")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_oil_production(payload: OilProductionCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["status"] = validate_status(data["status"])
    validate_oil_code_unique(db, data["kode"])
    validate_farmer_exists(db, data["petani_id"])
    validate_land(db, data.get("lahan_id"), data["petani_id"])
    validate_user_update(db, data.get("user_update_id"))
    validate_finished_required_fields(data)
    calculate_redaman(data)

    production = OilProduction(**data)
    db.add(production)
    db.commit()
    db.refresh(production)

    return JSONResponseHandler.success(
        data=serialize_oil_production(db, production),
        message="Data produksi minyak berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{production_id}")
def update_oil_production(
    production_id: UUID,
    payload: OilProductionUpdate,
    db: Session = Depends(get_db),
):
    production = get_oil_production_or_404(db, production_id)
    data = payload.model_dump(exclude_unset=True)

    if "status" in data:
        data["status"] = validate_status(data["status"])

    if "kode" in data:
        validate_oil_code_unique(db, data["kode"], production_id=production_id)

    merged_petani_id = data.get("petani_id", production.petani_id)
    merged_lahan_id = data.get("lahan_id", production.lahan_id)

    if "petani_id" in data:
        validate_farmer_exists(db, data["petani_id"])

    if "lahan_id" in data or "petani_id" in data:
        validate_land(db, merged_lahan_id, merged_petani_id)

    if "user_update_id" in data:
        validate_user_update(db, data["user_update_id"])

    merged = {
        "status": data.get("status", production.status),
        "aktual_tanggal_akhir": data.get("aktual_tanggal_akhir", production.aktual_tanggal_akhir),
        "berat_kering_bahan": data.get("berat_kering_bahan", production.berat_kering_bahan),
        "aktual_hasil_minyak": data.get("aktual_hasil_minyak", production.aktual_hasil_minyak),
    }
    validate_finished_required_fields(merged)
    calculate_redaman(merged)
    data["redaman"] = merged["redaman"]

    for key, value in data.items():
        setattr(production, key, value)

    db.commit()
    db.refresh(production)

    return JSONResponseHandler.success(
        data=serialize_oil_production(db, production),
        message="Data produksi minyak berhasil diperbarui",
    )


@router.delete("/{production_id}")
def delete_oil_production(production_id: UUID, db: Session = Depends(get_db)):
    production = get_oil_production_or_404(db, production_id)
    db.delete(production)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data produksi minyak berhasil dihapus")
