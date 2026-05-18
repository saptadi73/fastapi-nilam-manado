from fastapi import FastAPI
from app.supports.cors import setup_cors
from app.database import engine
from app.models.user import Base

app = FastAPI()

setup_cors(app)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


# Import dan include router autentikasi
from app.services.auth_service import router as auth_router
app.include_router(auth_router)
