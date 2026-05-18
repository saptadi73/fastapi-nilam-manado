"""create partners

Revision ID: 0013_partners
Revises: 0012_add_paid_by_financings
Create Date: 2026-05-18 18:10:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0013_partners"
down_revision = "0012_add_paid_by_financings"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "partners",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("nama", sa.String(length=150), nullable=False),
        sa.Column("alamat", sa.Text(), nullable=False),
        sa.Column("hp", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("pic", sa.String(length=150), nullable=True),
        sa.Column("web", sa.String(length=255), nullable=True),
        sa.Column("kecamatan_kode", sa.String(length=10), nullable=False),
        sa.Column("kabupaten_kota_kode", sa.String(length=10), nullable=False),
        sa.Column("provinsi_kode", sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(["kecamatan_kode"], ["gis_wilayah.kode"]),
        sa.ForeignKeyConstraint(["kabupaten_kota_kode"], ["gis_wilayah.kode"]),
        sa.ForeignKeyConstraint(["provinsi_kode"], ["gis_wilayah.kode"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_partners_id", "partners", ["id"], unique=False)
    op.create_index("ix_partners_nama", "partners", ["nama"], unique=False)
    op.create_index("ix_partners_kecamatan_kode", "partners", ["kecamatan_kode"], unique=False)
    op.create_index("ix_partners_kabupaten_kota_kode", "partners", ["kabupaten_kota_kode"], unique=False)
    op.create_index("ix_partners_provinsi_kode", "partners", ["provinsi_kode"], unique=False)


def downgrade():
    op.drop_index("ix_partners_provinsi_kode", table_name="partners")
    op.drop_index("ix_partners_kabupaten_kota_kode", table_name="partners")
    op.drop_index("ix_partners_kecamatan_kode", table_name="partners")
    op.drop_index("ix_partners_nama", table_name="partners")
    op.drop_index("ix_partners_id", table_name="partners")
    op.drop_table("partners")
