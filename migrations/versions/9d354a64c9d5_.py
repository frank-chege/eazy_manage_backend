"""

Revision ID: 9d354a64c9d5
Revises: 7cffaa5a905d
Create Date: 2024-11-06 00:17:57.939777

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9d354a64c9d5'
down_revision = '7cffaa5a905d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('job_title',
               existing_type=mysql.ENUM('hr', 'developer', 'accountant'),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('job_title',
               existing_type=mysql.ENUM('hr', 'developer', 'accountant'),
               nullable=False)

    # ### end Alembic commands ###