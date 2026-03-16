"""add moscow_facts to contenttype enum

Revision ID: 002_moscow_facts
Revises: 001_init
Create Date: 2026-03-16

"""

from alembic import op


revision = "002_moscow_facts"
down_revision = "001_init"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE contenttype ADD VALUE IF NOT EXISTS 'moscow_facts'")


def downgrade():
    pass
