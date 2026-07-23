"""initial schemas and app tables

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "app"


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS app")
    op.execute("CREATE SCHEMA IF NOT EXISTS langgraph")

    op.create_table(
        "conversations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_sub", sa.String(), nullable=False, index=True),
        sa.Column("surface", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("conversation_id", sa.String(), nullable=False, index=True),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("job_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["conversation_id"], [f"{SCHEMA}.conversations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("job_id", name="uq_message_job"),
        schema=SCHEMA,
    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("jira_key", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("conversation_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("jira_key", name="uq_ticket_jira_key"),
        schema=SCHEMA,
    )
    op.create_table(
        "ticket_reporters",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("user_sub", sa.String(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["ticket_id"], [f"{SCHEMA}.tickets.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("ticket_id", "user_sub", name="uq_ticket_reporter"),
        schema=SCHEMA,
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("type", sa.String(), nullable=False, server_default="create_ticket"),
        sa.Column("status", sa.String(), nullable=False, server_default="queued", index=True),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("user_sub", sa.String(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("jira_key", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_sub", sa.String(), nullable=False, index=True),
        sa.Column("conversation_id", sa.String(), nullable=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("jira_key", sa.String(), nullable=True),
        sa.Column("job_id", sa.String(), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("job_id", name="uq_notification_job"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    for table in ["notifications", "jobs", "ticket_reporters", "tickets", "messages", "conversations"]:
        op.drop_table(table, schema=SCHEMA)
    op.execute("DROP SCHEMA IF EXISTS langgraph CASCADE")
    op.execute("DROP SCHEMA IF EXISTS app CASCADE")
