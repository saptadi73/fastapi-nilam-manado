"""add jenis to sales_products

Revision ID: 0016_add_jenis_sales_products
Revises: 0015_sales
Create Date: 2026-05-18 19:20:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0016_add_jenis_sales_products"
down_revision = "0015_sales"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sales_products",
        sa.Column("jenis", sa.String(length=20), nullable=False, server_default="barang"),
    )
    op.create_index("ix_sales_products_jenis", "sales_products", ["jenis"], unique=False)
    op.alter_column("sales_products", "jenis", server_default=None)


def downgrade():
    op.drop_index("ix_sales_products_jenis", table_name="sales_products")
    op.drop_column("sales_products", "jenis")
