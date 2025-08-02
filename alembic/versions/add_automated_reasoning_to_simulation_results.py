"""Add automated_reasoning to simulation_results table

Revision ID: add_automated_reasoning_to_simulation_results
Revises: add_user_id_to_simulation_results
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_automated_reasoning_to_simulation_results'
down_revision = 'add_user_id_to_simulation_results'
branch_labels = None
depends_on = None


def upgrade():
    # Add automated_reasoning column to simulation_results table
    op.add_column('simulation_results', sa.Column('automated_reasoning', sa.Text(), nullable=True))


def downgrade():
    # Remove automated_reasoning column
    op.drop_column('simulation_results', 'automated_reasoning') 