"""创建初始数据库表

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
    
    # 创建健康数据表
    op.create_table(
        'health_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('data_type', sa.Enum('VITAL_SIGNS', 'BLOOD_TEST', 'URINE_TEST', 'IMAGING', 'SYMPTOMS', 'MEDICATION', 'EXERCISE', 'SLEEP', 'DIET', 'MOOD', name='datatype'), nullable=False),
        sa.Column('data_source', sa.Enum('MANUAL', 'DEVICE', 'HOSPITAL', 'THIRD_PARTY', 'AI_ANALYSIS', name='datasource'), nullable=False),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('processed_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('device_id', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('is_validated', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_anomaly', sa.Boolean(), nullable=False, default=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('idx_health_data_user_id', 'health_data', ['user_id'])
    op.create_index('idx_health_data_data_type', 'health_data', ['data_type'])
    op.create_index('idx_health_data_recorded_at', 'health_data', ['recorded_at'])
    op.create_index('idx_health_data_created_at', 'health_data', ['created_at'])
    op.create_index('idx_health_data_user_type', 'health_data', ['user_id', 'data_type'])
    op.create_index('idx_health_data_user_recorded', 'health_data', ['user_id', 'recorded_at'])
    
    # 创建生命体征表
    op.create_table(
        'vital_signs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('blood_pressure_systolic', sa.Integer(), nullable=True),
        sa.Column('blood_pressure_diastolic', sa.Integer(), nullable=True),
        sa.Column('body_temperature', sa.Float(), nullable=True),
        sa.Column('respiratory_rate', sa.Integer(), nullable=True),
        sa.Column('oxygen_saturation', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('bmi', sa.Float(), nullable=True),
        sa.Column('device_id', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建生命体征索引
    op.create_index('idx_vital_signs_user_id', 'vital_signs', ['user_id'])
    op.create_index('idx_vital_signs_recorded_at', 'vital_signs', ['recorded_at'])
    op.create_index('idx_vital_signs_user_recorded', 'vital_signs', ['user_id', 'recorded_at'])
    
    # 创建中医诊断表
    op.create_table(
        'tcm_diagnosis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('diagnosis_type', sa.String(length=50), nullable=False),
        sa.Column('diagnosis_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('standardized_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('practitioner_id', sa.Integer(), nullable=True),
        sa.Column('clinic_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建中医诊断索引
    op.create_index('idx_tcm_diagnosis_user_id', 'tcm_diagnosis', ['user_id'])
    op.create_index('idx_tcm_diagnosis_type', 'tcm_diagnosis', ['diagnosis_type'])
    op.create_index('idx_tcm_diagnosis_recorded_at', 'tcm_diagnosis', ['recorded_at'])
    op.create_index('idx_tcm_diagnosis_practitioner', 'tcm_diagnosis', ['practitioner_id'])
    op.create_index('idx_tcm_diagnosis_session', 'tcm_diagnosis', ['session_id'])
    
    # 创建数据处理记录表
    op.create_table(
        'processing_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('health_data_id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('errors', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('warnings', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['health_data_id'], ['health_data.id'], ondelete='CASCADE')
    )
    
    # 创建处理记录索引
    op.create_index('idx_processing_records_health_data_id', 'processing_records', ['health_data_id'])
    op.create_index('idx_processing_records_stage', 'processing_records', ['stage'])
    op.create_index('idx_processing_records_status', 'processing_records', ['status'])
    op.create_index('idx_processing_records_created_at', 'processing_records', ['created_at'])
    
    # 创建数据质量统计表
    op.create_table(
        'data_quality_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('data_type', sa.String(length=50), nullable=True),
        sa.Column('total_records', sa.Integer(), nullable=False, default=0),
        sa.Column('valid_records', sa.Integer(), nullable=False, default=0),
        sa.Column('invalid_records', sa.Integer(), nullable=False, default=0),
        sa.Column('anomaly_records', sa.Integer(), nullable=False, default=0),
        sa.Column('avg_quality_score', sa.Float(), nullable=True),
        sa.Column('avg_confidence_score', sa.Float(), nullable=True),
        sa.Column('processing_errors', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', 'data_type', name='uq_quality_stats_date_type')
    )
    
    # 创建质量统计索引
    op.create_index('idx_quality_stats_date', 'data_quality_stats', ['date'])
    op.create_index('idx_quality_stats_data_type', 'data_quality_stats', ['data_type'])
    
    # 创建用户健康档案表
    op.create_table(
        'user_health_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('profile_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('last_vital_signs_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_checkup_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('health_score', sa.Float(), nullable=True),
        sa.Column('risk_factors', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('medications', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('allergies', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('chronic_conditions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_health_profile')
    )
    
    # 创建健康档案索引
    op.create_index('idx_user_health_profiles_user_id', 'user_health_profiles', ['user_id'])
    op.create_index('idx_user_health_profiles_health_score', 'user_health_profiles', ['health_score'])


def downgrade() -> None:
    """降级数据库结构"""
    
    # 删除表（按依赖关系逆序）
    op.drop_table('user_health_profiles')
    op.drop_table('data_quality_stats')
    op.drop_table('processing_records')
    op.drop_table('tcm_diagnosis')
    op.drop_table('vital_signs')
    op.drop_table('health_data')
    
    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS datatype')
    op.execute('DROP TYPE IF EXISTS datasource') 