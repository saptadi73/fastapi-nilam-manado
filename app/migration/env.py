from logging.config import fileConfig
from typing import Any, Dict, cast

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.database import DATABASE_URL
from app.models import Base

config = context.config
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    section = config.get_section(config.config_ini_section) or {}
    configuration = cast(Dict[str, Any], section)

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
