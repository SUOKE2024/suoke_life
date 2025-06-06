"""
001_add_audit_logs - 索克生活项目模块
"""

from alembic import op

"""添加审计日志表和操作日志表

Revision ID: 001
Revises: 
Create Date: 2024-05-22 14:30:00.000000

"""


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """升级数据库架构，添加审计和操作日志表"""
    
    # 创建用户审计日志表
    op.create_table(
        'user_audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('action_time', sa.DateTime, nullable=False),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(200)),
        sa.Column('request_id', sa.String(50)),
        sa.Column('changes', sa.JSON, default={}),
        sa.Column('details', sa.Text),
        sa.Column('metadata', sa.JSON, default={})
    )
    
    # 创建索引
    op.create_index('idx_user_audit_logs_user_id', 'user_audit_logs', ['user_id'])
    op.create_index('idx_user_audit_logs_action', 'user_audit_logs', ['action'])
    op.create_index('idx_user_audit_logs_action_time', 'user_audit_logs', ['action_time'])
    
    # 创建操作日志表
    op.create_table(
        'operation_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('service', sa.String(50), nullable=False, default='user-service'),
        sa.Column('operation', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('end_time', sa.DateTime, nullable=False),
        sa.Column('duration_ms', sa.Integer),
        sa.Column('user_id', sa.String(100)),
        sa.Column('request_id', sa.String(50)),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('endpoint', sa.String(200)),
        sa.Column('method', sa.String(20)),
        sa.Column('request_data', sa.JSON),
        sa.Column('response_data', sa.JSON),
        sa.Column('error_message', sa.Text),
        sa.Column('stack_trace', sa.Text),
        sa.Column('metadata', sa.JSON, default={})
    )
    
    # 创建索引
    op.create_index('idx_operation_logs_service', 'operation_logs', ['service'])
    op.create_index('idx_operation_logs_operation', 'operation_logs', ['operation'])
    op.create_index('idx_operation_logs_status', 'operation_logs', ['status'])
    op.create_index('idx_operation_logs_start_time', 'operation_logs', ['start_time'])
    op.create_index('idx_operation_logs_user_id', 'operation_logs', ['user_id'])
    op.create_index('idx_operation_logs_request_id', 'operation_logs', ['request_id'])
    
    # 添加用户地址表
    op.create_table(
        'user_addresses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('province', sa.String(50), nullable=False),
        sa.Column('city', sa.String(50), nullable=False),
        sa.Column('district', sa.String(50)),
        sa.Column('street', sa.String(200)),
        sa.Column('postal_code', sa.String(20)),
        sa.Column('is_default', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )
    
    # 创建索引
    op.create_index('idx_user_addresses_user_id', 'user_addresses', ['user_id'])
    op.create_index('idx_user_addresses_is_default', 'user_addresses', ['is_default'])
    
    # 为users表添加新字段
    try:
        op.add_column('users', sa.Column('gender', sa.String(20)))
        op.add_column('users', sa.Column('birth_date', sa.DateTime))
        op.add_column('users', sa.Column('avatar_url', sa.String(200)))
        op.add_column('users', sa.Column('last_login_at', sa.DateTime))
        op.add_column('users', sa.Column('settings', sa.JSON, default={}))
        op.add_column('users', sa.Column('agent_assignments', sa.JSON, default={}))
    except Exception as e:
        print(f"添加用户表字段时出错: {e}")
        print("如果这些列已经存在，可以忽略此错误")
    
    # 为设备表添加新字段
    try:
        op.add_column('user_devices', sa.Column('platform', sa.String(50)))
        op.add_column('user_devices', sa.Column('os_version', sa.String(50)))
        op.add_column('user_devices', sa.Column('app_version', sa.String(50)))
        op.add_column('user_devices', sa.Column('push_token', sa.String(200)))
    except Exception as e:
        print(f"添加设备表字段时出错: {e}")
        print("如果这些列已经存在，可以忽略此错误")
    
    # 向健康摘要表添加新字段
    try:
        op.add_column('user_health_summaries', sa.Column('height', sa.Float))
        op.add_column('user_health_summaries', sa.Column('weight', sa.Float))
        op.add_column('user_health_summaries', sa.Column('bmi', sa.Float))
        op.add_column('user_health_summaries', sa.Column('blood_type', sa.String(20)))
        op.add_column('user_health_summaries', sa.Column('allergies', sa.JSON, default=[]))
        op.add_column('user_health_summaries', sa.Column('chronic_conditions', sa.JSON, default=[]))
        op.add_column('user_health_summaries', sa.Column('medications', sa.JSON, default=[]))
        op.add_column('user_health_summaries', sa.Column('family_history', sa.JSON, default={}))
    except Exception as e:
        print(f"添加健康摘要表字段时出错: {e}")
        print("如果这些列已经存在，可以忽略此错误")

def downgrade():
    """回滚数据库架构更改"""
    
    # 删除用户健康摘要表新增字段
    try:
        op.drop_column('user_health_summaries', 'family_history')
        op.drop_column('user_health_summaries', 'medications')
        op.drop_column('user_health_summaries', 'chronic_conditions')
        op.drop_column('user_health_summaries', 'allergies')
        op.drop_column('user_health_summaries', 'blood_type')
        op.drop_column('user_health_summaries', 'bmi')
        op.drop_column('user_health_summaries', 'weight')
        op.drop_column('user_health_summaries', 'height')
    except Exception as e:
        print(f"删除健康摘要表字段时出错: {e}")
    
    # 删除设备表新增字段
    try:
        op.drop_column('user_devices', 'push_token')
        op.drop_column('user_devices', 'app_version')
        op.drop_column('user_devices', 'os_version')
        op.drop_column('user_devices', 'platform')
    except Exception as e:
        print(f"删除设备表字段时出错: {e}")
    
    # 删除用户表新增字段
    try:
        op.drop_column('users', 'agent_assignments')
        op.drop_column('users', 'settings')
        op.drop_column('users', 'last_login_at')
        op.drop_column('users', 'avatar_url')
        op.drop_column('users', 'birth_date')
        op.drop_column('users', 'gender')
    except Exception as e:
        print(f"删除用户表字段时出错: {e}")
    
    # 删除用户地址表
    op.drop_table('user_addresses')
    
    # 删除操作日志表
    op.drop_table('operation_logs')
    
    # 删除用户审计日志表
    op.drop_table('user_audit_logs') 