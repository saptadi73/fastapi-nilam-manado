"""add paid_by to financings

Revision ID: 0012_add_paid_by_financings
Revises: 0011_financings
Create Date: 2026-05-18 17:20:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0012_add_paid_by_financings"
down_revision = "0011_financings"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("financings", sa.Column("paid_by", sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column("financings", "paid_by")
