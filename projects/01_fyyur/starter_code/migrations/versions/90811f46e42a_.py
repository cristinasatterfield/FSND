"""empty message

Revision ID: 90811f46e42a
Revises: fb7cf0079b81
Create Date: 2020-04-10 16:11:04.581726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90811f46e42a'
down_revision = 'fb7cf0079b81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shows_venue_id_fkey', 'shows', type_='foreignkey')
    op.drop_constraint('shows_artist_id_fkey', 'shows', type_='foreignkey')
    op.create_foreign_key(None, 'shows', 'artists', ['artist_id'], ['id'], ondelete='cascade')
    op.create_foreign_key(None, 'shows', 'venues', ['venue_id'], ['id'], ondelete='cascade')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.create_foreign_key('shows_artist_id_fkey', 'shows', 'artists', ['artist_id'], ['id'])
    op.create_foreign_key('shows_venue_id_fkey', 'shows', 'venues', ['venue_id'], ['id'])
    # ### end Alembic commands ###