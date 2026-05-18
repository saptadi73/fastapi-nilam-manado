"""add farmer photo

Revision ID: 0003_farmer_photo
Revises: 0002_gis_farmers
Create Date: 2026-05-18 10:45:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_farmer_photo"
down_revision = "0002_gis_farmers"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("farmers", sa.Column("foto_path", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("farmers", "foto_path")
