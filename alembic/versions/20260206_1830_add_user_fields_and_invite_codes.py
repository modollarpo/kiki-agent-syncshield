"""Add user fields and invite codes table

Revision ID: 20260206_1830
Revises: 6b1424f7a091
Create Date: 2026-02-06 18:30:00.000000

This migration:
1. Adds missing fields to users table (is_active, full_name, organization_id, updated_at)
2. Renames password_hash to hashed_password for consistency
3. Creates invite_codes table for invite-only registration
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BOOLEAN


# revision identifiers, used by Alembic.
revision = '20260206_1830'
down_revision = '6b1424f7a091'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add user fields and create invite_codes table"""
    
    # ========================================================================
    # Update users table
    # ========================================================================
    
    # Add new columns to users table
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('full_name', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('organization_id', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Create index on organization_id
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    
    # Rename password_hash to hashed_password
    op.alter_column('users', 'password_hash', new_column_name='hashed_password')
    
    # Set updated_at to created_at for existing users
    op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")
    
    # ========================================================================
    # Create invite_codes table
    # ========================================================================
    
    op.create_table(
        'invite_codes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('used_by_id', sa.Integer(), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['used_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_invite_codes_code'), 'invite_codes', ['code'], unique=True)
    op.create_index(op.f('ix_invite_codes_is_used'), 'invite_codes', ['is_used'], unique=False)
    op.create_index(op.f('ix_invite_codes_created_at'), 'invite_codes', ['created_at'], unique=False)
    op.create_index(op.f('ix_invite_codes_expires_at'), 'invite_codes', ['expires_at'], unique=False)


def downgrade() -> None:
    """Revert user fields and drop invite_codes table"""
    
    # Drop invite_codes table
    op.drop_index(op.f('ix_invite_codes_expires_at'), table_name='invite_codes')
    op.drop_index(op.f('ix_invite_codes_created_at'), table_name='invite_codes')
    op.drop_index(op.f('ix_invite_codes_is_used'), table_name='invite_codes')
    op.drop_index(op.f('ix_invite_codes_code'), table_name='invite_codes')
    op.drop_table('invite_codes')
    
    # Revert users table changes
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'organization_id')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'is_active')
    op.alter_column('users', 'hashed_password', new_column_name='password_hash')
