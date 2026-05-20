"""add harga and satuan to financing_products

Revision ID: 0017_financing_product_fields
Revises: 0016_add_jenis_sales_products
Create Date: 2026-05-18 19:45:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0017_financing_product_fields"
down_revision = "0016_add_jenis_sales_products"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "financing_products",
        sa.Column("harga", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "financing_products",
        sa.Column("satuan", sa.String(length=50), nullable=False, server_default="unit"),
    )
    op.alter_column("financing_products", "harga", server_default=None)
    op.alter_column("financing_products", "satuan", server_default=None)


def downgrade():
    op.drop_column("financing_products", "satuan")
    op.drop_column("financing_products", "harga")
