"""add role to users

Revision ID: 0020_add_user_role
Revises: 0019_oil_refinery_fields
Create Date: 2026-09-17
"""

from alembic import op
import sqlalchemy as sa


revision = "0020_add_user_role"
down_revision = "0019_oil_refinery_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), nullable=True, server_default="ADMIN"),
    )
    # Semua akun yang sudah ada harus memiliki akses admin.
    op.execute("UPDATE users SET role = 'ADMIN'")
    op.alter_column("users", "role", nullable=False, server_default="ADMIN")
    op.create_check_constraint(
        "ck_users_role_valid",
        "users",
        "role IN ('ADMIN', 'OFFICER', 'USER')",
    )


def downgrade():
    op.drop_constraint("ck_users_role_valid", "users", type_="check")
    op.drop_column("users", "role")
