"""create users table

Revision ID: 0001_create_users_table
Revises: None
Create Date: 2026-05-18 09:45:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0001_create_users_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "users" not in inspector.get_table_names():
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("password", sa.String(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_users_id", "users", ["id"], unique=False)
        op.create_index("ix_users_name", "users", ["name"], unique=False)
        op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "users" in inspector.get_table_names():
        op.drop_index("ix_users_email", table_name="users")
        op.drop_index("ix_users_name", table_name="users")
        op.drop_index("ix_users_id", table_name="users")
        op.drop_table("users")
