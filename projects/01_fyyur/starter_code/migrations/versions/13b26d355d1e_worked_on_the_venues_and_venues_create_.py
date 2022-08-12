"""worked on the/venues and /venues/create controllers

Revision ID: 13b26d355d1e
Revises: 1d0a87b69e3d
Create Date: 2022-08-12 02:53:52.726953

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13b26d355d1e'
down_revision = '1d0a87b69e3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
