"""ServiceProvider update XSI 3

Revision ID: 177aa1fdf479
Revises: 2d5b0c8383e0
Create Date: 2015-05-30 13:13:52.223615

"""

# revision identifiers, used by Alembic.
revision = '177aa1fdf479'
down_revision = '2d5b0c8383e0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_provider', sa.Column('city', sa.String(length=255), nullable=True))
    op.add_column('service_provider', sa.Column('keywords', sa.String(length=255), nullable=True))
    op.add_column('service_provider', sa.Column('phone_number', sa.String(length=128), nullable=True))
    op.add_column('service_provider', sa.Column('postal_name', sa.String(length=255), nullable=True))
    op.add_column('service_provider', sa.Column('street', sa.String(length=255), nullable=True))
    op.add_column('service_provider', sa.Column('zipcode', sa.String(length=25), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service_provider', 'zipcode')
    op.drop_column('service_provider', 'street')
    op.drop_column('service_provider', 'postal_name')
    op.drop_column('service_provider', 'phone_number')
    op.drop_column('service_provider', 'keywords')
    op.drop_column('service_provider', 'city')
    ### end Alembic commands ###