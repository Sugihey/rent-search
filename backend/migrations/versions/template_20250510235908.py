"""Template migration for future schema changes

Revision ID: template_20250510235908
Create Date: 2025-05-10T23:59:08.829135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'template_20250510235908'
down_revision: Union[str, None] = None  # Set this to the previous migration ID
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Example schema changes:
    
    # Add a new column
    op.add_column('properties', sa.Column('new_column', sa.String(255), nullable=True))
    
    # Modify an existing column
    op.alter_column('properties', 'existing_column', 
                   existing_type=sa.String(100),
                   type_=sa.String(200),
                   nullable=False)
                   
    # Create a new table
    op.create_table(
        'new_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    """
    pass


def downgrade() -> None:
    """
    Example downgrade operations:
    
    # Remove a column
    op.drop_column('properties', 'new_column')
    
    # Revert a column modification
    op.alter_column('properties', 'existing_column', 
                   existing_type=sa.String(200),
                   type_=sa.String(100),
                   nullable=True)
                   
    # Drop a table
    op.drop_table('new_table')
    """
    pass
