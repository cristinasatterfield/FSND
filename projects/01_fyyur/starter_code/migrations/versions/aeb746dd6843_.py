"""empty message

Revision ID: aeb746dd6843
Revises: 
Create Date: 2020-03-12 14:06:09.065939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "aeb746dd6843"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "venues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String()(length=120), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("address", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=120), nullable=False),
        sa.Column(
            "website_link", sa.String(length=120), server_default="", nullable=False
        ),
        sa.Column(
            "facebook_link", sa.String(length=120), server_default="", nullable=False
        ),
        sa.Column(
            "seeking_talent", sa.Boolean(), server_default="false", nullable=False
        ),
        sa.Column(
            "seeking_description",
            sa.String(length=500),
            server_default="",
            nullable=False,
        ),
        sa.Column(
            "image_link",
            sa.String(length=500),
            server_default="https://images.all-free-download.com/images/graphiclarge/scene_layout_04_hd_picture_167802.jpg",
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("venues")
    # ### end Alembic commands ###
