"""add partner to financings

Revision ID: 0014_add_partner_to_financings
Revises: 0013_partners
Create Date: 2026-05-18 18:35:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0014_add_partner_to_financings"
down_revision = "0013_partners"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("financings", sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_financings_partner_id_partners", "financings", "partners", ["partner_id"], ["id"])
    op.create_index("ix_financings_partner_id", "financings", ["partner_id"], unique=False)


def downgrade():
    op.drop_index("ix_financings_partner_id", table_name="financings")
    op.drop_constraint("fk_financings_partner_id_partners", "financings", type_="foreignkey")
    op.drop_column("financings", "partner_id")
