"""add default role to users

Revision ID: add_default_role_to_users
Revises: d54c5b37d5d2
Create Date: 2025-11-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_default_role_to_users"
down_revision = "d54c5b37d5d2"   # <-- setze hier die tatsächliche vorherige revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Set role_id to 2 for existing rows that are NULL
    op.execute("UPDATE users SET role_id = 2 WHERE role_id IS NULL;")

    # 2) Alter the column to have a server_default (Postgres expects text)
    op.alter_column(
        "users",
        "role_id",
        existing_type=sa.Integer(),
        server_default=sa.text("2"),
        existing_nullable=False,
    )


def downgrade() -> None:
    # remove the server_default (do not change existing values)
    op.alter_column(
        "users",
        "role_id",
        existing_type=sa.Integer(),
        server_default=None,
        existing_nullable=False,
    )
