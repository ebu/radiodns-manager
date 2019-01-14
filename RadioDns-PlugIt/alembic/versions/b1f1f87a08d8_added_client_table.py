"""Added clients.

Revision ID: b1f1f87a08d8
Revises: 005f84c40e24
Create Date: 2018-10-11 11:06:51.823681

"""

# revision identifiers, used by Alembic.
revision = 'b1f1f87a08d8'
down_revision = '005f84c40e24'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.create_table('clients',
                    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
                    sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
                    sa.Column('orga', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
                    sa.Column('identifier', mysql.VARCHAR(length=128), nullable=False),
                    sa.Column('email', mysql.VARCHAR(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_collate=u'utf8mb4_0900_ai_ci',
                    mysql_default_charset=u'utf8mb4',
                    mysql_engine=u'InnoDB'
                    )
    op.create_index('clients_name_uindex', 'clients', ['name'], unique=True)
    op.create_index('clients_identifier_uindex', 'clients', ['identifier'], unique=True)


def downgrade():
    op.drop_index('clients_identifier_uindex', table_name='clients')
    op.drop_index('clients_name_uindex', table_name='clients')
    op.drop_table('clients')
