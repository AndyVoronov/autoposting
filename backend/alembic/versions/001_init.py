"""init

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column(
            "platform", sa.Enum("telegram", "vk", "wordpress", name="platform"), nullable=False
        ),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_channels_slug", "channels", ["slug"])

    op.create_table(
        "content_types",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "reddit",
                "horoscope",
                "animal_facts",
                "news",
                "city",
                "affiliate",
                "custom",
                name="contenttype",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "channel_content",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("content_type_id", sa.Integer(), nullable=False),
        sa.Column("schedule", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"]),
        sa.ForeignKeyConstraint(["content_type_id"], ["content_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_channel_content_channel_id", "channel_content", ["channel_id"])
    op.create_index("ix_channel_content_content_type_id", "channel_content", ["content_type_id"])

    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("content_type_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "pending",
                "approved",
                "scheduled",
                "published",
                "failed",
                "rejected",
                name="poststatus",
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("media_urls", sa.JSON(), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("source_title", sa.String(length=500), nullable=True),
        sa.Column("censorship_flags", sa.JSON(), nullable=True),
        sa.Column("censorship_passed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("ai_metadata", sa.JSON(), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"]),
        sa.ForeignKeyConstraint(["content_type_id"], ["content_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_posts_channel_id", "posts", ["channel_id"])
    op.create_index("ix_posts_content_type_id", "posts", ["content_type_id"])

    op.create_table(
        "publish_queue",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column(
            "platform", sa.Enum("telegram", "vk", "wordpress", name="platform"), nullable=False
        ),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_publish_queue_post_id", "publish_queue", ["post_id"])

    op.create_table(
        "publish_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column(
            "platform", sa.Enum("telegram", "vk", "wordpress", name="platform"), nullable=False
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("message_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_publish_logs_post_id", "publish_logs", ["post_id"])

    op.create_table(
        "censorship_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pattern", sa.String(length=500), nullable=False),
        sa.Column("pattern_type", sa.String(length=20), nullable=False, server_default="word"),
        sa.Column("rule_type", sa.String(length=20), nullable=False, server_default="banned"),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("replacement", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_censorship_rules_pattern", "censorship_rules", ["pattern"])

    op.create_table(
        "censorship_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=True),
        sa.Column("matched_pattern", sa.String(length=500), nullable=True),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["rule_id"], ["censorship_rules.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_censorship_logs_post_id", "censorship_logs", ["post_id"])

    op.create_table(
        "affiliate_products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("ref_url", sa.String(length=1000), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("price", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "affiliate_clicks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.Column("clicked_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["affiliate_products.id"]),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_affiliate_clicks_product_id", "affiliate_clicks", ["product_id"])
    op.create_index("ix_affiliate_clicks_post_id", "affiliate_clicks", ["post_id"])
    op.create_index("ix_affiliate_clicks_channel_id", "affiliate_clicks", ["channel_id"])

    op.create_table(
        "analytics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("comments", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("date", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analytics_post_id", "analytics", ["post_id"])


def downgrade() -> None:
    op.drop_table("analytics")
    op.drop_table("affiliate_clicks")
    op.drop_table("affiliate_products")
    op.drop_table("censorship_logs")
    op.drop_table("censorship_rules")
    op.drop_table("publish_logs")
    op.drop_table("publish_queue")
    op.drop_table("posts")
    op.drop_table("channel_content")
    op.drop_table("content_types")
    op.drop_table("channels")
    op.drop_table("users")
