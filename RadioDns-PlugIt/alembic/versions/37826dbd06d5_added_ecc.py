"""Added ECC

Revision ID: 37826dbd06d5
Revises: 79cf16aef0b
Create Date: 2013-08-05 17:35:03.326000

"""

# revision identifiers, used by Alembic.
revision = '37826dbd06d5'
down_revision = '79cf16aef0b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ecc',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('iso', sa.String(length=2), nullable=True),
    sa.Column('pi', sa.String(length=2), nullable=True),
    sa.Column('ecc', sa.String(length=3), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ecc')
    ### end Alembic commands ###