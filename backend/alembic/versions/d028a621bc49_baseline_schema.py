"""baseline schema

Captures the schema as it already exists in the live DB (originally created
ad-hoc via SQLAlchemy's Base.metadata.create_all() plus manual ALTER TABLEs --
see C:\\Users\\ediso\\minton_pj\\docker_postgresql\\create_table.sql, the
out-of-repo reference this was written from). This migration is the baseline
every future schema change builds on top of.

On a DB that already has these tables (any existing dev/prod environment),
run `alembic stamp head` instead of `alembic upgrade head` -- stamping just
records this revision as applied without re-running the CREATE TABLEs, which
would fail against tables that already exist. Only a genuinely fresh database
(no bd_* tables yet) should run `alembic upgrade head` to create them.

Revision ID: d028a621bc49
Revises:
Create Date: 2026-08-16 22:44:37.258083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from config import settings

# revision identifiers, used by Alembic.
revision: str = 'd028a621bc49'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = settings.DATABASE_SCHEMA


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "bd_usr_mt",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("login_id", sa.String(40), nullable=False, unique=True),
        sa.Column("login_pw", sa.String(255), nullable=False),
        sa.Column("group_key", sa.String(40), nullable=True),
        sa.Column("name", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        schema=SCHEMA,
    )
    op.create_table(
        "bd_grp_mt",
        sa.Column("group_key", sa.String(40), primary_key=True),
        sa.Column("group_name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "owner_id",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_usr_mt.id", ondelete="SET NULL", name="fk_grp_owner"),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        schema=SCHEMA,
    )
    op.create_index("idx_grp_name", "bd_grp_mt", ["group_name"], schema=SCHEMA)

    op.create_table(
        "bd_grp_usr_map",
        sa.Column(
            "group_key",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_grp_mt.group_key", ondelete="CASCADE", name="fk_map_group"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_usr_mt.id", ondelete="CASCADE", name="fk_map_user"),
            primary_key=True,
        ),
        sa.Column("role", sa.String(20), server_default="member"),
        sa.Column("joined_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        schema=SCHEMA,
    )
    op.create_index("idx_map_user_id", "bd_grp_usr_map", ["user_id"], schema=SCHEMA)

    op.create_table(
        "bd_game_mt",
        sa.Column("game_id", sa.String(40), primary_key=True),
        sa.Column(
            "group_key",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_grp_mt.group_key", ondelete="CASCADE", name="fk_game_group"),
            nullable=False,
        ),
        sa.Column("game_type", sa.String(20), server_default="doubles"),
        sa.Column("game_status", sa.String(20), server_default="finished"),
        sa.Column("court_number", sa.Integer(), nullable=True),
        sa.Column("played_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("video_url", sa.String(500), nullable=True),
        schema=SCHEMA,
    )
    op.create_index("idx_game_group_played", "bd_game_mt", ["group_key", sa.text("played_at DESC")], schema=SCHEMA)

    op.create_table(
        "bd_game_usr_map",
        sa.Column(
            "game_id",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_game_mt.game_id", ondelete="CASCADE", name="fk_gmap_game"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_usr_mt.id", ondelete="CASCADE", name="fk_gmap_user"),
            primary_key=True,
        ),
        sa.Column("team_color", sa.String(10), nullable=False),
        sa.Column("score", sa.Integer(), server_default="0"),
        sa.Column("is_winner", sa.Boolean(), nullable=True),
        schema=SCHEMA,
    )
    op.create_index("idx_gmap_user_id", "bd_game_usr_map", ["user_id"], schema=SCHEMA)

    op.create_table(
        "bd_game_comment_mt",
        sa.Column("comment_id", sa.String(40), primary_key=True),
        sa.Column(
            "game_id",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_game_mt.game_id", ondelete="CASCADE", name="fk_comment_game"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_usr_mt.id", ondelete="CASCADE", name="fk_comment_user"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        schema=SCHEMA,
    )
    op.create_index("idx_comment_game_created", "bd_game_comment_mt", ["game_id", "created_at"], schema=SCHEMA)

    op.create_table(
        "bd_game_like_map",
        sa.Column(
            "game_id",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_game_mt.game_id", ondelete="CASCADE", name="fk_like_game"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.String(40),
            sa.ForeignKey(f"{SCHEMA}.bd_usr_mt.id", ondelete="CASCADE", name="fk_like_user"),
            primary_key=True,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        schema=SCHEMA,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("bd_game_like_map", schema=SCHEMA)
    op.drop_index("idx_comment_game_created", table_name="bd_game_comment_mt", schema=SCHEMA)
    op.drop_table("bd_game_comment_mt", schema=SCHEMA)
    op.drop_index("idx_gmap_user_id", table_name="bd_game_usr_map", schema=SCHEMA)
    op.drop_table("bd_game_usr_map", schema=SCHEMA)
    op.drop_index("idx_game_group_played", table_name="bd_game_mt", schema=SCHEMA)
    op.drop_table("bd_game_mt", schema=SCHEMA)
    op.drop_index("idx_map_user_id", table_name="bd_grp_usr_map", schema=SCHEMA)
    op.drop_table("bd_grp_usr_map", schema=SCHEMA)
    op.drop_index("idx_grp_name", table_name="bd_grp_mt", schema=SCHEMA)
    op.drop_table("bd_grp_mt", schema=SCHEMA)
    op.drop_table("bd_usr_mt", schema=SCHEMA)
