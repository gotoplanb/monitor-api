"""add message to monitor status

Revision ID: 20250330
Revises: 20250329_2
Create Date: 2025-03-30 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20250330"
down_revision: Union[str, None] = "20250329_2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add message field to monitor_statuses table."""
    with op.batch_alter_table("monitor_statuses") as batch_op:
        batch_op.add_column(sa.Column("message", sa.String(), nullable=True))


def downgrade() -> None:
    """Remove message field from monitor_statuses table."""
    with op.batch_alter_table("monitor_statuses") as batch_op:
        batch_op.drop_column("message")
