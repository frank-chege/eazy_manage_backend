"""changed enum for status column in tasks

Revision ID: 54108ed9c628
Revises: 73e8b7b0431d
Create Date: 2024-10-20 23:54:15.407816

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '54108ed9c628'
down_revision = '73e8b7b0431d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.ENUM('pending', 'complete'),
               type_=sa.Enum('pending', 'completed'),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.Enum('pending', 'completed'),
               type_=mysql.ENUM('pending', 'complete'),
               existing_nullable=True)

    # ### end Alembic commands ###
