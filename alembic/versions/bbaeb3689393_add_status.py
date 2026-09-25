"""Add status

Revision ID: bbaeb3689393
Revises: 55d144ce9cb0
Create Date: 2026-XX-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'bbaeb3689393'
down_revision = '55d144ce9cb0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    moviestatus_enum = postgresql.ENUM(
        "PENDING", "APPROVED", "NOT_APPROVED", name="moviestatus"
    )
    moviestatus_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "movies",
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING", "APPROVED", "NOT_APPROVED", name="moviestatus", create_type=False
            ),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("movies", "status")
    postgresql.ENUM(name="moviestatus").drop(op.get_bind(), checkfirst=True)