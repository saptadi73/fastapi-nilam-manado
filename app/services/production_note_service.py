from typing import Optional, Type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.oil_production import OilProduction
from app.models.planting_production import PlantingProduction
from app.models.production_note import OilProductionNote, PlantingProductionNote
from app.models.user import User
from app.schemas.production_note_schema import (
    ProductionNoteCreate,
    ProductionNoteSchema,
    ProductionNoteUpdate,
)
from app.supports.json_response import JSONResponseHandler

planting_note_router = APIRouter(
    prefix="/planting-production-notes",
    tags=["planting-production-notes"],
)
oil_note_router = APIRouter(
    prefix="/oil-production-notes",
    tags=["oil-production-notes"],
)


def validate_user_update(db: Session, user_id: Optional[UUID]):
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User update tidak ditemukan")
    return user


def validate_production_exists(db: Session, production_model, production_id: UUID, label: str):
    production = db.query(production_model).filter(production_model.id == production_id).first()
    if not production:
        raise HTTPException(status_code=400, detail=f"{label} tidak ditemukan")
    return production


def get_note_or_404(db: Session, note_model, note_id: UUID, label: str):
    note = db.query(note_model).filter(note_model.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail=f"Catatan {label} tidak ditemukan")
    return note


def serialize_note(db: Session, note):
    data = ProductionNoteSchema.model_validate(note).model_dump()
    user_update = (
        db.query(User).filter(User.id == note.user_update_id).first()
        if note.user_update_id
        else None
    )
    data["user_update"] = (
        {"id": user_update.id, "name": user_update.name, "email": user_update.email}
        if user_update
        else None
    )
    return data


def list_notes(
    db: Session,
    note_model,
    kode_produksi: Optional[UUID],
):
    query = db.query(note_model)
    if kode_produksi:
        query = query.filter(note_model.kode_produksi == kode_produksi)
    return query.order_by(note_model.tanggal.desc()).all()


def create_note(
    db: Session,
    payload: ProductionNoteCreate,
    note_model,
    production_model,
    label: str,
):
    data = payload.model_dump()
    validate_production_exists(db, production_model, data["kode_produksi"], label)
    validate_user_update(db, data.get("user_update_id"))

    note = note_model(**data)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def update_note(
    db: Session,
    note_id: UUID,
    payload: ProductionNoteUpdate,
    note_model,
    production_model,
    label: str,
):
    note = get_note_or_404(db, note_model, note_id, label)
    data = payload.model_dump(exclude_unset=True)

    if "kode_produksi" in data:
        validate_production_exists(db, production_model, data["kode_produksi"], label)

    if "user_update_id" in data:
        validate_user_update(db, data["user_update_id"])

    for key, value in data.items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: UUID, note_model, label: str):
    note = get_note_or_404(db, note_model, note_id, label)
    db.delete(note)
    db.commit()


@planting_note_router.get("")
def list_planting_production_notes(
    kode_produksi: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    notes = list_notes(db, PlantingProductionNote, kode_produksi)
    data = [serialize_note(db, note) for note in notes]
    return JSONResponseHandler.success(data=data, message="Data catatan produksi tanam berhasil diambil")


@planting_note_router.get("/{note_id}")
def get_planting_production_note(note_id: UUID, db: Session = Depends(get_db)):
    note = get_note_or_404(db, PlantingProductionNote, note_id, "produksi tanam")
    return JSONResponseHandler.success(data=serialize_note(db, note), message="Data catatan produksi tanam berhasil diambil")


@planting_note_router.post("", status_code=status.HTTP_201_CREATED)
def create_planting_production_note(payload: ProductionNoteCreate, db: Session = Depends(get_db)):
    note = create_note(db, payload, PlantingProductionNote, PlantingProduction, "Produksi tanam")
    return JSONResponseHandler.success(
        data=serialize_note(db, note),
        message="Data catatan produksi tanam berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@planting_note_router.put("/{note_id}")
def update_planting_production_note(
    note_id: UUID,
    payload: ProductionNoteUpdate,
    db: Session = Depends(get_db),
):
    note = update_note(db, note_id, payload, PlantingProductionNote, PlantingProduction, "produksi tanam")
    return JSONResponseHandler.success(data=serialize_note(db, note), message="Data catatan produksi tanam berhasil diperbarui")


@planting_note_router.delete("/{note_id}")
def delete_planting_production_note(note_id: UUID, db: Session = Depends(get_db)):
    delete_note(db, note_id, PlantingProductionNote, "produksi tanam")
    return JSONResponseHandler.success(data=None, message="Data catatan produksi tanam berhasil dihapus")


@oil_note_router.get("")
def list_oil_production_notes(
    kode_produksi: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    notes = list_notes(db, OilProductionNote, kode_produksi)
    data = [serialize_note(db, note) for note in notes]
    return JSONResponseHandler.success(data=data, message="Data catatan produksi minyak berhasil diambil")


@oil_note_router.get("/{note_id}")
def get_oil_production_note(note_id: UUID, db: Session = Depends(get_db)):
    note = get_note_or_404(db, OilProductionNote, note_id, "produksi minyak")
    return JSONResponseHandler.success(data=serialize_note(db, note), message="Data catatan produksi minyak berhasil diambil")


@oil_note_router.post("", status_code=status.HTTP_201_CREATED)
def create_oil_production_note(payload: ProductionNoteCreate, db: Session = Depends(get_db)):
    note = create_note(db, payload, OilProductionNote, OilProduction, "Produksi minyak")
    return JSONResponseHandler.success(
        data=serialize_note(db, note),
        message="Data catatan produksi minyak berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@oil_note_router.put("/{note_id}")
def update_oil_production_note(
    note_id: UUID,
    payload: ProductionNoteUpdate,
    db: Session = Depends(get_db),
):
    note = update_note(db, note_id, payload, OilProductionNote, OilProduction, "produksi minyak")
    return JSONResponseHandler.success(data=serialize_note(db, note), message="Data catatan produksi minyak berhasil diperbarui")


@oil_note_router.delete("/{note_id}")
def delete_oil_production_note(note_id: UUID, db: Session = Depends(get_db)):
    delete_note(db, note_id, OilProductionNote, "produksi minyak")
    return JSONResponseHandler.success(data=None, message="Data catatan produksi minyak berhasil dihapus")
