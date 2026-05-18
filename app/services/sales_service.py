from datetime import date
from typing import Optional, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.partner import Partner
from app.models.sales import Sale, SalesProduct
from app.schemas.sales_schema import (
    SaleCreate,
    SaleSchema,
    SalesProductCreate,
    SalesProductSchema,
    SalesProductUpdate,
    SaleUpdate,
)
from app.supports.json_response import JSONResponseHandler

product_router = APIRouter(prefix="/sales-products", tags=["sales-products"])
router = APIRouter(prefix="/sales", tags=["sales"])

ALLOWED_PRODUCT_TYPES = {"jasa", "barang"}


def get_sales_product_or_404(db: Session, product_id: UUID):
    product = db.query(SalesProduct).filter(SalesProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk penjualan tidak ditemukan")
    return product


def validate_sales_product_name_unique(db: Session, nama: str, product_id: Optional[UUID] = None):
    query = db.query(SalesProduct).filter(SalesProduct.nama == nama)
    if product_id:
        query = query.filter(SalesProduct.id != product_id)
    if query.first():
        raise HTTPException(status_code=400, detail="Nama produk penjualan sudah terdaftar")


def normalize_product_type(jenis: str):
    value = jenis.lower().strip()
    if value not in ALLOWED_PRODUCT_TYPES:
        raise HTTPException(status_code=400, detail="Jenis produk penjualan harus salah satu dari: jasa, barang")
    return value


def validate_farmer_exists(db: Session, farmer_id: UUID):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=400, detail="Petani penjual tidak ditemukan")
    return farmer


def validate_partner_exists(db: Session, partner_id: UUID):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=400, detail="Partner pembeli tidak ditemukan")
    return partner


def calculate_sub_total(data: dict):
    data["sub_total"] = data["harga"] * data["quantity"]
    return data


def get_sale_or_404(db: Session, sale_id: UUID):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Transaksi penjualan tidak ditemukan")
    return sale


def serialize_sales_product(product: SalesProduct):
    return SalesProductSchema.model_validate(product).model_dump()


def serialize_sale(db: Session, sale: Sale):
    data = SaleSchema.model_validate(sale).model_dump()
    sale_product_id = cast(UUID, sale.produk_penjualan_id)
    sale_seller_id = cast(UUID, sale.penjual_id)
    sale_buyer_id = cast(UUID, sale.pembeli_id)

    product = db.query(SalesProduct).filter(SalesProduct.id == sale_product_id).first()
    seller = db.query(Farmer).filter(Farmer.id == sale_seller_id).first()
    buyer = db.query(Partner).filter(Partner.id == sale_buyer_id).first()

    data["produk_penjualan"] = serialize_sales_product(product) if product else None
    data["penjual"] = (
        {"id": seller.id, "nama": seller.nama, "nik": seller.nik, "hp": seller.hp}
        if seller
        else None
    )
    data["pembeli"] = (
        {
            "id": buyer.id,
            "nama": buyer.nama,
            "pic": buyer.pic,
            "hp": buyer.hp,
            "email": buyer.email,
        }
        if buyer
        else None
    )
    return data


@product_router.get("")
def list_sales_products(
    search: Optional[str] = Query(default=None),
    jenis: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(SalesProduct)
    if search:
        query = query.filter(SalesProduct.nama.ilike(f"%{search}%"))
    if jenis:
        query = query.filter(SalesProduct.jenis == normalize_product_type(jenis))
    products = query.order_by(SalesProduct.nama.asc()).all()
    return JSONResponseHandler.success(
        data=[serialize_sales_product(product) for product in products],
        message="Data produk penjualan berhasil diambil",
    )


@product_router.post("", status_code=status.HTTP_201_CREATED)
def create_sales_product(payload: SalesProductCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["jenis"] = normalize_product_type(data["jenis"])
    validate_sales_product_name_unique(db, data["nama"])
    product = SalesProduct(**data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return JSONResponseHandler.success(
        data=serialize_sales_product(product),
        message="Data produk penjualan berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@product_router.get("/{product_id}")
def get_sales_product(product_id: UUID, db: Session = Depends(get_db)):
    return JSONResponseHandler.success(
        data=serialize_sales_product(get_sales_product_or_404(db, product_id)),
        message="Data produk penjualan berhasil diambil",
    )


@product_router.put("/{product_id}")
def update_sales_product(
    product_id: UUID,
    payload: SalesProductUpdate,
    db: Session = Depends(get_db),
):
    product = get_sales_product_or_404(db, product_id)
    data = payload.model_dump(exclude_unset=True)
    if "jenis" in data:
        data["jenis"] = normalize_product_type(data["jenis"])
    if "nama" in data:
        validate_sales_product_name_unique(db, data["nama"], product_id=product_id)
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return JSONResponseHandler.success(
        data=serialize_sales_product(product),
        message="Data produk penjualan berhasil diperbarui",
    )


@product_router.delete("/{product_id}")
def delete_sales_product(product_id: UUID, db: Session = Depends(get_db)):
    product = get_sales_product_or_404(db, product_id)
    used = db.query(Sale).filter(Sale.produk_penjualan_id == product_id).first()
    if used:
        raise HTTPException(status_code=400, detail="Produk penjualan sudah digunakan")
    db.delete(product)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data produk penjualan berhasil dihapus")


@router.get("")
def list_sales(
    search: Optional[str] = Query(default=None),
    penjual_id: Optional[UUID] = Query(default=None),
    pembeli_id: Optional[UUID] = Query(default=None),
    produk_penjualan_id: Optional[UUID] = Query(default=None),
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Sale)

    if search:
        query = query.filter(Sale.nama.ilike(f"%{search}%"))
    if penjual_id:
        query = query.filter(Sale.penjual_id == penjual_id)
    if pembeli_id:
        query = query.filter(Sale.pembeli_id == pembeli_id)
    if produk_penjualan_id:
        query = query.filter(Sale.produk_penjualan_id == produk_penjualan_id)
    if tanggal_mulai:
        query = query.filter(Sale.tanggal >= tanggal_mulai)
    if tanggal_akhir:
        query = query.filter(Sale.tanggal <= tanggal_akhir)

    sales = query.order_by(Sale.tanggal.desc()).all()
    data = [serialize_sale(db, sale) for sale in sales]
    total = sum(item["sub_total"] for item in data)
    return JSONResponseHandler.success(
        data={"items": data, "total_sub_total": total},
        message="Data transaksi penjualan berhasil diambil",
    )


@router.get("/{sale_id}")
def get_sale(sale_id: UUID, db: Session = Depends(get_db)):
    return JSONResponseHandler.success(
        data=serialize_sale(db, get_sale_or_404(db, sale_id)),
        message="Data transaksi penjualan berhasil diambil",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    get_sales_product_or_404(db, data["produk_penjualan_id"])
    validate_farmer_exists(db, data["penjual_id"])
    validate_partner_exists(db, data["pembeli_id"])
    calculate_sub_total(data)

    sale = Sale(**data)
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return JSONResponseHandler.success(
        data=serialize_sale(db, sale),
        message="Data transaksi penjualan berhasil dibuat",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{sale_id}")
def update_sale(
    sale_id: UUID,
    payload: SaleUpdate,
    db: Session = Depends(get_db),
):
    sale = get_sale_or_404(db, sale_id)
    data = payload.model_dump(exclude_unset=True)

    if "produk_penjualan_id" in data:
        get_sales_product_or_404(db, data["produk_penjualan_id"])

    if "penjual_id" in data:
        validate_farmer_exists(db, data["penjual_id"])

    if "pembeli_id" in data:
        validate_partner_exists(db, data["pembeli_id"])

    merged = {
        "harga": data.get("harga", sale.harga),
        "quantity": data.get("quantity", sale.quantity),
    }
    calculate_sub_total(merged)
    data["sub_total"] = merged["sub_total"]

    for key, value in data.items():
        setattr(sale, key, value)

    db.commit()
    db.refresh(sale)
    return JSONResponseHandler.success(
        data=serialize_sale(db, sale),
        message="Data transaksi penjualan berhasil diperbarui",
    )


@router.delete("/{sale_id}")
def delete_sale(sale_id: UUID, db: Session = Depends(get_db)):
    sale = get_sale_or_404(db, sale_id)
    db.delete(sale)
    db.commit()
    return JSONResponseHandler.success(data=None, message="Data transaksi penjualan berhasil dihapus")
