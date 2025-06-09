"""
初始数据库架构迁移
创建健康数据相关的表结构

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """创建表结构"""
    
    # 创建健康数据表
    op.create_table(
        'health_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('data_type', sa.String(100), nullable=False),
        sa.Column('data_value', sa.Text()),
        sa.Column('unit', sa.String(50)),
        sa.Column('source', sa.String(100)),
        sa.Column('metadata', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('idx_health_data_user_id', 'health_data', ['user_id'])
    op.create_index('idx_health_data_data_type', 'health_data', ['data_type'])
    op.create_index('idx_health_data_created_at', 'health_data', ['created_at'])
    op.create_index('idx_health_data_user_type', 'health_data', ['user_id', 'data_type'])
    
    # 创建生命体征表
    op.create_table(
        'vital_signs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('heart_rate', sa.Float()),
        sa.Column('blood_pressure_systolic', sa.Float()),
        sa.Column('blood_pressure_diastolic', sa.Float()),
        sa.Column('temperature', sa.Float()),
        sa.Column('oxygen_saturation', sa.Float()),
        sa.Column('respiratory_rate', sa.Float()),
        sa.Column('recorded_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建生命体征索引
    op.create_index('idx_vital_signs_user_id', 'vital_signs', ['user_id'])
    op.create_index('idx_vital_signs_recorded_at', 'vital_signs', ['recorded_at'])
    op.create_index('idx_vital_signs_created_at', 'vital_signs', ['created_at'])
    op.create_index('idx_vital_signs_user_recorded', 'vital_signs', ['user_id', 'recorded_at'])
    
    # 创建诊断数据表
    op.create_table(
        'diagnostic_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('diagnosis_type', sa.String(100), nullable=False),
        sa.Column('diagnosis_result', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float()),
        sa.Column('raw_data', postgresql.JSON()),
        sa.Column('processed_data', postgresql.JSON()),
        sa.Column('doctor_id', sa.String(255)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建诊断数据索引
    op.create_index('idx_diagnostic_data_user_id', 'diagnostic_data', ['user_id'])
    op.create_index('idx_diagnostic_data_type', 'diagnostic_data', ['diagnosis_type'])
    op.create_index('idx_diagnostic_data_doctor', 'diagnostic_data', ['doctor_id'])
    op.create_index('idx_diagnostic_data_created_at', 'diagnostic_data', ['created_at'])
    
    # 创建中医诊断摘要表
    op.create_table(
        'tcm_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('mongo_id', sa.String(255)),
        sa.Column('diagnosis_method', sa.String(50)),
        sa.Column('main_syndrome', sa.String(200)),
        sa.Column('constitution_type', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建中医诊断索引
    op.create_index('idx_tcm_summary_user_id', 'tcm_summary', ['user_id'])
    op.create_index('idx_tcm_summary_mongo_id', 'tcm_summary', ['mongo_id'])
    op.create_index('idx_tcm_summary_method', 'tcm_summary', ['diagnosis_method'])
    op.create_index('idx_tcm_summary_created_at', 'tcm_summary', ['created_at'])
    
    # 创建数据质量表
    op.create_table(
        'data_quality',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_id', sa.String(255), nullable=False),
        sa.Column('data_type', sa.String(100), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('completeness_score', sa.Float()),
        sa.Column('accuracy_score', sa.Float()),
        sa.Column('timeliness_score', sa.Float()),
        sa.Column('consistency_score', sa.Float()),
        sa.Column('quality_details', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建数据质量索引
    op.create_index('idx_data_quality_data_id', 'data_quality', ['data_id'])
    op.create_index('idx_data_quality_type', 'data_quality', ['data_type'])
    op.create_index('idx_data_quality_score', 'data_quality', ['quality_score'])
    
    # 创建健康报告表
    op.create_table(
        'health_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('report_type', sa.String(100), nullable=False),
        sa.Column('health_score', sa.Float()),
        sa.Column('report_data', postgresql.JSON()),
        sa.Column('recommendations', postgresql.JSON()),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建健康报告索引
    op.create_index('idx_health_reports_user_id', 'health_reports', ['user_id'])
    op.create_index('idx_health_reports_type', 'health_reports', ['report_type'])
    op.create_index('idx_health_reports_generated_at', 'health_reports', ['generated_at'])
    
    # 创建数据同步日志表
    op.create_table(
        'data_sync_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.String(100), nullable=False),
        sa.Column('source_table', sa.String(100)),
        sa.Column('target_table', sa.String(100)),
        sa.Column('records_processed', sa.Integer()),
        sa.Column('records_success', sa.Integer()),
        sa.Column('records_failed', sa.Integer()),
        sa.Column('sync_status', sa.String(50)),
        sa.Column('error_message', sa.Text()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建同步日志索引
    op.create_index('idx_data_sync_log_type', 'data_sync_log', ['sync_type'])
    op.create_index('idx_data_sync_log_status', 'data_sync_log', ['sync_status'])
    op.create_index('idx_data_sync_log_started_at', 'data_sync_log', ['started_at'])


def downgrade():
    """删除表结构"""
    
    # 删除表（按依赖关系逆序）
    op.drop_table('data_sync_log')
    op.drop_table('health_reports')
    op.drop_table('data_quality')
    op.drop_table('tcm_summary')
    op.drop_table('diagnostic_data')
    op.drop_table('vital_signs')
    op.drop_table('health_data') 