from typing import Optional, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.partner import Partner
from app.models.wilayah import GisWilayah
from app.schemas.partner_schema import PartnerCreate, PartnerSchema, PartnerUpdate
from app.supports.json_response import JSONResponseHandler

router = APIRouter(prefix="/partners", tags=["partners"])


def _get_wilayah(db: Session, kode: str, level: str):
    return (
        db.query(GisWilayah)
        .filter(GisWilayah.kode == kode, GisWilayah.level == level)
        .first()
    )


def validate_partner_wilayah(db: Session, data: dict):
    provinsi = _get_wilayah(db, data["provinsi_kode"], "provinsi")
    kabupaten = _get_wilayah(db, data["kabupaten_kota_kode"], "kabupaten_kota")
    kecamatan = _get_wilayah(db, data["kecamatan_kode"], "kecamatan")

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


def serialize_partner(db: Session, partner: Partner):
    provinsi_kode = cast(Optional[str], partner.provinsi_kode)
    kabupaten_kota_kode = cast(Optional[str], partner.kabupaten_kota_kode)
    kecamatan_kode = cast(Optional[str], partner.kecamatan_kode)

    wilayah: dict[str, Optional[str]] = {
        cast(str, row.kode): cast(Optional[str], row.nama)
        for row in db.query(GisWilayah)
        .filter(
            GisWilayah.kode.in_(
                [
                    provinsi_kode,
                    kabupaten_kota_kode,
                    kecamatan_kode,
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

    data = PartnerSchema.model_validate(partner).model_dump()
    data["provinsi"] = get_wilayah_name(provinsi_kode)
    data["kabupaten_kota"] = get_wilayah_name(kabupaten_kota_kode)
    data["kecamatan"] = get_wilayah_name(kecamatan_kode)
    return data


def get_partner_or_404(db: Session, partner_id: UUID):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner tidak ditemukan")
    return partner


@router.get("")
def list_partners(
    search: Optional[str] = Query(default=None),
    provinsi_kode: Optional[str] = Query(default=None),
    kabupaten_kota_kode: Optional[str] = Query(default=None),
    kecamatan_kode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Partner)

    if search:
        query = query.filter(Partner.nama.ilike(f"%{search}%"))

    if provinsi_kode:
        query = query.filter(Partner.provinsi_kode == provinsi_kode)

    if kabupaten_kota_kode:
        query = query.filter(Partner.kabupaten_kota_kode == kabupaten_kota_kode)

    if kecamatan_kode:
        query = query.filter(Partner.kecamatan_kode == kecamatan_kode)

    partners = query.order_by(Partner.nama.asc()).all()
    data = [serialize_partner(db, partner) for partner in partners]
    return JSONResponseHandler.success(data=data, message="Data partner berhasil diambil")


@router.get("/{partner_id}")
def get_partner(partner_id: UUID, db: Session = Depends(get_db)):
    data = serialize_partner(db, get_partner_or_404(db, partner_id))
    return JSONResponseHandler.success(data=data, message="Data partner berhasil diambil")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_partner(payload: PartnerCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    validate_partner_wilayah(db, data)

    partner = Partner(**data)
    db.add(partner)
    db.commit()
    db.refresh(partner)
    return JSONResponseHandler.success(
        data=serialize_partner(db, partner),
        message="Data partner berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{partner_id}")
def update_partner(
    partner_id: UUID,
    payload: PartnerUpdate,
    db: Session = Depends(get_db),
):
    partner = get_partner_or_404(db, partner_id)
    data = payload.model_dump(exclude_unset=True)

    merged = {
        "provinsi_kode": data.get("provinsi_kode", partner.provinsi_kode),
        "kabupaten_kota_kode": data.get("kabupaten_kota_kode", partner.kabupaten_kota_kode),
        "kecamatan_kode": data.get("kecamatan_kode", partner.kecamatan_kode),
    }
    validate_partner_wilayah(db, merged)

    for key, value in data.items():
        setattr(partner, key, value)

    db.commit()
    db.refresh(partner)
    return JSONResponseHandler.success(
        data=serialize_partner(db, partner),
        message="Data partner berhasil diperbarui",
    )


@router.delete("/{partner_id}")
def delete_partner(partner_id: UUID, db: Session = Depends(get_db)):
    partner = get_partner_or_404(db, partner_id)
    db.delete(partner)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data partner berhasil dihapus")
