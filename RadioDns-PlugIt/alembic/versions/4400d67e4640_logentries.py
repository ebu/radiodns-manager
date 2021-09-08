"""LogEntries

Revision ID: 4400d67e4640
Revises: 4c03607d9774
Create Date: 2013-08-12 14:08:53.541000

"""

# revision identifiers, used by Alembic.
revision = '4400d67e4640'
down_revision = '4c03607d9774'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('log_entry', u'reception_timestamp')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('log_entry', sa.Column(u'reception_timestamp', mysql.VARCHAR(length=15), nullable=True))
    ### end Alembic commands ###