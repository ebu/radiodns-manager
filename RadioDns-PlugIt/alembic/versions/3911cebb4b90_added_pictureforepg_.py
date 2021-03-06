"""Added PictureForEPG 3

Revision ID: 3911cebb4b90
Revises: 18287b7e1999
Create Date: 2014-06-03 14:44:07.884806

"""

# revision identifiers, used by Alembic.
revision = '3911cebb4b90'
down_revision = '18287b7e1999'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('channel', sa.Column('epg_picture_id', sa.Integer(), nullable=True))
    op.drop_column('channel', u'epg_picture')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('channel', sa.Column(u'epg_picture', mysql.INTEGER(display_width=11), nullable=True))
    op.drop_column('channel', 'epg_picture_id')
    ### end Alembic commands ###
