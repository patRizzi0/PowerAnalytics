"""Add description to categories

Revision ID: a6a60ebe7e83
Revises: c92f3c2d9dd8
Create Date: 2026-05-02 16:14:01.721174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6a60ebe7e83'
down_revision: Union[str, Sequence[str], None] = 'c92f3c2d9dd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aggiunge la colonna description alla tabella categorie."""
    op.add_column('categories_elettrodomestico',
    sa.Column('description', sa.String(length=200), nullable=True))


def downgrade() -> None:
    """Rimuove la colonna description dalla tabella categorie."""
    op.drop_column('categories_elettrodomestico', 'description')
