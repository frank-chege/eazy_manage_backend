"""initial migration

Revision ID: ed0e14bad3d4
Revises: 
Create Date: 2024-11-05 23:32:27.019648

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ed0e14bad3d4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('employeestotal', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('email', sa.String(length=255), nullable=False))
        batch_op.drop_index('org_email')
        batch_op.create_unique_constraint(None, ['email'])
        batch_op.drop_column('org_name')
        batch_op.drop_column('org_email')
        batch_op.drop_column('employees_total')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('employees_total', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('org_email', mysql.VARCHAR(length=255), nullable=False))
        batch_op.add_column(sa.Column('org_name', mysql.VARCHAR(length=255), nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_index('org_email', ['org_email'], unique=True)
        batch_op.drop_column('email')
        batch_op.drop_column('employeestotal')
        batch_op.drop_column('name')

    # ### end Alembic commands ###
