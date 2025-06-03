"""初始数据库结构

Revision ID: 001
Create Date: 2025-05-19

"""
from alembic import op
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifier, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """升级数据库结构"""
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('user_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('metadata', JSONB, server_default='{}'),
        sa.Column('roles', JSONB, server_default='["user"]'),
        sa.Column('preferences', JSONB, server_default='{}'),
    )
    
    # 创建健康摘要表
    op.create_table(
        'health_summaries',
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.user_id'), primary_key=True),
        sa.Column('health_score', sa.Integer, server_default='60'),
        sa.Column('dominant_constitution', sa.String(50), nullable=True),
        sa.Column('constitution_scores', JSONB, server_default='{}'),
        sa.Column('recent_metrics', JSONB, server_default='[]'),
        sa.Column('last_assessment_date', sa.DateTime, nullable=True),
    )
    
    # 创建设备表
    op.create_table(
        'devices',
        sa.Column('binding_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('device_id', sa.String(100), nullable=False),
        sa.Column('device_type', sa.String(50), nullable=False),
        sa.Column('device_name', sa.String(100), nullable=True),
        sa.Column('binding_time', sa.DateTime, server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_active_time', sa.DateTime, server_default=sa.func.now()),
        sa.Column('device_metadata', JSONB, server_default='{}'),
    )
    
    # 创建索引
    op.create_index('idx_devices_user_id', 'devices', ['user_id'])
    op.create_index('idx_devices_device_id', 'devices', ['device_id'])
    op.create_unique_index('idx_user_device', 'devices', ['user_id', 'device_id'])
    
    # 创建UUID扩展（如果不存在）
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

def downgrade():
    """回滚数据库结构"""
    # 删除表（级联删除关联数据）
    op.drop_table('devices')
    op.drop_table('health_summaries')
    op.drop_table('users')