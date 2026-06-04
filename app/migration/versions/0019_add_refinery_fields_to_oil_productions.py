"""add refinery fields to oil productions

Revision ID: 0019_oil_refinery_fields
Revises: 0018_user_update_master_sales
Create Date: 2026-06-04 13:10:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0019_oil_refinery_fields"
down_revision = "0018_user_update_master_sales"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("oil_productions", sa.Column("tempat_penyulingan", sa.String(length=255), nullable=True))
    op.add_column("oil_productions", sa.Column("harga_penyulingan_per_kg", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("oil_productions", "harga_penyulingan_per_kg")
    op.drop_column("oil_productions", "tempat_penyulingan")
