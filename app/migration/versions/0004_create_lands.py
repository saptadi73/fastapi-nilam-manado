"""create lands

Revision ID: 0004_lands
Revises: 0003_farmer_photo
Create Date: 2026-05-18 11:10:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_lands"
down_revision = "0003_farmer_photo"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lands",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("kode", sa.String(length=50), nullable=False),
        sa.Column("luas", sa.Float(), nullable=False),
        sa.Column("kepemilikan", sa.String(length=20), nullable=False),
        sa.Column("pemilik_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("foto_path", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["pemilik_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kode"),
    )
    op.create_index("ix_lands_id", "lands", ["id"], unique=False)
    op.create_index("ix_lands_kode", "lands", ["kode"], unique=True)
    op.create_index("ix_lands_kepemilikan", "lands", ["kepemilikan"], unique=False)
    op.create_index("ix_lands_pemilik_id", "lands", ["pemilik_id"], unique=False)

    op.create_table(
        "land_coordinates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("land_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("urutan", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["land_id"], ["lands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_land_coordinates_id", "land_coordinates", ["id"], unique=False)
    op.create_index("ix_land_coordinates_land_id", "land_coordinates", ["land_id"], unique=False)


def downgrade():
    op.drop_index("ix_land_coordinates_land_id", table_name="land_coordinates")
    op.drop_index("ix_land_coordinates_id", table_name="land_coordinates")
    op.drop_table("land_coordinates")

    op.drop_index("ix_lands_pemilik_id", table_name="lands")
    op.drop_index("ix_lands_kepemilikan", table_name="lands")
    op.drop_index("ix_lands_kode", table_name="lands")
    op.drop_index("ix_lands_id", table_name="lands")
    op.drop_table("lands")
