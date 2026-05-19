"""add user_update to master and sales tables

Revision ID: 0018_user_update_master_sales
Revises: 0017_financing_product_fields
Create Date: 2026-05-19 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0018_user_update_master_sales"
down_revision = "0017_financing_product_fields"
branch_labels = None
depends_on = None


TABLES = [
    "farmers",
    "lands",
    "partners",
    "financing_products",
    "sales_products",
    "sales",
]


def upgrade():
    for table in TABLES:
        op.add_column(
            table,
            sa.Column("user_update_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.create_foreign_key(
            f"fk_{table}_user_update_id_users",
            table,
            "users",
            ["user_update_id"],
            ["id"],
        )
        op.create_index(f"ix_{table}_user_update_id", table, ["user_update_id"], unique=False)


def downgrade():
    for table in reversed(TABLES):
        op.drop_index(f"ix_{table}_user_update_id", table_name=table)
        op.drop_constraint(f"fk_{table}_user_update_id_users", table, type_="foreignkey")
        op.drop_column(table, "user_update_id")
