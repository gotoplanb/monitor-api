"""rename monitors to monitor

Revision ID: 20250322
Revises:
Create Date: 2025-03-22 12:07:54.123456

"""

from typing import Sequence, Union

# pylint: disable=unused-import
import sqlalchemy as sa  # Required by alembic
# pylint: disable=no-member
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20250322"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade the database schema from monitors to monitor.
    
    This migration renames the monitors table to monitor and updates all foreign keys 
    referencing the table.
    """
    # Rename tables
    op.rename_table("monitors", "monitor")

    # Update foreign keys
    with op.batch_alter_table("monitor_statuses") as batch_op:
        batch_op.drop_constraint(
            "fk_monitor_statuses_monitor_id_monitors", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            "fk_monitor_statuses_monitor_id_monitor", "monitor", ["monitor_id"], ["id"]
        )

    # Update monitor_tags table
    with op.batch_alter_table("monitor_tags") as batch_op:
        batch_op.drop_constraint(
            "fk_monitor_tags_monitor_id_monitors", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            "fk_monitor_tags_monitor_id_monitor", "monitor", ["monitor_id"], ["id"]
        )


def downgrade() -> None:
    """Downgrade the database schema from monitor back to monitors.
    
    This migration reverts the table rename and foreign key changes.
    """
    # Revert foreign keys
    with op.batch_alter_table("monitor_tags") as batch_op:
        batch_op.drop_constraint(
            "fk_monitor_tags_monitor_id_monitor", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            "fk_monitor_tags_monitor_id_monitors", "monitors", ["monitor_id"], ["id"]
        )

    with op.batch_alter_table("monitor_statuses") as batch_op:
        batch_op.drop_constraint(
            "fk_monitor_statuses_monitor_id_monitor", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            "fk_monitor_statuses_monitor_id_monitors",
            "monitors",
            ["monitor_id"],
            ["id"],
        )

    # Rename table back
    op.rename_table("monitor", "monitors")
