import os

from fastapi.middleware.cors import CORSMiddleware


def _env_bool(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _cors_origins():
    origins = os.getenv("CORS_ORIGINS")
    if not origins:
        return ["*"]
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


def setup_cors(app):
    if not _env_bool("CORS_ENABLED", default=True):
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
