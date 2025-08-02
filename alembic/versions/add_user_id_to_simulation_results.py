"""Add user_id to simulation_results table

Revision ID: add_user_id_to_simulation_results
Revises: add_simulation_results_table
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_id_to_simulation_results'
down_revision = 'add_simulation_results_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add user_id column to simulation_results table
    op.add_column('simulation_results', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Create index on user_id for better query performance
    op.create_index(op.f('ix_simulation_results_user_id'), 'simulation_results', ['user_id'], unique=False)
    
    # Make user_id not nullable after adding it (if you want to enforce it)
    # op.alter_column('simulation_results', 'user_id', nullable=False)


def downgrade():
    # Remove index
    op.drop_index(op.f('ix_simulation_results_user_id'), table_name='simulation_results')
    
    # Remove user_id column
    op.drop_column('simulation_results', 'user_id') 