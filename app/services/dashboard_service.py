from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farmer import Farmer
from app.models.financing import Financing
from app.models.oil_production import OilProduction
from app.models.planting_production import PlantingProduction
from app.models.sales import Sale
from app.models.wilayah import GisWilayah
from app.supports.json_response import JSONResponseHandler

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def month_key(year: int, month: int):
    return f"{year:04d}-{month:02d}"


def farmer_payload(farmer_id: UUID, farmer_name: str, nik: str, hp: Optional[str]):
    return {
        "id": farmer_id,
        "nama": farmer_name,
        "nik": nik,
        "hp": hp,
    }


def apply_date_filter(query, model, tanggal_mulai: Optional[date], tanggal_akhir: Optional[date]):
    if tanggal_mulai:
        query = query.filter(model >= tanggal_mulai)
    if tanggal_akhir:
        query = query.filter(model <= tanggal_akhir)
    return query


def month_columns(model):
    year = func.extract("year", model).label("year")
    month = func.extract("month", model).label("month")
    return year, month


def serialize_monthly_amount(rows, total_field: str):
    data = []
    for row in rows:
        year = int(row.year)
        month = int(row.month)
        total = float(getattr(row, total_field) or 0)
        data.append(
            {
                "bulan": month_key(year, month),
                "tahun": year,
                "bulan_ke": month,
                total_field: total,
                "jumlah_transaksi": int(row.jumlah_transaksi or 0),
            }
        )
    return data


def sale_monthly_query(db: Session, tanggal_mulai: Optional[date], tanggal_akhir: Optional[date], petani_id: Optional[UUID] = None):
    year, month = month_columns(Sale.tanggal)
    query = db.query(
        year,
        month,
        func.sum(Sale.sub_total).label("total_penjualan"),
        func.count(Sale.id).label("jumlah_transaksi"),
    )
    if petani_id:
        query = query.filter(Sale.penjual_id == petani_id)
    query = apply_date_filter(query, Sale.tanggal, tanggal_mulai, tanggal_akhir)
    return query.group_by(year, month).order_by(year.asc(), month.asc()).all()


def expense_monthly_query(db: Session, tanggal_mulai: Optional[date], tanggal_akhir: Optional[date], petani_id: Optional[UUID] = None):
    year, month = month_columns(Financing.tanggal)
    query = db.query(
        year,
        month,
        func.sum(Financing.sub_total).label("total_expense"),
        func.count(Financing.id).label("jumlah_transaksi"),
    )
    if petani_id:
        query = query.filter(Financing.petani_id == petani_id)
    query = apply_date_filter(query, Financing.tanggal, tanggal_mulai, tanggal_akhir)
    return query.group_by(year, month).order_by(year.asc(), month.asc()).all()


@router.get("/sales/monthly")
def monthly_sales_report(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    petani_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    rows = sale_monthly_query(db, tanggal_mulai, tanggal_akhir, petani_id=petani_id)
    data = serialize_monthly_amount(rows, "total_penjualan")
    return JSONResponseHandler.success_list(
        data=data,
        label="laporan penjualan bulan ke bulan",
        message="Report penjualan bulan ke bulan berhasil diambil",
    )


@router.get("/expenses/monthly")
def monthly_expense_report(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    petani_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    rows = expense_monthly_query(db, tanggal_mulai, tanggal_akhir, petani_id=petani_id)
    data = serialize_monthly_amount(rows, "total_expense")
    return JSONResponseHandler.success_list(
        data=data,
        label="laporan expense bulan ke bulan",
        message="Report expense bulan ke bulan berhasil diambil",
    )


@router.get("/planting-productions/monthly")
def monthly_planting_production_report(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    petani_id: Optional[UUID] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    year, month = month_columns(PlantingProduction.tanggal_mulai)
    query = db.query(
        year,
        month,
        func.count(PlantingProduction.id).label("jumlah_produksi"),
        func.sum(PlantingProduction.luas_garapan).label("total_luas_garapan"),
        func.sum(PlantingProduction.jumlah_batang).label("total_jumlah_batang"),
        func.sum(PlantingProduction.hasil_produksi_basah).label("total_rencana_hasil_basah"),
        func.sum(PlantingProduction.aktual_hasil_produksi_basah).label("total_aktual_hasil_basah"),
        func.sum(PlantingProduction.aktual_hasil_produksi_kering).label("total_aktual_hasil_kering"),
    )
    if petani_id:
        query = query.filter(PlantingProduction.petani_id == petani_id)
    if status:
        query = query.filter(PlantingProduction.status == status.lower().strip())
    query = apply_date_filter(query, PlantingProduction.tanggal_mulai, tanggal_mulai, tanggal_akhir)
    rows = query.group_by(year, month).order_by(year.asc(), month.asc()).all()

    data = []
    for row in rows:
        year_value = int(row.year)
        month_value = int(row.month)
        data.append(
            {
                "bulan": month_key(year_value, month_value),
                "tahun": year_value,
                "bulan_ke": month_value,
                "jumlah_produksi": int(row.jumlah_produksi or 0),
                "total_luas_garapan": float(row.total_luas_garapan or 0),
                "total_jumlah_batang": int(row.total_jumlah_batang or 0),
                "total_rencana_hasil_basah": float(row.total_rencana_hasil_basah or 0),
                "total_aktual_hasil_basah": float(row.total_aktual_hasil_basah or 0),
                "total_aktual_hasil_kering": float(row.total_aktual_hasil_kering or 0),
            }
        )
    return JSONResponseHandler.success_list(
        data=data,
        label="laporan produksi tanam bulan ke bulan",
        message="Report produksi tanam bulan ke bulan berhasil diambil",
    )


@router.get("/oil-productions/monthly")
def monthly_oil_production_report(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    petani_id: Optional[UUID] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    year, month = month_columns(OilProduction.tanggal_mulai)
    query = db.query(
        year,
        month,
        func.count(OilProduction.id).label("jumlah_produksi"),
        func.sum(OilProduction.berat_kering_bahan).label("total_berat_kering_bahan"),
        func.sum(OilProduction.hasil_minyak).label("total_rencana_hasil_minyak"),
        func.sum(OilProduction.aktual_hasil_minyak).label("total_aktual_hasil_minyak"),
    )
    if petani_id:
        query = query.filter(OilProduction.petani_id == petani_id)
    if status:
        query = query.filter(OilProduction.status == status.lower().strip())
    query = apply_date_filter(query, OilProduction.tanggal_mulai, tanggal_mulai, tanggal_akhir)
    rows = query.group_by(year, month).order_by(year.asc(), month.asc()).all()

    data = []
    for row in rows:
        year_value = int(row.year)
        month_value = int(row.month)
        total_berat_kering_bahan = float(row.total_berat_kering_bahan or 0)
        total_aktual_hasil_minyak = float(row.total_aktual_hasil_minyak or 0)
        data.append(
            {
                "bulan": month_key(year_value, month_value),
                "tahun": year_value,
                "bulan_ke": month_value,
                "jumlah_produksi": int(row.jumlah_produksi or 0),
                "total_berat_kering_bahan": total_berat_kering_bahan,
                "total_rencana_hasil_minyak": float(row.total_rencana_hasil_minyak or 0),
                "total_aktual_hasil_minyak": total_aktual_hasil_minyak,
                "redaman_rata_rata": (
                    total_aktual_hasil_minyak / total_berat_kering_bahan
                    if total_berat_kering_bahan
                    else None
                ),
            }
        )
    return JSONResponseHandler.success_list(
        data=data,
        label="laporan produksi minyak bulan ke bulan",
        message="Report produksi minyak bulan ke bulan berhasil diambil",
    )


@router.get("/sales/by-farmer")
def total_sales_by_farmer(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            Farmer.id.label("farmer_id"),
            Farmer.nama.label("farmer_name"),
            Farmer.nik,
            Farmer.hp,
            func.sum(Sale.sub_total).label("total_penjualan"),
            func.count(Sale.id).label("jumlah_transaksi"),
        )
        .join(Sale, Sale.penjual_id == Farmer.id)
    )
    query = apply_date_filter(query, Sale.tanggal, tanggal_mulai, tanggal_akhir)
    rows = query.group_by(Farmer.id, Farmer.nama, Farmer.nik, Farmer.hp).order_by(func.sum(Sale.sub_total).desc()).all()
    data = [
        {
            "petani": farmer_payload(row.farmer_id, row.farmer_name, row.nik, row.hp),
            "total_penjualan": float(row.total_penjualan or 0),
            "jumlah_transaksi": int(row.jumlah_transaksi or 0),
        }
        for row in rows
    ]
    return JSONResponseHandler.success_list(
        data=data,
        label="total penjualan berdasarkan petani",
        message="Total penjualan berdasarkan petani berhasil diambil",
    )


@router.get("/farmers/{petani_id}/summary")
def farmer_summary(
    petani_id: UUID,
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return the values needed by the farmer card in one request."""
    sales_query = db.query(func.coalesce(func.sum(Sale.sub_total), 0)).filter(Sale.penjual_id == petani_id)
    expense_query = db.query(func.coalesce(func.sum(Financing.sub_total), 0)).filter(Financing.petani_id == petani_id)
    oil_query = db.query(func.coalesce(func.sum(OilProduction.aktual_hasil_minyak), 0)).filter(
        OilProduction.petani_id == petani_id
    )
    planting_running_query = db.query(func.count(PlantingProduction.id)).filter(
        PlantingProduction.petani_id == petani_id,
        PlantingProduction.status == "berjalan",
    )
    oil_running_query = db.query(func.count(OilProduction.id)).filter(
        OilProduction.petani_id == petani_id,
        OilProduction.status == "berjalan",
    )

    sales_query = apply_date_filter(sales_query, Sale.tanggal, tanggal_mulai, tanggal_akhir)
    expense_query = apply_date_filter(expense_query, Financing.tanggal, tanggal_mulai, tanggal_akhir)
    oil_query = apply_date_filter(oil_query, OilProduction.tanggal_mulai, tanggal_mulai, tanggal_akhir)

    data = {
        "petani_id": petani_id,
        "total_penjualan": float(sales_query.scalar() or 0),
        "total_produksi_minyak": float(oil_query.scalar() or 0),
        "total_expense": float(expense_query.scalar() or 0),
        "jumlah_produksi_tanam_berjalan": int(planting_running_query.scalar() or 0),
        "jumlah_produksi_minyak_berjalan": int(oil_running_query.scalar() or 0),
    }
    return JSONResponseHandler.success(
        data=data,
        message="Ringkasan petani berhasil diambil",
    )


@router.get("/sales/by-farmer-regency")
@router.get("/sales/by-regency")
def total_sales_by_farmer_regency(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            Farmer.kabupaten_kota_kode.label("kabupaten_kota_kode"),
            GisWilayah.nama.label("kabupaten_kota"),
            func.sum(Sale.sub_total).label("total_penjualan"),
            func.count(Sale.id).label("jumlah_transaksi"),
            func.count(func.distinct(Farmer.id)).label("jumlah_petani"),
        )
        .join(Farmer, Sale.penjual_id == Farmer.id)
        .outerjoin(GisWilayah, Farmer.kabupaten_kota_kode == GisWilayah.kode)
    )
    query = apply_date_filter(query, Sale.tanggal, tanggal_mulai, tanggal_akhir)
    rows = (
        query.group_by(Farmer.kabupaten_kota_kode, GisWilayah.nama)
        .order_by(func.sum(Sale.sub_total).desc())
        .all()
    )
    grand_total = sum(float(row.total_penjualan or 0) for row in rows)
    data = []
    for row in rows:
        total_penjualan = float(row.total_penjualan or 0)
        data.append(
            {
                "kabupaten_kota_kode": row.kabupaten_kota_kode,
                "kabupaten_kota": row.kabupaten_kota,
                "total_penjualan": total_penjualan,
                "jumlah_transaksi": int(row.jumlah_transaksi or 0),
                "jumlah_petani": int(row.jumlah_petani or 0),
                "persentase": (total_penjualan / grand_total * 100) if grand_total else 0,
            }
        )
    return JSONResponseHandler.success_list(
        data=data,
        label="total penjualan berdasarkan wilayah kabupaten petani",
        message="Total penjualan berdasarkan wilayah kabupaten petani berhasil diambil",
    )


@router.get("/sales/monthly-by-farmer")
def monthly_sales_by_farmer(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    petani_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    year, month = month_columns(Sale.tanggal)
    query = (
        db.query(
            year,
            month,
            Farmer.id.label("farmer_id"),
            Farmer.nama.label("farmer_name"),
            Farmer.nik,
            Farmer.hp,
            func.sum(Sale.sub_total).label("total_penjualan"),
            func.count(Sale.id).label("jumlah_transaksi"),
        )
        .join(Farmer, Sale.penjual_id == Farmer.id)
    )
    if petani_id:
        query = query.filter(Sale.penjual_id == petani_id)
    query = apply_date_filter(query, Sale.tanggal, tanggal_mulai, tanggal_akhir)
    rows = query.group_by(year, month, Farmer.id, Farmer.nama, Farmer.nik, Farmer.hp).order_by(year.asc(), month.asc(), Farmer.nama.asc()).all()
    data = [
        {
            "bulan": month_key(int(row.year), int(row.month)),
            "tahun": int(row.year),
            "bulan_ke": int(row.month),
            "petani": farmer_payload(row.farmer_id, row.farmer_name, row.nik, row.hp),
            "total_penjualan": float(row.total_penjualan or 0),
            "jumlah_transaksi": int(row.jumlah_transaksi or 0),
        }
        for row in rows
    ]
    return JSONResponseHandler.success_list(
        data=data,
        label="penjualan bulan ke bulan berdasarkan petani",
        message="Penjualan bulan ke bulan berdasarkan petani berhasil diambil",
    )


@router.get("/expenses/monthly-by-farmer")
def monthly_expense_by_farmer(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    petani_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    year, month = month_columns(Financing.tanggal)
    query = (
        db.query(
            year,
            month,
            Farmer.id.label("farmer_id"),
            Farmer.nama.label("farmer_name"),
            Farmer.nik,
            Farmer.hp,
            func.sum(Financing.sub_total).label("total_expense"),
            func.count(Financing.id).label("jumlah_transaksi"),
        )
        .join(Farmer, Financing.petani_id == Farmer.id)
    )
    if petani_id:
        query = query.filter(Financing.petani_id == petani_id)
    query = apply_date_filter(query, Financing.tanggal, tanggal_mulai, tanggal_akhir)
    rows = query.group_by(year, month, Farmer.id, Farmer.nama, Farmer.nik, Farmer.hp).order_by(year.asc(), month.asc(), Farmer.nama.asc()).all()
    data = [
        {
            "bulan": month_key(int(row.year), int(row.month)),
            "tahun": int(row.year),
            "bulan_ke": int(row.month),
            "petani": farmer_payload(row.farmer_id, row.farmer_name, row.nik, row.hp),
            "total_expense": float(row.total_expense or 0),
            "jumlah_transaksi": int(row.jumlah_transaksi or 0),
        }
        for row in rows
    ]
    return JSONResponseHandler.success_list(
        data=data,
        label="expense bulan ke bulan berdasarkan petani",
        message="Expense bulan ke bulan berdasarkan petani berhasil diambil",
    )


@router.get("/sales-vs-expenses/monthly")
def monthly_sales_vs_expenses(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    petani_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    sales_rows = sale_monthly_query(db, tanggal_mulai, tanggal_akhir, petani_id=petani_id)
    expense_rows = expense_monthly_query(db, tanggal_mulai, tanggal_akhir, petani_id=petani_id)
    grouped = {}

    for row in sales_rows:
        key = month_key(int(row.year), int(row.month))
        grouped[key] = {
            "bulan": key,
            "tahun": int(row.year),
            "bulan_ke": int(row.month),
            "total_penjualan": float(row.total_penjualan or 0),
            "total_expense": 0,
        }
    for row in expense_rows:
        key = month_key(int(row.year), int(row.month))
        grouped.setdefault(
            key,
            {
                "bulan": key,
                "tahun": int(row.year),
                "bulan_ke": int(row.month),
                "total_penjualan": 0,
                "total_expense": 0,
            },
        )
        grouped[key]["total_expense"] = float(row.total_expense or 0)

    data = []
    for item in sorted(grouped.values(), key=lambda value: (value["tahun"], value["bulan_ke"])):
        item["net_profit"] = item["total_penjualan"] - item["total_expense"]
        data.append(item)

    return JSONResponseHandler.success_list(
        data=data,
        label="penjualan vs expense bulan ke bulan",
        message="Penjualan vs expense bulan ke bulan berhasil diambil",
    )


@router.get("/sales-vs-expenses/by-farmer")
def sales_vs_expenses_by_farmer(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    sales_query = (
        db.query(
            Sale.penjual_id.label("farmer_id"),
            func.sum(Sale.sub_total).label("total_penjualan"),
        )
        .group_by(Sale.penjual_id)
    )
    sales_query = apply_date_filter(sales_query, Sale.tanggal, tanggal_mulai, tanggal_akhir)
    expense_query = (
        db.query(
            Financing.petani_id.label("farmer_id"),
            func.sum(Financing.sub_total).label("total_expense"),
        )
        .group_by(Financing.petani_id)
    )
    expense_query = apply_date_filter(expense_query, Financing.tanggal, tanggal_mulai, tanggal_akhir)

    totals = {}
    for row in sales_query.all():
        totals.setdefault(row.farmer_id, {"total_penjualan": 0, "total_expense": 0})
        totals[row.farmer_id]["total_penjualan"] = float(row.total_penjualan or 0)
    for row in expense_query.all():
        totals.setdefault(row.farmer_id, {"total_penjualan": 0, "total_expense": 0})
        totals[row.farmer_id]["total_expense"] = float(row.total_expense or 0)

    farmers = db.query(Farmer).filter(Farmer.id.in_(list(totals.keys()))).all() if totals else []
    farmer_map = {farmer.id: farmer for farmer in farmers}
    data = []
    for farmer_id, total in totals.items():
        farmer = farmer_map.get(farmer_id)
        data.append(
            {
                "petani": farmer_payload(farmer.id, farmer.nama, farmer.nik, farmer.hp) if farmer else None,
                "total_penjualan": total["total_penjualan"],
                "total_expense": total["total_expense"],
                "net_profit": total["total_penjualan"] - total["total_expense"],
            }
        )
    data.sort(key=lambda item: item["net_profit"], reverse=True)
    return JSONResponseHandler.success_list(
        data=data,
        label="penjualan vs expense berdasarkan petani",
        message="Penjualan vs expense berdasarkan petani berhasil diambil",
    )


@router.get("/farmer-net-profit")
def farmer_net_profit_performance(
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_akhir: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    sales_query = (
        db.query(
            Sale.penjual_id.label("farmer_id"),
            func.sum(Sale.sub_total).label("total_penjualan"),
        )
        .group_by(Sale.penjual_id)
    )
    sales_query = apply_date_filter(sales_query, Sale.tanggal, tanggal_mulai, tanggal_akhir)
    expense_query = (
        db.query(
            Financing.petani_id.label("farmer_id"),
            func.sum(Financing.sub_total).label("total_expense"),
        )
        .group_by(Financing.petani_id)
    )
    expense_query = apply_date_filter(expense_query, Financing.tanggal, tanggal_mulai, tanggal_akhir)

    totals = {}
    for row in sales_query.all():
        totals.setdefault(row.farmer_id, {"total_penjualan": 0, "total_expense": 0})
        totals[row.farmer_id]["total_penjualan"] = float(row.total_penjualan or 0)
    for row in expense_query.all():
        totals.setdefault(row.farmer_id, {"total_penjualan": 0, "total_expense": 0})
        totals[row.farmer_id]["total_expense"] = float(row.total_expense or 0)

    farmers = db.query(Farmer).filter(Farmer.id.in_(list(totals.keys()))).all() if totals else []
    farmer_map = {farmer.id: farmer for farmer in farmers}
    data = []
    for farmer_id, total in totals.items():
        farmer = farmer_map.get(farmer_id)
        data.append(
            {
                "petani": farmer_payload(farmer.id, farmer.nama, farmer.nik, farmer.hp) if farmer else None,
                "total_penjualan": total["total_penjualan"],
                "total_expense": total["total_expense"],
                "net_profit": total["total_penjualan"] - total["total_expense"],
            }
        )
    data.sort(key=lambda item: item["net_profit"], reverse=True)
    return JSONResponseHandler.success_list(
        data=data,
        label="net profit performance petani",
        message="Net profit performance petani berhasil diambil",
    )
