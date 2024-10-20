"""deleted team column

Revision ID: 73e8b7b0431d
Revises: b11283b93ef3
Create Date: 2024-10-20 12:21:49.985113

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '73e8b7b0431d'
down_revision = 'b11283b93ef3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_column('team')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('team', mysql.VARCHAR(length=255), nullable=False))

    # ### end Alembic commands ###