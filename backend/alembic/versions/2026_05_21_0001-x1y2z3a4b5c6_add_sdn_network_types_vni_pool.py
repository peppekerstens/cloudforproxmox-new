"""add SDN network types (vxlan, simple) and VXLAN VNI pool

Revision ID: x1y2z3a4b5c6
Revises: r5s6t7u8v9w0
Create Date: 2026-05-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'x1y2z3a4b5c6'
down_revision: Union[str, None] = 'r5s6t7u8v9w0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the unique constraint on vlan_id — VLAN uniqueness is now
    # enforced by the VLAN pool service, and non-VLAN networks store 0.
    op.drop_index('ix_vpc_networks_vlan_id', table_name='vpc_networks')
    op.create_index('ix_vpc_networks_vlan_id', 'vpc_networks', ['vlan_id'])

    # Add SDN/VXLAN columns to vpc_networks
    op.add_column('vpc_networks', sa.Column(
        'network_type', sa.String(20),
        nullable=False, server_default='vlan'
    ))
    op.create_index('ix_vpc_networks_network_type', 'vpc_networks', ['network_type'])

    op.add_column('vpc_networks', sa.Column(
        'vni', sa.Integer(), nullable=True
    ))
    op.create_index('ix_vpc_networks_vni', 'vpc_networks', ['vni'])

    op.add_column('vpc_networks', sa.Column(
        'sdn_zone', sa.String(50), nullable=True
    ))
    op.add_column('vpc_networks', sa.Column(
        'sdn_vnet', sa.String(50), nullable=True
    ))

    # Create VXLAN VNI pool table
    op.create_table('vxlan_vni_pool',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('vni', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='available'),
        sa.Column('allocated_to_network_id', sa.String(36), nullable=True),
        sa.Column('allocated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['allocated_to_network_id'], ['vpc_networks.id'],
                                ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_vxlan_vni_pool_vni', 'vxlan_vni_pool', ['vni'])
    op.create_index('ix_vxlan_vni_pool_status', 'vxlan_vni_pool', ['status'])


def downgrade() -> None:
    # Drop VXLAN VNI pool
    op.drop_index('ix_vxlan_vni_pool_status', table_name='vxlan_vni_pool')
    op.drop_index('ix_vxlan_vni_pool_vni', table_name='vxlan_vni_pool')
    op.drop_table('vxlan_vni_pool')

    # Remove SDN/VXLAN columns from vpc_networks
    op.drop_index('ix_vpc_networks_vni', table_name='vpc_networks')
    op.drop_column('vpc_networks', 'vni')

    op.drop_index('ix_vpc_networks_network_type', table_name='vpc_networks')
    op.drop_column('vpc_networks', 'network_type')

    op.drop_column('vpc_networks', 'sdn_zone')
    op.drop_column('vpc_networks', 'sdn_vnet')

    # Restore unique constraint on vlan_id
    op.drop_index('ix_vpc_networks_vlan_id', table_name='vpc_networks')
    op.create_index('ix_vpc_networks_vlan_id', 'vpc_networks', ['vlan_id'], unique=True)
