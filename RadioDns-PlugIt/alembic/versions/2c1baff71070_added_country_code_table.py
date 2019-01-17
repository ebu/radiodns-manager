"""Added country code table

Revision ID: 2c1baff71070
Revises: b4009d2ab0ba
Create Date: 2019-01-16 16:18:17.001528

"""

# revision identifiers, used by Alembic.
revision = '2c1baff71070'
down_revision = 'b4009d2ab0ba'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    country_code = op.create_table('country_code',
                    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
                    sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
                    sa.Column('iso', mysql.VARCHAR(length=2), nullable=False),
                    sa.Column('cc', mysql.VARCHAR(length=3), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_collate=u'utf8mb4_0900_ai_ci',
                    mysql_default_charset=u'utf8mb4',
                    mysql_engine=u'InnoDB'
                    )

    op.bulk_insert(
        country_code,
        [
            {"id": 1, "name": "United States", "iso": "US", "cc": "292"},
            {"id": 2, "name": "Canada", "iso": "CA", "cc": "040"},
            {"id": 3, "name": "Brazil", "iso": "BR", "cc": "031"},
            {"id": 4, "name": "Mexico", "iso": "MX", "cc": "197"},
            {"id": 5, "name": "Phillipines", "iso": "PH", "cc": "1e7"},
        ],
    )


def downgrade():
    op.drop_table('country_code')
