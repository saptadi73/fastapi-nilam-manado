"""create sales and sales_products

Revision ID: 0015_sales
Revises: 0014_add_partner_to_financings
Create Date: 2026-05-18 19:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0015_sales"
down_revision = "0014_add_partner_to_financings"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sales_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("nama", sa.String(length=150), nullable=False),
        sa.Column("harga", sa.Float(), nullable=False),
        sa.Column("satuan", sa.String(length=50), nullable=False),
        sa.Column("deskripsi", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nama"),
    )
    op.create_index("ix_sales_products_id", "sales_products", ["id"], unique=False)
    op.create_index("ix_sales_products_nama", "sales_products", ["nama"], unique=True)

    op.create_table(
        "sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("nama", sa.String(length=150), nullable=False),
        sa.Column("tanggal", sa.Date(), nullable=False),
        sa.Column("deskripsi", sa.Text(), nullable=True),
        sa.Column("produk_penjualan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("harga", sa.Float(), nullable=False),
        sa.Column("penjual_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pembeli_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sub_total", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["produk_penjualan_id"], ["sales_products.id"]),
        sa.ForeignKeyConstraint(["penjual_id"], ["farmers.id"]),
        sa.ForeignKeyConstraint(["pembeli_id"], ["partners.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sales_id", "sales", ["id"], unique=False)
    op.create_index("ix_sales_nama", "sales", ["nama"], unique=False)
    op.create_index("ix_sales_tanggal", "sales", ["tanggal"], unique=False)
    op.create_index("ix_sales_produk_penjualan_id", "sales", ["produk_penjualan_id"], unique=False)
    op.create_index("ix_sales_penjual_id", "sales", ["penjual_id"], unique=False)
    op.create_index("ix_sales_pembeli_id", "sales", ["pembeli_id"], unique=False)


def downgrade():
    op.drop_index("ix_sales_pembeli_id", table_name="sales")
    op.drop_index("ix_sales_penjual_id", table_name="sales")
    op.drop_index("ix_sales_produk_penjualan_id", table_name="sales")
    op.drop_index("ix_sales_tanggal", table_name="sales")
    op.drop_index("ix_sales_nama", table_name="sales")
    op.drop_index("ix_sales_id", table_name="sales")
    op.drop_table("sales")

    op.drop_index("ix_sales_products_nama", table_name="sales_products")
    op.drop_index("ix_sales_products_id", table_name="sales_products")
    op.drop_table("sales_products")
