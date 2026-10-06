"""Phase 8 Advanced Models: Branches, Stock Transfers, Goals

Revision ID: 8a1b2c3d4e5f
Revises: 12307a99b475
Create Date: 2026-10-05 12:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '8a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '12307a99b475'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    # 1. Branches table
    if 'branches' not in tables:
        op.create_table(
            'branches',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('business_id', sa.String(), sa.ForeignKey('businesses.id'), nullable=False, index=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('code', sa.String(), nullable=False),
            sa.Column('address', sa.String(), nullable=True),
            sa.Column('city', sa.String(), nullable=True),
            sa.Column('state', sa.String(), nullable=True),
            sa.Column('postal_code', sa.String(), nullable=True),
            sa.Column('phone', sa.String(), nullable=True),
            sa.Column('email', sa.String(), nullable=True),
            sa.Column('manager_id', sa.String(), sa.ForeignKey('employees.id'), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.UniqueConstraint('business_id', 'code', name='uq_business_branch_code')
        )

    # 2. Add branch_id to warehouses
    wh_cols = [c['name'] for c in insp.get_columns('warehouses')]
    if 'branch_id' not in wh_cols:
        with op.batch_alter_table('warehouses') as batch_op:
            batch_op.add_column(sa.Column('branch_id', sa.String(), nullable=True))

    # 3. Add branch_id to orders
    ord_cols = [c['name'] for c in insp.get_columns('orders')]
    if 'branch_id' not in ord_cols:
        with op.batch_alter_table('orders') as batch_op:
            batch_op.add_column(sa.Column('branch_id', sa.String(), nullable=True))

    # 4. Stock Transfers table
    if 'stock_transfers' not in tables:
        op.create_table(
            'stock_transfers',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('business_id', sa.String(), sa.ForeignKey('businesses.id'), nullable=False, index=True),
            sa.Column('transfer_number', sa.String(), nullable=False, index=True),
            sa.Column('source_warehouse_id', sa.String(), sa.ForeignKey('warehouses.id'), nullable=False, index=True),
            sa.Column('destination_warehouse_id', sa.String(), sa.ForeignKey('warehouses.id'), nullable=False, index=True),
            sa.Column('status', sa.String(), server_default='Draft', nullable=False),
            sa.Column('requested_date', sa.DateTime(), nullable=True),
            sa.Column('shipped_date', sa.DateTime(), nullable=True),
            sa.Column('received_date', sa.DateTime(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_by', sa.String(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.UniqueConstraint('business_id', 'transfer_number', name='uq_business_transfer_number')
        )

    # 5. Stock Transfer Items table
    if 'stock_transfer_items' not in tables:
        op.create_table(
            'stock_transfer_items',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('transfer_id', sa.String(), sa.ForeignKey('stock_transfers.id'), nullable=False, index=True),
            sa.Column('product_id', sa.String(), sa.ForeignKey('products.id'), nullable=False, index=True),
            sa.Column('quantity', sa.Numeric(12, 2), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True)
        )

    # 6. Business Goals table
    if 'business_goals' not in tables:
        op.create_table(
            'business_goals',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('business_id', sa.String(), sa.ForeignKey('businesses.id'), nullable=False, index=True),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('metric', sa.String(), nullable=False),
            sa.Column('target_value', sa.Numeric(12, 2), nullable=False),
            sa.Column('period', sa.String(), server_default='current_month', nullable=False),
            sa.Column('start_date', sa.DateTime(), nullable=True),
            sa.Column('end_date', sa.DateTime(), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True)
        )

def downgrade() -> None:
    op.drop_table('business_goals')
    op.drop_table('stock_transfer_items')
    op.drop_table('stock_transfers')
    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_column('branch_id')
    with op.batch_alter_table('warehouses') as batch_op:
        batch_op.drop_column('branch_id')
    op.drop_table('branches')
