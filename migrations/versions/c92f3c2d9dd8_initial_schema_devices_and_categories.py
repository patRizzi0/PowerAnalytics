"""Initial schema: devices and categories

Revision ID: c92f3c2d9dd8
Revises: 
Create Date: 2026-05-02 16:11:59.145156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c92f3c2d9dd8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Crea le tabelle iniziali."""
    # Crea tabella categories_elettrodomestico
    op.create_table(
        'categories_elettrodomestico',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='public'
    )

    # Crea tabella devices
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('average_watts', sa.Integer(), nullable=False),
        sa.Column('standby_watts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories_elettrodomestico.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )


def downgrade() -> None:
    """Downgrade schema - Elimina le tabelle."""
    op.drop_table('devices', schema='public')
    op.drop_table('categories_elettrodomestico', schema='public')
