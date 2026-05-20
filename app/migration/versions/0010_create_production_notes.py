"""create production notes

Revision ID: 0010_production_notes
Revises: 0009_oil_user_update
Create Date: 2026-05-18 13:45:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_production_notes"
down_revision = "0009_oil_user_update"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "planting_production_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("kode_produksi", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tanggal", sa.Date(), nullable=False),
        sa.Column("catatan", sa.Text(), nullable=False),
        sa.Column("user_update_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["kode_produksi"], ["planting_productions.id"]),
        sa.ForeignKeyConstraint(["user_update_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_planting_production_notes_id", "planting_production_notes", ["id"], unique=False)
    op.create_index("ix_planting_production_notes_kode_produksi", "planting_production_notes", ["kode_produksi"], unique=False)
    op.create_index("ix_planting_production_notes_tanggal", "planting_production_notes", ["tanggal"], unique=False)
    op.create_index("ix_planting_production_notes_user_update_id", "planting_production_notes", ["user_update_id"], unique=False)

    op.create_table(
        "oil_production_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("kode_produksi", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tanggal", sa.Date(), nullable=False),
        sa.Column("catatan", sa.Text(), nullable=False),
        sa.Column("user_update_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["kode_produksi"], ["oil_productions.id"]),
        sa.ForeignKeyConstraint(["user_update_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_oil_production_notes_id", "oil_production_notes", ["id"], unique=False)
    op.create_index("ix_oil_production_notes_kode_produksi", "oil_production_notes", ["kode_produksi"], unique=False)
    op.create_index("ix_oil_production_notes_tanggal", "oil_production_notes", ["tanggal"], unique=False)
    op.create_index("ix_oil_production_notes_user_update_id", "oil_production_notes", ["user_update_id"], unique=False)


def downgrade():
    op.drop_index("ix_oil_production_notes_user_update_id", table_name="oil_production_notes")
    op.drop_index("ix_oil_production_notes_tanggal", table_name="oil_production_notes")
    op.drop_index("ix_oil_production_notes_kode_produksi", table_name="oil_production_notes")
    op.drop_index("ix_oil_production_notes_id", table_name="oil_production_notes")
    op.drop_table("oil_production_notes")

    op.drop_index("ix_planting_production_notes_user_update_id", table_name="planting_production_notes")
    op.drop_index("ix_planting_production_notes_tanggal", table_name="planting_production_notes")
    op.drop_index("ix_planting_production_notes_kode_produksi", table_name="planting_production_notes")
    op.drop_index("ix_planting_production_notes_id", table_name="planting_production_notes")
    op.drop_table("planting_production_notes")
