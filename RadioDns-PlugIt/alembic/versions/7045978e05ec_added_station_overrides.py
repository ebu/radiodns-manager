"""added station overrides

Revision ID: 7045978e05ec
Revises: b1f1f87a08d8
Create Date: 2018-10-15 09:45:24.256760

"""

# revision identifiers, used by Alembic.
revision = '7045978e05ec'
down_revision = 'b1f1f87a08d8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('station', sa.Column('parent', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('station',
                  sa.Column('fk_client', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key(u'station_clients_id_fk', 'station', 'clients', ['fk_client'], ['id'], ondelete=u'CASCADE')
    op.create_foreign_key(u'station_station_id_fk', 'station', 'station', ['parent'], ['id'], ondelete=u'CASCADE')


def downgrade():
    op.drop_constraint(u'station_clients_id_fk', 'station', type_='foreignkey')
    op.drop_constraint(u'station_station_id_fk', 'station', type_='foreignkey')
    op.drop_column('station', 'fk_client')
    op.drop_column('station', 'parent')
