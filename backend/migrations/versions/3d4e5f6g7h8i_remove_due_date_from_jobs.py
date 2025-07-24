"""Remove due_date column from jobs table

Revision ID: 3d4e5f6g7h8i
Revises: 2ce8bc4cb093
Create Date: 2025-01-24 11:03:04.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d4e5f6g7h8i'
down_revision: Union[str, None] = '2ce8bc4cb093'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop indexes that reference due_date column
    op.drop_index('idx_job_due_date_status', table_name='jobs')
    op.drop_index(op.f('ix_jobs_due_date'), table_name='jobs')
    
    # Drop the due_date column
    op.drop_column('jobs', 'due_date')


def downgrade() -> None:
    # Add the due_date column back
    op.add_column('jobs', sa.Column('due_date', sa.DateTime(), nullable=True))
    
    # Recreate indexes
    op.create_index(op.f('ix_jobs_due_date'), 'jobs', ['due_date'], unique=False)
    op.create_index('idx_job_due_date_status', 'jobs', ['due_date', 'status'], unique=False)