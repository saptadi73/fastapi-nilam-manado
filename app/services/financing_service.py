from datetime import date
from typing import Optional, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.financing import Financing, FinancingProduct
from app.models.oil_production import OilProduction
from app.models.planting_production import PlantingProduction
from app.models.user import User
from app.schemas.financing_schema import (
    FinancingCreate,
    FinancingProductCreate,
    FinancingProductSchema,
    FinancingProductUpdate,
    FinancingSchema,
    FinancingUpdate,
)
from app.supports.json_response import JSONResponseHandler

product_router = APIRouter(prefix="/financing-products", tags=["financing-products"])
router = APIRouter(prefix="/financings", tags=["financings"])


def get_product_or_404(db: Session, product_id: UUID):
    product = db.query(FinancingProduct).filter(FinancingProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk pembiayaan tidak ditemukan")
    return product


def validate_product_name_unique(db: Session, nama: str, product_id: Optional[UUID] = None):
    query = db.query(FinancingProduct).filter(FinancingProduct.nama == nama)
    if product_id:
        query = query.filter(FinancingProduct.id != product_id)
    if query.first():
        raise HTTPException(status_code=400, detail="Nama produk pembiayaan sudah terdaftar")


def validate_farmer_exists(db: Session, farmer_id: UUID):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=400, detail="Petani tidak ditemukan")
    return farmer


def validate_user_update(db: Session, user_id: Optional[UUID]):
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User update tidak ditemukan")
    return user


def validate_production_refs(
    db: Session,
    petani_id: UUID,
    planting_production_id: Optional[UUID],
    oil_production_id: Optional[UUID],
):
    planting = None
    oil = None

    if planting_production_id:
        planting = (
            db.query(PlantingProduction)
            .filter(PlantingProduction.id == planting_production_id)
            .first()
        )
        if not planting:
            raise HTTPException(status_code=400, detail="Produksi tanam tidak ditemukan")
        planting_petani_id = cast(UUID, planting.petani_id)
        if planting_petani_id != petani_id:
            raise HTTPException(status_code=400, detail="Produksi tanam tidak sesuai petani")

    if oil_production_id:
        oil = db.query(OilProduction).filter(OilProduction.id == oil_production_id).first()
        if not oil:
            raise HTTPException(status_code=400, detail="Produksi minyak tidak ditemukan")
        oil_petani_id = cast(UUID, oil.petani_id)
        if oil_petani_id != petani_id:
            raise HTTPException(status_code=400, detail="Produksi minyak tidak sesuai petani")

    return planting, oil


def calculate_sub_total(data: dict):
    data["sub_total"] = data["harga"] * data["quantity"]
    return data


def get_financing_or_404(db: Session, financing_id: UUID):
    financing = db.query(Financing).filter(Financing.id == financing_id).first()
    if not financing:
        raise HTTPException(status_code=404, detail="Pembiayaan tidak ditemukan")
    return financing


def serialize_product(product: FinancingProduct):
    return FinancingProductSchema.model_validate(product).model_dump()


def serialize_financing(db: Session, financing: Financing):
    data = FinancingSchema.model_validate(financing).model_dump()
    financing_produk_id = cast(UUID, financing.produk_id)
    financing_petani_id = cast(UUID, financing.petani_id)
    financing_planting_id = cast(Optional[UUID], financing.planting_production_id)
    financing_oil_id = cast(Optional[UUID], financing.oil_production_id)
    financing_user_update_id = cast(Optional[UUID], financing.user_update_id)

    product = db.query(FinancingProduct).filter(FinancingProduct.id == financing_produk_id).first()
    farmer = db.query(Farmer).filter(Farmer.id == financing_petani_id).first()
    planting = (
        db.query(PlantingProduction).filter(PlantingProduction.id == financing_planting_id).first()
        if financing_planting_id is not None
        else None
    )
    oil = (
        db.query(OilProduction).filter(OilProduction.id == financing_oil_id).first()
        if financing_oil_id is not None
        else None
    )
    user_update = (
        db.query(User).filter(User.id == financing_user_update_id).first()
        if financing_user_update_id is not None
        else None
    )

    data["produk"] = serialize_product(product) if product else None
    data["petani"] = (
        {"id": farmer.id, "nama": farmer.nama, "nik": farmer.nik, "hp": farmer.hp}
        if farmer
        else None
    )
    data["planting_production"] = (
        {"id": planting.id, "kode": planting.kode}
        if planting
        else None
    )
    data["oil_production"] = {"id": oil.id, "kode": oil.kode} if oil else None
    data["user_update"] = (
        {"id": user_update.id, "name": user_update.name, "email": user_update.email}
        if user_update
        else None
    )
    return data


@product_router.get("")
def list_financing_products(search: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(FinancingProduct)
    if search:
        query = query.filter(FinancingProduct.nama.ilike(f"%{search}%"))
    products = query.order_by(FinancingProduct.nama.asc()).all()
    return JSONResponseHandler.success(
        data=[serialize_product(product) for product in products],
        message="Data produk pembiayaan berhasil diambil",
    )


@product_router.post("", status_code=status.HTTP_201_CREATED)
def create_financing_product(payload: FinancingProductCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    validate_product_name_unique(db, data["nama"])
    product = FinancingProduct(**data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return JSONResponseHandler.success(
        data=serialize_product(product),
        message="Data produk pembiayaan berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@product_router.get("/{product_id}")
def get_financing_product(product_id: UUID, db: Session = Depends(get_db)):
    return JSONResponseHandler.success(
        data=serialize_product(get_product_or_404(db, product_id)),
        message="Data produk pembiayaan berhasil diambil",
    )


@product_router.put("/{product_id}")
def update_financing_product(
    product_id: UUID,
    payload: FinancingProductUpdate,
    db: Session = Depends(get_db),
):
    product = get_product_or_404(db, product_id)
    data = payload.model_dump(exclude_unset=True)
    if "nama" in data:
        validate_product_name_unique(db, data["nama"], product_id=product_id)
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return JSONResponseHandler.success(data=serialize_product(product), message="Data produk pembiayaan berhasil diperbarui")


@product_router.delete("/{product_id}")
def delete_financing_product(product_id: UUID, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    used = db.query(Financing).filter(Financing.produk_id == product_id).first()
    if used:
        raise HTTPException(status_code=400, detail="Produk pembiayaan sudah digunakan")
    db.delete(product)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data produk pembiayaan berhasil dihapus")


@router.get("")
def list_financings(
    search: Optional[str] = Query(default=None),
    petani_id: Optional[UUID] = Query(default=None),
    produk_id: Optional[UUID] = Query(default=None),
    planting_production_id: Optional[UUID] = Query(default=None),
    oil_production_id: Optional[UUID] = Query(default=None),
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Financing)

    if search:
        query = query.filter(Financing.nama.ilike(f"%{search}%"))
    if petani_id:
        query = query.filter(Financing.petani_id == petani_id)
    if produk_id:
        query = query.filter(Financing.produk_id == produk_id)
    if planting_production_id:
        query = query.filter(Financing.planting_production_id == planting_production_id)
    if oil_production_id:
        query = query.filter(Financing.oil_production_id == oil_production_id)
    if tanggal_mulai:
        query = query.filter(Financing.tanggal >= tanggal_mulai)
    if tanggal_akhir:
        query = query.filter(Financing.tanggal <= tanggal_akhir)

    financings = query.order_by(Financing.tanggal.desc()).all()
    data = [serialize_financing(db, financing) for financing in financings]
    total = sum(item["sub_total"] for item in data)
    return JSONResponseHandler.success(
        data={"items": data, "total_sub_total": total},
        message="Data pembiayaan berhasil diambil",
    )


@router.get("/{financing_id}")
def get_financing(financing_id: UUID, db: Session = Depends(get_db)):
    return JSONResponseHandler.success(
        data=serialize_financing(db, get_financing_or_404(db, financing_id)),
        message="Data pembiayaan berhasil diambil",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_financing(payload: FinancingCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    get_product_or_404(db, data["produk_id"])
    validate_farmer_exists(db, data["petani_id"])
    validate_production_refs(
        db,
        data["petani_id"],
        data.get("planting_production_id"),
        data.get("oil_production_id"),
    )
    validate_user_update(db, data.get("user_update_id"))
    calculate_sub_total(data)
    financing = Financing(**data)
    db.add(financing)
    db.commit()
    db.refresh(financing)
    return JSONResponseHandler.success(
        data=serialize_financing(db, financing),
        message="Data pembiayaan berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{financing_id}")
def update_financing(
    financing_id: UUID,
    payload: FinancingUpdate,
    db: Session = Depends(get_db),
):
    financing = get_financing_or_404(db, financing_id)
    data = payload.model_dump(exclude_unset=True)

    if "produk_id" in data:
        get_product_or_404(db, data["produk_id"])

    if "petani_id" in data:
        validate_farmer_exists(db, data["petani_id"])

    merged_petani_id = cast(UUID, data.get("petani_id", financing.petani_id))
    merged_planting_id = cast(Optional[UUID], data.get("planting_production_id", financing.planting_production_id))
    merged_oil_id = cast(Optional[UUID], data.get("oil_production_id", financing.oil_production_id))
    validate_production_refs(db, merged_petani_id, merged_planting_id, merged_oil_id)

    if "user_update_id" in data:
        validate_user_update(db, data["user_update_id"])

    merged = {
        "harga": data.get("harga", financing.harga),
        "quantity": data.get("quantity", financing.quantity),
    }
    calculate_sub_total(merged)
    data["sub_total"] = merged["sub_total"]

    for key, value in data.items():
        setattr(financing, key, value)

    db.commit()
    db.refresh(financing)
    return JSONResponseHandler.success(data=serialize_financing(db, financing), message="Data pembiayaan berhasil diperbarui")


@router.delete("/{financing_id}")
def delete_financing(financing_id: UUID, db: Session = Depends(get_db)):
    financing = get_financing_or_404(db, financing_id)
    db.delete(financing)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data pembiayaan berhasil dihapus")
