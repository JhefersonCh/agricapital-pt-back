"""Update Request table

Revision ID: 85f53ffd8498
Revises: 27fd9995217c
Create Date: 2025-05-30 09:51:38.090736

"""

# ruff: noqa: F401
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "85f53ffd8498"
down_revision: Union[str, None] = "27fd9995217c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
