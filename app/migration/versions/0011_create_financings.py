"""create financings

Revision ID: 0011_financings
Revises: 0010_production_notes
Create Date: 2026-05-18 14:15:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_financings"
down_revision = "0010_production_notes"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "financing_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("nama", sa.String(length=150), nullable=False),
        sa.Column("deskripsi", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nama"),
    )
    op.create_index("ix_financing_products_id", "financing_products", ["id"], unique=False)
    op.create_index("ix_financing_products_nama", "financing_products", ["nama"], unique=True)

    op.create_table(
        "financings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("nama", sa.String(length=150), nullable=False),
        sa.Column("tanggal", sa.Date(), nullable=False),
        sa.Column("deskripsi", sa.Text(), nullable=True),
        sa.Column("produk_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("harga", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("petani_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("planting_production_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("oil_production_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sub_total", sa.Float(), nullable=False),
        sa.Column("user_update_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["oil_production_id"], ["oil_productions.id"]),
        sa.ForeignKeyConstraint(["petani_id"], ["farmers.id"]),
        sa.ForeignKeyConstraint(["planting_production_id"], ["planting_productions.id"]),
        sa.ForeignKeyConstraint(["produk_id"], ["financing_products.id"]),
        sa.ForeignKeyConstraint(["user_update_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_financings_id", "financings", ["id"], unique=False)
    op.create_index("ix_financings_nama", "financings", ["nama"], unique=False)
    op.create_index("ix_financings_tanggal", "financings", ["tanggal"], unique=False)
    op.create_index("ix_financings_produk_id", "financings", ["produk_id"], unique=False)
    op.create_index("ix_financings_petani_id", "financings", ["petani_id"], unique=False)
    op.create_index("ix_financings_planting_production_id", "financings", ["planting_production_id"], unique=False)
    op.create_index("ix_financings_oil_production_id", "financings", ["oil_production_id"], unique=False)
    op.create_index("ix_financings_user_update_id", "financings", ["user_update_id"], unique=False)


def downgrade():
    op.drop_index("ix_financings_user_update_id", table_name="financings")
    op.drop_index("ix_financings_oil_production_id", table_name="financings")
    op.drop_index("ix_financings_planting_production_id", table_name="financings")
    op.drop_index("ix_financings_petani_id", table_name="financings")
    op.drop_index("ix_financings_produk_id", table_name="financings")
    op.drop_index("ix_financings_tanggal", table_name="financings")
    op.drop_index("ix_financings_nama", table_name="financings")
    op.drop_index("ix_financings_id", table_name="financings")
    op.drop_table("financings")

    op.drop_index("ix_financing_products_nama", table_name="financing_products")
    op.drop_index("ix_financing_products_id", table_name="financing_products")
    op.drop_table("financing_products")
