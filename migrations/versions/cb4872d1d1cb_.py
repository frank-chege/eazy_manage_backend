"""

Revision ID: cb4872d1d1cb
Revises: de7d9afd628a
Create Date: 2024-11-06 00:11:35.073048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb4872d1d1cb'
down_revision = 'de7d9afd628a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.alter_column('address',
               existing_type=sa.DATE(),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.alter_column('address',
               existing_type=sa.String(length=255),
               type_=sa.DATE(),
               existing_nullable=False)

    # ### end Alembic commands ###