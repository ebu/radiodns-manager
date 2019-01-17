"""Added spi enabled and service columns to station

Revision ID: 005f84c40e24
Revises: 1144b3a7bfc2
Create Date: 2018-10-08 09:49:14.926062
Author: Ioannis Noukakis (inoukakis@gmail.com)

"""

# revision identifiers, used by Alembic.
revision = '005f84c40e24'
down_revision = '1144b3a7bfc2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('station',
                  sa.Column('radiospi_enabled', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('station', sa.Column('radiospi_service', mysql.VARCHAR(length=255), nullable=True))


def downgrade():
    op.drop_column('station', 'radiospi_enabled')
    op.drop_column('station', 'radiospi_service')
