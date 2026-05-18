"""add land regions

Revision ID: 0007_land_regions
Revises: 0006_planting_productions
Create Date: 2026-05-18 12:35:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_land_regions"
down_revision = "0006_planting_productions"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("lands", sa.Column("desa_kelurahan_kode", sa.String(length=10), nullable=True))
    op.add_column("lands", sa.Column("kecamatan_kode", sa.String(length=10), nullable=True))
    op.add_column("lands", sa.Column("kabupaten_kota_kode", sa.String(length=10), nullable=True))
    op.add_column("lands", sa.Column("provinsi_kode", sa.String(length=10), nullable=True))
    op.create_foreign_key("fk_lands_desa_kelurahan_kode", "lands", "gis_wilayah", ["desa_kelurahan_kode"], ["kode"])
    op.create_foreign_key("fk_lands_kecamatan_kode", "lands", "gis_wilayah", ["kecamatan_kode"], ["kode"])
    op.create_foreign_key("fk_lands_kabupaten_kota_kode", "lands", "gis_wilayah", ["kabupaten_kota_kode"], ["kode"])
    op.create_foreign_key("fk_lands_provinsi_kode", "lands", "gis_wilayah", ["provinsi_kode"], ["kode"])
    op.create_index("ix_lands_desa_kelurahan_kode", "lands", ["desa_kelurahan_kode"], unique=False)
    op.create_index("ix_lands_kecamatan_kode", "lands", ["kecamatan_kode"], unique=False)
    op.create_index("ix_lands_kabupaten_kota_kode", "lands", ["kabupaten_kota_kode"], unique=False)
    op.create_index("ix_lands_provinsi_kode", "lands", ["provinsi_kode"], unique=False)


def downgrade():
    op.drop_index("ix_lands_provinsi_kode", table_name="lands")
    op.drop_index("ix_lands_kabupaten_kota_kode", table_name="lands")
    op.drop_index("ix_lands_kecamatan_kode", table_name="lands")
    op.drop_index("ix_lands_desa_kelurahan_kode", table_name="lands")
    op.drop_constraint("fk_lands_provinsi_kode", "lands", type_="foreignkey")
    op.drop_constraint("fk_lands_kabupaten_kota_kode", "lands", type_="foreignkey")
    op.drop_constraint("fk_lands_kecamatan_kode", "lands", type_="foreignkey")
    op.drop_constraint("fk_lands_desa_kelurahan_kode", "lands", type_="foreignkey")
    op.drop_column("lands", "provinsi_kode")
    op.drop_column("lands", "kabupaten_kota_kode")
    op.drop_column("lands", "kecamatan_kode")
    op.drop_column("lands", "desa_kelurahan_kode")
