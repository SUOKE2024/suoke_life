-- 索克生活数据库初始化脚本
-- 创建必要的表和初始数据

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    avatar_url TEXT,
    birth_date DATE,
    gender VARCHAR(10),
    constitution_type VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- 健康档案表
CREATE TABLE IF NOT EXISTS health_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    blood_type VARCHAR(10),
    allergies TEXT[],
    chronic_diseases TEXT[],
    medications TEXT[],
    emergency_contact JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 诊断会话表
CREATE TABLE IF NOT EXISTS diagnosis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(20) NOT NULL, -- 'four_diagnosis', 'consultation', 'follow_up'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'cancelled'
    symptoms TEXT,
    diagnosis_result JSONB,
    recommendations JSONB,
    agent_id VARCHAR(20) DEFAULT 'xiaoai',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 聊天记录表
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES diagnosis_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_id VARCHAR(20) NOT NULL,
    message_type VARCHAR(20) NOT NULL, -- 'text', 'image', 'audio', 'file'
    content TEXT,
    metadata JSONB,
    is_from_user BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 健康记录表
CREATE TABLE IF NOT EXISTS health_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    record_type VARCHAR(30) NOT NULL, -- 'vital_signs', 'lab_results', 'symptoms', 'medication'
    data JSONB NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'device', 'import'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 知识文章表
CREATE TABLE IF NOT EXISTS knowledge_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    category VARCHAR(50),
    tags TEXT[],
    author VARCHAR(100),
    reading_time INTEGER, -- 分钟
    difficulty_level VARCHAR(20) DEFAULT 'beginner', -- 'beginner', 'intermediate', 'advanced'
    is_published BOOLEAN DEFAULT true,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 学习路径表
CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    estimated_duration INTEGER, -- 小时
    article_ids UUID[],
    prerequisites TEXT[],
    learning_objectives TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 用户学习进度表
CREATE TABLE IF NOT EXISTS learning_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    path_id UUID REFERENCES learning_paths(id) ON DELETE CASCADE,
    article_id UUID REFERENCES knowledge_articles(id) ON DELETE CASCADE,
    progress_percentage INTEGER DEFAULT 0,
    completion_status VARCHAR(20) DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
    time_spent INTEGER DEFAULT 0, -- 分钟
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, path_id, article_id)
);

-- 健康计划表
CREATE TABLE IF NOT EXISTS health_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_type VARCHAR(30) NOT NULL, -- 'diet', 'exercise', 'medication', 'lifestyle'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    goals JSONB,
    schedule JSONB,
    recommendations JSONB,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'completed', 'cancelled'
    created_by VARCHAR(20) DEFAULT 'soer', -- 智能体ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 传感器数据表
CREATE TABLE IF NOT EXISTS sensor_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(50),
    sensor_type VARCHAR(30) NOT NULL, -- 'heart_rate', 'blood_pressure', 'temperature', 'steps'
    data_value DECIMAL(10,3),
    unit VARCHAR(20),
    metadata JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 食物数据库表
CREATE TABLE IF NOT EXISTS food_database (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    category VARCHAR(50),
    nutrition_per_100g JSONB,
    tcm_properties JSONB, -- 中医属性：性味、归经等
    health_benefits TEXT[],
    contraindications TEXT[],
    preparation_methods TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 营养记录表
CREATE TABLE IF NOT EXISTS nutrition_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    food_id UUID REFERENCES food_database(id),
    meal_type VARCHAR(20) NOT NULL, -- 'breakfast', 'lunch', 'dinner', 'snack'
    portion_size DECIMAL(5,2),
    calories DECIMAL(6,2),
    nutrition_data JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_health_profiles_user_id ON health_profiles(user_id);
CREATE INDEX idx_diagnosis_sessions_user_id ON diagnosis_sessions(user_id);
CREATE INDEX idx_diagnosis_sessions_status ON diagnosis_sessions(status);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_health_records_user_id ON health_records(user_id);
CREATE INDEX idx_health_records_type_date ON health_records(record_type, recorded_at);
CREATE INDEX idx_knowledge_articles_category ON knowledge_articles(category);
CREATE INDEX idx_knowledge_articles_published ON knowledge_articles(is_published);
CREATE INDEX idx_learning_progress_user_id ON learning_progress(user_id);
CREATE INDEX idx_health_plans_user_id ON health_plans(user_id);
CREATE INDEX idx_health_plans_status ON health_plans(status);
CREATE INDEX idx_sensor_data_user_id ON sensor_data(user_id);
CREATE INDEX idx_sensor_data_type_date ON sensor_data(sensor_type, recorded_at);
CREATE INDEX idx_food_database_category ON food_database(category);
CREATE INDEX idx_nutrition_records_user_id ON nutrition_records(user_id);

-- 创建全文搜索索引
CREATE INDEX idx_knowledge_articles_search ON knowledge_articles USING gin(to_tsvector('chinese', title || ' ' || content));
CREATE INDEX idx_food_database_search ON food_database USING gin(to_tsvector('chinese', name || ' ' || COALESCE(name_en, '')));

-- 插入初始数据
INSERT INTO food_database (name, name_en, category, nutrition_per_100g, tcm_properties, health_benefits) VALUES
('苹果', 'Apple', '水果', '{"calories": 52, "carbs": 14, "fiber": 2.4, "vitamin_c": 4.6}', '{"nature": "平", "flavor": "甘、酸", "meridian": ["脾", "胃"]}', ARRAY['生津止渴', '健脾开胃', '润肺止咳']),
('白萝卜', 'White Radish', '蔬菜', '{"calories": 16, "carbs": 3.4, "fiber": 1.6, "vitamin_c": 14.8}', '{"nature": "凉", "flavor": "甘、辛", "meridian": ["肺", "脾"]}', ARRAY['清热生津', '消食化积', '止咳化痰']),
('红枣', 'Red Date', '水果', '{"calories": 79, "carbs": 20.2, "fiber": 6.7, "iron": 0.48}', '{"nature": "温", "flavor": "甘", "meridian": ["脾", "胃"]}', ARRAY['补中益气', '养血安神', '健脾和胃']);

INSERT INTO knowledge_articles (title, content, summary, category, tags, author, reading_time, difficulty_level) VALUES
('中医四诊基础知识', '中医四诊是中医诊断疾病的基本方法，包括望、闻、问、切四种诊察方法...', '介绍中医四诊的基本概念和应用方法', '中医基础', ARRAY['四诊', '诊断', '中医'], '老克', 15, 'beginner'),
('春季养生要点', '春季是万物复苏的季节，人体阳气开始生发，养生应该顺应春季的特点...', '详细介绍春季养生的方法和注意事项', '养生保健', ARRAY['春季', '养生', '保健'], '老克', 10, 'beginner'),
('常见体质类型解析', '中医体质学说将人体体质分为九种基本类型，每种体质都有其特点...', '介绍九种体质类型的特征和调理方法', '体质调理', ARRAY['体质', '调理', '中医'], '老克', 20, 'intermediate');

-- 创建触发器函数用于更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建更新时间戳触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_health_profiles_updated_at BEFORE UPDATE ON health_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_diagnosis_sessions_updated_at BEFORE UPDATE ON diagnosis_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_articles_updated_at BEFORE UPDATE ON knowledge_articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_learning_paths_updated_at BEFORE UPDATE ON learning_paths FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_health_plans_updated_at BEFORE UPDATE ON health_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_food_database_updated_at BEFORE UPDATE ON food_database FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 完成初始化
INSERT INTO users (username, email, password_hash, full_name) VALUES
('admin', 'admin@suoke.life', '$2b$12$dummy_hash', '系统管理员');

COMMENT ON DATABASE suoke_db IS '索克生活健康管理平台数据库';