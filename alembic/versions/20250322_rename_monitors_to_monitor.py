"""rename monitors to monitor

Revision ID: 20250322
Revises: 
Create Date: 2025-03-22 12:07:54.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250322'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename tables
    op.rename_table('monitors', 'monitor')
    
    # Update foreign keys
    with op.batch_alter_table('monitor_statuses') as batch_op:
        batch_op.drop_constraint('fk_monitor_statuses_monitor_id_monitors', type_='foreignkey')
        batch_op.create_foreign_key('fk_monitor_statuses_monitor_id_monitor', 'monitor', ['monitor_id'], ['id'])
    
    # Update monitor_tags table
    with op.batch_alter_table('monitor_tags') as batch_op:
        batch_op.drop_constraint('fk_monitor_tags_monitor_id_monitors', type_='foreignkey')
        batch_op.create_foreign_key('fk_monitor_tags_monitor_id_monitor', 'monitor', ['monitor_id'], ['id'])


def downgrade() -> None:
    # Revert foreign keys
    with op.batch_alter_table('monitor_tags') as batch_op:
        batch_op.drop_constraint('fk_monitor_tags_monitor_id_monitor', type_='foreignkey')
        batch_op.create_foreign_key('fk_monitor_tags_monitor_id_monitors', 'monitors', ['monitor_id'], ['id'])
    
    with op.batch_alter_table('monitor_statuses') as batch_op:
        batch_op.drop_constraint('fk_monitor_statuses_monitor_id_monitor', type_='foreignkey')
        batch_op.create_foreign_key('fk_monitor_statuses_monitor_id_monitors', 'monitors', ['monitor_id'], ['id'])
    
    # Rename table back
    op.rename_table('monitor', 'monitors')