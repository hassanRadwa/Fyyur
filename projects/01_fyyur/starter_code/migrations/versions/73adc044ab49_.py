"""empty message

Revision ID: 73adc044ab49
Revises: 6e68ac3a351b
Create Date: 2020-07-21 17:50:08.072309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73adc044ab49'
down_revision = '6e68ac3a351b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('genres', sa.String(), nullable=False))
    op.add_column('artists', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('artists', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.add_column('venues', sa.Column('genres', sa.String(), nullable=False))
    op.add_column('venues', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'seeking_talent')
    op.drop_column('venues', 'seeking_description')
    op.drop_column('venues', 'genres')
    op.drop_column('artists', 'seeking_venue')
    op.drop_column('artists', 'seeking_description')
    op.drop_column('artists', 'genres')
    # ### end Alembic commands ###
