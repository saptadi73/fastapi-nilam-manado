"""add oil production user update

Revision ID: 0009_oil_user_update
Revises: 0008_oil_productions
Create Date: 2026-05-18 13:25:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_oil_user_update"
down_revision = "0008_oil_productions"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("oil_productions", sa.Column("user_update_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_oil_productions_user_update_id", "oil_productions", "users", ["user_update_id"], ["id"])
    op.create_index("ix_oil_productions_user_update_id", "oil_productions", ["user_update_id"], unique=False)


def downgrade():
    op.drop_index("ix_oil_productions_user_update_id", table_name="oil_productions")
    op.drop_constraint("fk_oil_productions_user_update_id", "oil_productions", type_="foreignkey")
    op.drop_column("oil_productions", "user_update_id")
