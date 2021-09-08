"""added multicast identifier (mid) to hd channel spec

Revision ID: 3bbfede9cb1b
Revises: 2c1baff71070
Create Date: 2019-05-28 10:41:20.579904

"""

# revision identifiers, used by Alembic.
revision = '3bbfede9cb1b'
down_revision = '2c1baff71070'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('channel', sa.Column('mid', sa.Integer(), nullable=True))
    ### end Alembic commands ###

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('channel', 'mid')
    ### end Alembic commands ###