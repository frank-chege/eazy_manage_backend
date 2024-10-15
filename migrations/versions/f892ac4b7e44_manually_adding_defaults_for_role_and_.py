"""Manually adding defaults for role and status

Revision ID: f892ac4b7e44
Revises: e7743404509b
Create Date: 2024-10-15 21:57:36.215341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f892ac4b7e44'
down_revision = 'e7743404509b'
branch_labels = None
depends_on = None

def upgrade():
    # Add server default to the 'role' column
    op.alter_column(
        'users', 
        'role', 
        existing_type=sa.Enum('admin', 'user'), 
        server_default='user', 
        nullable=False
    )

    # Add server default to the 'status' column
    op.alter_column(
        'users', 
        'status', 
        existing_type=sa.Enum('active', 'leave', 'inactive'), 
        server_default='active', 
        nullable=False
    )

def downgrade():
    # Remove the server default on downgrade
    op.alter_column('users', 'role', server_default=None)
    op.alter_column('users', 'status', server_default=None)

