from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.supports.cors import setup_cors
from app.supports.json_response import JSONResponseHandler

app = FastAPI()

setup_cors(app)
Path("uploads").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponseHandler.error(
        message=exc.detail,
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponseHandler.error(
        message="Validation error",
        data=exc.errors(),
        status_code=422,
    )


@app.get("/")
def read_root():
    return JSONResponseHandler.success(
        message="Nilam ERP API is running",
        data={"service": "fastapi-nilam-manado"},
    )


# Import dan include router autentikasi
from app.services.auth_service import router as auth_router
from app.services.dashboard_service import router as dashboard_router
from app.services.farmer_service import router as farmer_router
from app.services.financing_service import product_router as financing_product_router
from app.services.financing_service import router as financing_router
from app.services.land_service import router as land_router
from app.services.oil_production_service import router as oil_production_router
from app.services.partner_service import router as partner_router
from app.services.planting_production_service import router as planting_production_router
from app.services.production_note_service import (
    oil_note_router,
    planting_note_router,
)
from app.services.sales_service import product_router as sales_product_router
from app.services.sales_service import router as sales_router
from app.services.wilayah_service import router as wilayah_router

routers = (
    auth_router,
    dashboard_router,
    wilayah_router,
    farmer_router,
    partner_router,
    financing_product_router,
    financing_router,
    sales_product_router,
    sales_router,
    land_router,
    planting_production_router,
    oil_production_router,
    planting_note_router,
    oil_note_router,
)

for router in routers:
    app.include_router(router)
    app.include_router(router, prefix="/api")
