"""初始数据库结构

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级数据库结构"""
    # 创建用户表
    op.create_table('users',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('profile', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)

    # 创建平台表
    op.create_table('platforms',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('api_base_url', sa.String(length=200), nullable=True),
        sa.Column('auth_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_platforms_id'), 'platforms', ['id'], unique=False)

    # 创建平台配置表
    op.create_table('platform_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform_id', sa.String(length=50), nullable=False),
        sa.Column('config_key', sa.String(length=100), nullable=False),
        sa.Column('config_value', sa.String(length=500), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_platform_configs_id'), 'platform_configs', ['id'], unique=False)
    op.create_index(op.f('ix_platform_configs_platform_id'), 'platform_configs', ['platform_id'], unique=False)

    # 创建用户平台授权表
    op.create_table('user_platform_auths',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('platform_id', sa.String(length=50), nullable=False),
        sa.Column('access_token', sa.String(length=500), nullable=True),
        sa.Column('refresh_token', sa.String(length=500), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('auth_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['platform_id'], ['platforms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_platform_auths_id'), 'user_platform_auths', ['id'], unique=False)
    op.create_index(op.f('ix_user_platform_auths_user_id'), 'user_platform_auths', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_platform_auths_platform_id'), 'user_platform_auths', ['platform_id'], unique=False)

    # 创建健康数据表
    op.create_table('health_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('platform_id', sa.String(length=50), nullable=False),
        sa.Column('data_type', sa.Enum('STEPS', 'HEART_RATE', 'BLOOD_PRESSURE', 'WEIGHT', 'HEIGHT', 'SLEEP', 'EXERCISE', 'CALORIES', 'DISTANCE', 'BLOOD_GLUCOSE', 'BODY_TEMPERATURE', 'OXYGEN_SATURATION', name='healthdatatype'), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['platform_id'], ['platforms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_data_id'), 'health_data', ['id'], unique=False)
    op.create_index(op.f('ix_health_data_user_id'), 'health_data', ['user_id'], unique=False)
    op.create_index(op.f('ix_health_data_platform_id'), 'health_data', ['platform_id'], unique=False)
    op.create_index(op.f('ix_health_data_data_type'), 'health_data', ['data_type'], unique=False)


def downgrade() -> None:
    """降级数据库结构"""
    op.drop_index(op.f('ix_health_data_data_type'), table_name='health_data')
    op.drop_index(op.f('ix_health_data_platform_id'), table_name='health_data')
    op.drop_index(op.f('ix_health_data_user_id'), table_name='health_data')
    op.drop_index(op.f('ix_health_data_id'), table_name='health_data')
    op.drop_table('health_data')
    
    op.drop_index(op.f('ix_user_platform_auths_platform_id'), table_name='user_platform_auths')
    op.drop_index(op.f('ix_user_platform_auths_user_id'), table_name='user_platform_auths')
    op.drop_index(op.f('ix_user_platform_auths_id'), table_name='user_platform_auths')
    op.drop_table('user_platform_auths')
    
    op.drop_index(op.f('ix_platform_configs_platform_id'), table_name='platform_configs')
    op.drop_index(op.f('ix_platform_configs_id'), table_name='platform_configs')
    op.drop_table('platform_configs')
    
    op.drop_index(op.f('ix_platforms_id'), table_name='platforms')
    op.drop_table('platforms')
    
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users') 