"""fix monitor_tags foreign key

Revision ID: 20250329
Revises: 20250322
Create Date: 2025-03-29 14:20:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250329"
down_revision: Union[str, None] = "20250322"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix the monitor_tags foreign key constraint."""
    # Drop the old foreign key constraint
    with op.batch_alter_table("monitor_tags") as batch_op:
        batch_op.drop_constraint("monitor_tags_monitor_id_fkey", type_="foreignkey")
        # Create the new foreign key constraint
        batch_op.create_foreign_key(
            "monitor_tags_monitor_id_fkey", "monitor", ["monitor_id"], ["id"]
        )


def downgrade() -> None:
    """Revert the monitor_tags foreign key constraint."""
    with op.batch_alter_table("monitor_tags") as batch_op:
        batch_op.drop_constraint("monitor_tags_monitor_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "monitor_tags_monitor_id_fkey", "monitors", ["monitor_id"], ["id"]
        )
