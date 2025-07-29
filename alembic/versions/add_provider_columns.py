"""add provider columns to users

Revision ID: add_provider_columns
Revises: c3a2c4c74f78
Create Date: 2025-07-29 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_provider_columns'
down_revision = 'c3a2c4c74f78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add provider and provider_id columns to users table
    op.add_column('users', sa.Column('provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('provider_id', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove provider and provider_id columns from users table
    op.drop_column('users', 'provider_id')
    op.drop_column('users', 'provider') 