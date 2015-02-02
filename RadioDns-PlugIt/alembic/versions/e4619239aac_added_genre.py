"""Added genre

Revision ID: e4619239aac
Revises: 33bc6fe131c7
Create Date: 2014-06-03 17:36:12.387714

"""

# revision identifiers, used by Alembic.
revision = 'e4619239aac'
down_revision = '33bc6fe131c7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('station', sa.Column('genres', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('station', 'genres')
    ### end Alembic commands ###