"""empty message

Revision ID: f7ae9cf553c7
Revises: ffc89c6a485e
Create Date: 2017-09-19 14:47:44.977746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7ae9cf553c7'
down_revision = 'ffc89c6a485e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workers', sa.Column('surges_only', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('workers', 'surges_only')
    # ### end Alembic commands ###
