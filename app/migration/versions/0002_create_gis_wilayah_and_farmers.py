"""create gis wilayah and farmers

Revision ID: 0002_gis_farmers
Revises: 0001_create_users_table
Create Date: 2026-05-18 10:10:00
"""

import csv
from pathlib import Path

from alembic import op
import sqlalchemy as sa

revision = "0002_gis_farmers"
down_revision = "0001_create_users_table"
branch_labels = None
depends_on = None


def _wilayah_csv_path():
    return Path(__file__).resolve().parents[2] / "reference" / "gis" / "kode wilayah.csv"


def _wilayah_level(kode):
    levels = {
        2: "provinsi",
        4: "kabupaten_kota",
        6: "kecamatan",
        10: "desa_kelurahan",
    }
    return levels[len(kode)]


def _parent_kode(kode):
    if len(kode) == 2:
        return None
    if len(kode) == 4:
        return kode[:2]
    if len(kode) == 6:
        return kode[:4]
    return kode[:6]


def _load_wilayah_rows():
    csv_path = _wilayah_csv_path()
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        for row in csv.DictReader(csv_file):
            kode = row["kode"].strip()
            yield {
                "kode": kode,
                "nama": row["wilayah"].strip(),
                "level": _wilayah_level(kode),
                "parent_kode": _parent_kode(kode),
            }


def _bulk_insert_wilayah():
    wilayah_table = sa.table(
        "gis_wilayah",
        sa.column("kode", sa.String),
        sa.column("nama", sa.String),
        sa.column("level", sa.String),
        sa.column("parent_kode", sa.String),
    )

    chunk = []
    for row in _load_wilayah_rows():
        chunk.append(row)
        if len(chunk) == 1000:
            op.bulk_insert(wilayah_table, chunk)
            chunk = []

    if chunk:
        op.bulk_insert(wilayah_table, chunk)


def upgrade():
    op.create_table(
        "gis_wilayah",
        sa.Column("kode", sa.String(length=10), nullable=False),
        sa.Column("nama", sa.String(length=150), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("parent_kode", sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint("kode"),
    )
    op.create_index("ix_gis_wilayah_kode", "gis_wilayah", ["kode"], unique=False)
    op.create_index("ix_gis_wilayah_level", "gis_wilayah", ["level"], unique=False)
    op.create_index("ix_gis_wilayah_nama", "gis_wilayah", ["nama"], unique=False)
    op.create_index("ix_gis_wilayah_parent_kode", "gis_wilayah", ["parent_kode"], unique=False)
    _bulk_insert_wilayah()

    op.create_table(
        "farmers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nama", sa.String(length=150), nullable=False),
        sa.Column("nik", sa.String(length=16), nullable=False),
        sa.Column("alamat", sa.String(length=255), nullable=False),
        sa.Column("hp", sa.String(length=30), nullable=True),
        sa.Column("desa_kelurahan_kode", sa.String(length=10), nullable=False),
        sa.Column("kecamatan_kode", sa.String(length=10), nullable=False),
        sa.Column("kabupaten_kota_kode", sa.String(length=10), nullable=False),
        sa.Column("provinsi_kode", sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(["desa_kelurahan_kode"], ["gis_wilayah.kode"]),
        sa.ForeignKeyConstraint(["kecamatan_kode"], ["gis_wilayah.kode"]),
        sa.ForeignKeyConstraint(["kabupaten_kota_kode"], ["gis_wilayah.kode"]),
        sa.ForeignKeyConstraint(["provinsi_kode"], ["gis_wilayah.kode"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nik"),
    )
    op.create_index("ix_farmers_id", "farmers", ["id"], unique=False)
    op.create_index("ix_farmers_nama", "farmers", ["nama"], unique=False)
    op.create_index("ix_farmers_nik", "farmers", ["nik"], unique=True)
    op.create_index("ix_farmers_desa_kelurahan_kode", "farmers", ["desa_kelurahan_kode"], unique=False)
    op.create_index("ix_farmers_kecamatan_kode", "farmers", ["kecamatan_kode"], unique=False)
    op.create_index("ix_farmers_kabupaten_kota_kode", "farmers", ["kabupaten_kota_kode"], unique=False)
    op.create_index("ix_farmers_provinsi_kode", "farmers", ["provinsi_kode"], unique=False)


def downgrade():
    op.drop_index("ix_farmers_provinsi_kode", table_name="farmers")
    op.drop_index("ix_farmers_kabupaten_kota_kode", table_name="farmers")
    op.drop_index("ix_farmers_kecamatan_kode", table_name="farmers")
    op.drop_index("ix_farmers_desa_kelurahan_kode", table_name="farmers")
    op.drop_index("ix_farmers_nik", table_name="farmers")
    op.drop_index("ix_farmers_nama", table_name="farmers")
    op.drop_index("ix_farmers_id", table_name="farmers")
    op.drop_table("farmers")

    op.drop_index("ix_gis_wilayah_parent_kode", table_name="gis_wilayah")
    op.drop_index("ix_gis_wilayah_nama", table_name="gis_wilayah")
    op.drop_index("ix_gis_wilayah_level", table_name="gis_wilayah")
    op.drop_index("ix_gis_wilayah_kode", table_name="gis_wilayah")
    op.drop_table("gis_wilayah")
