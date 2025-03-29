"""drop_unused_monitors_table

Revision ID: 8ccc8e52ee58
Revises: 20250329_2
Create Date: 2025-03-29 14:53:53.222612+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8ccc8e52ee58"
down_revision: Union[str, None] = "20250329_2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the unused monitors table
    op.drop_table("monitors")


def downgrade() -> None:
    # Recreate the monitors table if we need to downgrade
    op.create_table(
        "monitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
