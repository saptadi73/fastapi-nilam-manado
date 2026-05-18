"""add land elevation

Revision ID: 0005_land_elevation
Revises: 0004_lands
Create Date: 2026-05-18 11:35:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_land_elevation"
down_revision = "0004_lands"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("lands", sa.Column("elevasi", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("lands", "elevasi")
