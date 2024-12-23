"""change org column names

Revision ID: 9541b61356bd
Revises: ed0e14bad3d4
Create Date: 2024-11-05 23:35:23.373960

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9541b61356bd'
down_revision = 'ed0e14bad3d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('employees_total', sa.Integer(), nullable=False))
        batch_op.drop_column('employeestotal')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('employeestotal', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_column('employees_total')

    # ### end Alembic commands ###
