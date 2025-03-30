"""merge heads

Revision ID: 20250330_merge
Revises: 8ccc8e52ee58, 20250330
Create Date: 2025-03-30 10:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250330_merge"
down_revision: Union[str, Sequence[str], None] = ("8ccc8e52ee58", "20250330")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge the two heads."""
    pass


def downgrade() -> None:
    """No downgrade needed for merge."""
    pass
