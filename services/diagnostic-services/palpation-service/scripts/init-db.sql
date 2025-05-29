-- 触诊服务数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- 创建触诊数据表
CREATE TABLE IF NOT EXISTS palpation_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    session_type VARCHAR(50) NOT NULL DEFAULT 'standard',
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建传感器数据表
CREATE TABLE IF NOT EXISTS sensor_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES palpation_sessions(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB NOT NULL,
    processed_data JSONB,
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES palpation_sessions(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL,
    algorithm_version VARCHAR(20) NOT NULL,
    confidence_score DECIMAL(3,2),
    results JSONB NOT NULL,
    recommendations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户配置表
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    medical_history JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建模型配置表
CREATE TABLE IF NOT EXISTS model_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    config_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_name, model_version)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_palpation_sessions_user_id ON palpation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_palpation_sessions_status ON palpation_sessions(status);
CREATE INDEX IF NOT EXISTS idx_palpation_sessions_created_at ON palpation_sessions(created_at);

CREATE INDEX IF NOT EXISTS idx_sensor_data_session_id ON sensor_data(session_id);
CREATE INDEX IF NOT EXISTS idx_sensor_data_sensor_type ON sensor_data(sensor_type);
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_data_quality_score ON sensor_data(quality_score);

CREATE INDEX IF NOT EXISTS idx_analysis_results_session_id ON analysis_results(session_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_results_confidence_score ON analysis_results(confidence_score);

CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

CREATE INDEX IF NOT EXISTS idx_model_configs_model_name ON model_configs(model_name);
CREATE INDEX IF NOT EXISTS idx_model_configs_is_active ON model_configs(is_active);

-- 创建GIN索引用于JSONB查询
CREATE INDEX IF NOT EXISTS idx_sensor_data_raw_data_gin ON sensor_data USING GIN (raw_data);
CREATE INDEX IF NOT EXISTS idx_analysis_results_results_gin ON analysis_results USING GIN (results);
CREATE INDEX IF NOT EXISTS idx_user_profiles_medical_history_gin ON user_profiles USING GIN (medical_history);

-- 创建触发器函数用于更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器
CREATE TRIGGER update_palpation_sessions_updated_at 
    BEFORE UPDATE ON palpation_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入默认模型配置
INSERT INTO model_configs (model_name, model_version, config_data, is_active) 
VALUES 
    ('pressure_analyzer', '1.0.0', '{"threshold": 0.8, "window_size": 100}', true),
    ('temperature_analyzer', '1.0.0', '{"threshold": 0.75, "smoothing": true}', true),
    ('texture_analyzer', '1.0.0', '{"feature_extraction": "cnn", "confidence_threshold": 0.7}', true),
    ('fusion_model', '1.0.0', '{"weights": {"pressure": 0.4, "temperature": 0.3, "texture": 0.3}}', true)
ON CONFLICT (model_name, model_version) DO NOTHING;

-- 创建视图用于快速查询
CREATE OR REPLACE VIEW session_summary AS
SELECT 
    ps.id,
    ps.user_id,
    ps.session_type,
    ps.start_time,
    ps.end_time,
    ps.status,
    COUNT(sd.id) as sensor_data_count,
    COUNT(ar.id) as analysis_count,
    AVG(ar.confidence_score) as avg_confidence
FROM palpation_sessions ps
LEFT JOIN sensor_data sd ON ps.id = sd.session_id
LEFT JOIN analysis_results ar ON ps.id = ar.session_id
GROUP BY ps.id, ps.user_id, ps.session_type, ps.start_time, ps.end_time, ps.status;

-- 设置权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO palpation_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO palpation_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO palpation_user; 