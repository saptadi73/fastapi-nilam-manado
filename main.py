from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from app.supports.cors import setup_cors
from app.supports.json_response import JSONResponseHandler

app = FastAPI()

setup_cors(app)


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
from app.services.farmer_service import router as farmer_router
from app.services.wilayah_service import router as wilayah_router

app.include_router(auth_router)
app.include_router(wilayah_router)
app.include_router(farmer_router)
