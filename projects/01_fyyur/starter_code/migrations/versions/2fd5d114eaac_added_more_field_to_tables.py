"""added more field to tables

Revision ID: 2fd5d114eaac
Revises: 4f27fcb23bed
Create Date: 2022-08-11 08:06:38.041578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fd5d114eaac'
down_revision = '4f27fcb23bed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Artist', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('created_at', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'created_at')
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_venue')
    op.drop_column('Venue', 'website')
    op.drop_column('Artist', 'created_at')
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'website')
    # ### end Alembic commands ###
