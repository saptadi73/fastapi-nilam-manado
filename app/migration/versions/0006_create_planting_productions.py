"""create planting productions

Revision ID: 0006_planting_productions
Revises: 0005_land_elevation
Create Date: 2026-05-18 12:05:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006_planting_productions"
down_revision = "0005_land_elevation"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "planting_productions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("kode", sa.String(length=50), nullable=False),
        sa.Column("tanggal_mulai", sa.Date(), nullable=False),
        sa.Column("tanggal_akhir", sa.Date(), nullable=True),
        sa.Column("aktual_tanggal_akhir", sa.Date(), nullable=True),
        sa.Column("luas_garapan", sa.Float(), nullable=False),
        sa.Column("jarak_tanam", sa.String(length=50), nullable=True),
        sa.Column("jumlah_batang", sa.Integer(), nullable=True),
        sa.Column("hasil_produksi_basah", sa.Float(), nullable=True),
        sa.Column("aktual_hasil_produksi_basah", sa.Float(), nullable=True),
        sa.Column("aktual_hasil_produksi_kering", sa.Float(), nullable=True),
        sa.Column("varietas_bibit", sa.String(length=100), nullable=True),
        sa.Column("sumber_bibit", sa.String(length=150), nullable=True),
        sa.Column("cara_tanam", sa.String(length=150), nullable=True),
        sa.Column("perawatan", sa.Text(), nullable=True),
        sa.Column("pupuk", sa.Text(), nullable=True),
        sa.Column("musim_tanam", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("petani_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lahan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rasio_berat_kering_ke_basah", sa.Float(), nullable=True),
        sa.Column("rasio_luas_garapan_ke_hasil_kering", sa.Float(), nullable=True),
        sa.Column("user_update_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["lahan_id"], ["lands.id"]),
        sa.ForeignKeyConstraint(["petani_id"], ["farmers.id"]),
        sa.ForeignKeyConstraint(["user_update_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kode"),
    )
    op.create_index("ix_planting_productions_id", "planting_productions", ["id"], unique=False)
    op.create_index("ix_planting_productions_kode", "planting_productions", ["kode"], unique=True)
    op.create_index("ix_planting_productions_lahan_id", "planting_productions", ["lahan_id"], unique=False)
    op.create_index("ix_planting_productions_petani_id", "planting_productions", ["petani_id"], unique=False)
    op.create_index("ix_planting_productions_status", "planting_productions", ["status"], unique=False)
    op.create_index("ix_planting_productions_user_update_id", "planting_productions", ["user_update_id"], unique=False)


def downgrade():
    op.drop_index("ix_planting_productions_user_update_id", table_name="planting_productions")
    op.drop_index("ix_planting_productions_status", table_name="planting_productions")
    op.drop_index("ix_planting_productions_petani_id", table_name="planting_productions")
    op.drop_index("ix_planting_productions_lahan_id", table_name="planting_productions")
    op.drop_index("ix_planting_productions_kode", table_name="planting_productions")
    op.drop_index("ix_planting_productions_id", table_name="planting_productions")
    op.drop_table("planting_productions")
