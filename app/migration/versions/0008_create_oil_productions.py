"""create oil productions

Revision ID: 0008_oil_productions
Revises: 0007_land_regions
Create Date: 2026-05-18 13:05:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_oil_productions"
down_revision = "0007_land_regions"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "oil_productions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("kode", sa.String(length=50), nullable=False),
        sa.Column("tanggal_mulai", sa.Date(), nullable=False),
        sa.Column("tanggal_akhir", sa.Date(), nullable=True),
        sa.Column("aktual_tanggal_akhir", sa.Date(), nullable=True),
        sa.Column("berat_kering_bahan", sa.Float(), nullable=True),
        sa.Column("hasil_minyak", sa.Float(), nullable=True),
        sa.Column("aktual_hasil_minyak", sa.Float(), nullable=True),
        sa.Column("redaman", sa.Float(), nullable=True),
        sa.Column("petani_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lahan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["lahan_id"], ["lands.id"]),
        sa.ForeignKeyConstraint(["petani_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kode"),
    )
    op.create_index("ix_oil_productions_id", "oil_productions", ["id"], unique=False)
    op.create_index("ix_oil_productions_kode", "oil_productions", ["kode"], unique=True)
    op.create_index("ix_oil_productions_lahan_id", "oil_productions", ["lahan_id"], unique=False)
    op.create_index("ix_oil_productions_petani_id", "oil_productions", ["petani_id"], unique=False)
    op.create_index("ix_oil_productions_status", "oil_productions", ["status"], unique=False)


def downgrade():
    op.drop_index("ix_oil_productions_status", table_name="oil_productions")
    op.drop_index("ix_oil_productions_petani_id", table_name="oil_productions")
    op.drop_index("ix_oil_productions_lahan_id", table_name="oil_productions")
    op.drop_index("ix_oil_productions_kode", table_name="oil_productions")
    op.drop_index("ix_oil_productions_id", table_name="oil_productions")
    op.drop_table("oil_productions")
