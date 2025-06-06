"""AddedNotificationsTables

Revision ID: 1053a3cbd9c8
Revises: 1a149b772179
Create Date: 2025-05-30 15:49:45.520370

"""

# ruff: noqa: F401
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "1053a3cbd9c8"
down_revision: Union[str, None] = "1a149b772179"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "title", sqlmodel.sql.sqltypes.AutoString(length=None), nullable=False
        ),
        sa.Column(
            "message", sqlmodel.sql.sqltypes.AutoString(length=None), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("notifications", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_notifications_id"), ["id"], unique=False)

    op.create_table(
        "notifications_users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("notification_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["notification_id"],
            ["notifications.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["client_profiles.user_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("notifications_users", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_notifications_users_id"), ["id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_notifications_users_notification_id"),
            ["notification_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_notifications_users_user_id"), ["user_id"], unique=False
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("notifications_users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_notifications_users_user_id"))
        batch_op.drop_index(batch_op.f("ix_notifications_users_notification_id"))
        batch_op.drop_index(batch_op.f("ix_notifications_users_id"))

    op.drop_table("notifications_users")
    with op.batch_alter_table("notifications", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_notifications_id"))

    op.drop_table("notifications")
    # ### end Alembic commands ###
