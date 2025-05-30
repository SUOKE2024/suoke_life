-- PostgreSQL initialization script for xiaoke-service
-- Creates necessary tables and indexes for the service

-- 医疗资源表
CREATE TABLE IF NOT EXISTS medical_resources (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2),
    rating NUMERIC(3, 2),
    specialties JSONB,
    available_times JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建医疗资源类型索引
CREATE INDEX IF NOT EXISTS idx_medical_resources_type ON medical_resources(type);
-- 创建医疗资源位置索引
CREATE INDEX IF NOT EXISTS idx_medical_resources_location ON medical_resources(location);
-- 创建医疗资源评分索引
CREATE INDEX IF NOT EXISTS idx_medical_resources_rating ON medical_resources(rating);

-- 医生信息表
CREATE TABLE IF NOT EXISTS doctors (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(100),
    hospital VARCHAR(255),
    department VARCHAR(100),
    specialties JSONB,
    experience_years INTEGER,
    education TEXT,
    certificates JSONB,
    bio TEXT,
    avatar_url VARCHAR(255),
    contact_info JSONB,
    working_hours JSONB,
    rating NUMERIC(3, 2),
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建医生专长索引（使用GIN索引加速JSON查询）
CREATE INDEX IF NOT EXISTS idx_doctors_specialties ON doctors USING GIN (specialties);

-- 预约表
CREATE TABLE IF NOT EXISTS appointments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    doctor_id VARCHAR(36) NOT NULL,
    appointment_type VARCHAR(50) NOT NULL,
    appointment_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL,
    symptoms TEXT,
    constitution_type VARCHAR(50),
    meeting_link VARCHAR(255),
    location VARCHAR(255),
    notes TEXT,
    payment_id VARCHAR(36),
    payment_status VARCHAR(20),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_doctor FOREIGN KEY(doctor_id) REFERENCES doctors(id)
);

-- 创建预约用户索引
CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id);
-- 创建预约医生索引
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_id ON appointments(doctor_id);
-- 创建预约时间索引
CREATE INDEX IF NOT EXISTS idx_appointments_appointment_time ON appointments(appointment_time);
-- 创建预约状态索引
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    origin VARCHAR(255),
    producer VARCHAR(255),
    price NUMERIC(10, 2) NOT NULL,
    image_url VARCHAR(255),
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    constitution_benefits JSONB,
    health_benefits JSONB,
    harvesting_date DATE,
    shelf_life INTEGER, -- 保质期（天）
    is_seasonal BOOLEAN DEFAULT FALSE,
    season VARCHAR(50),
    nutrition_facts JSONB,
    ingredients TEXT,
    storage_instructions TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建产品类别索引
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
-- 创建产品季节索引
CREATE INDEX IF NOT EXISTS idx_products_season ON products(season);
-- 创建体质受益索引
CREATE INDEX IF NOT EXISTS idx_products_constitution_benefits ON products USING GIN (constitution_benefits);

-- 产品定制订单表
CREATE TABLE IF NOT EXISTS product_customizations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    constitution_type VARCHAR(50),
    packaging_preference VARCHAR(50),
    quantity INTEGER NOT NULL,
    need_delivery BOOLEAN DEFAULT TRUE,
    delivery_address TEXT,
    total_price NUMERIC(10, 2) NOT NULL,
    delivery_estimate TIMESTAMP WITH TIME ZONE,
    payment_id VARCHAR(36),
    payment_status VARCHAR(20) DEFAULT 'PENDING',
    payment_link VARCHAR(255),
    status VARCHAR(20) DEFAULT 'CREATED',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建产品定制用户索引
CREATE INDEX IF NOT EXISTS idx_product_customizations_user_id ON product_customizations(user_id);
-- 创建产品定制状态索引
CREATE INDEX IF NOT EXISTS idx_product_customizations_status ON product_customizations(status);

-- 定制产品明细表
CREATE TABLE IF NOT EXISTS customization_items (
    id VARCHAR(36) PRIMARY KEY,
    customization_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customization FOREIGN KEY(customization_id) REFERENCES product_customizations(id),
    CONSTRAINT fk_product FOREIGN KEY(product_id) REFERENCES products(id)
);

-- 创建定制明细索引
CREATE INDEX IF NOT EXISTS idx_customization_items_customization_id ON customization_items(customization_id);

-- 产品溯源表
CREATE TABLE IF NOT EXISTS product_traces (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL,
    batch_id VARCHAR(36) NOT NULL,
    stage_name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    operator VARCHAR(255),
    details JSONB,
    verification_hash VARCHAR(255),
    blockchain_tx VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product FOREIGN KEY(product_id) REFERENCES products(id)
);

-- 创建产品溯源索引
CREATE INDEX IF NOT EXISTS idx_product_traces_product_batch ON product_traces(product_id, batch_id);

-- 支付记录表
CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    order_id VARCHAR(36) NOT NULL,
    order_type VARCHAR(50) NOT NULL, -- APPOINTMENT, PRODUCT, SUBSCRIPTION
    payment_method VARCHAR(50) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'CNY',
    status VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(255),
    payment_url VARCHAR(255),
    receipt_url VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建支付用户索引
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
-- 创建支付订单索引
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
-- 创建支付状态索引
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- 订阅计划表
CREATE TABLE IF NOT EXISTS subscription_plans (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    duration_months INTEGER NOT NULL,
    included_services JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 用户订阅表
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    plan_id VARCHAR(36) NOT NULL,
    payment_method VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    next_billing_date TIMESTAMP WITH TIME ZONE,
    payment_id VARCHAR(36),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_plan FOREIGN KEY(plan_id) REFERENCES subscription_plans(id)
);

-- 创建用户订阅索引
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
-- 创建订阅状态索引
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);
-- 创建订阅结束日期索引
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_end_date ON user_subscriptions(end_date);

-- 初始化一些基础订阅计划数据
INSERT INTO subscription_plans (id, name, description, price, duration_months, included_services)
VALUES 
('basic', '基础健康会员', '基础健康咨询和体质评估服务', 29.9, 1, '["基础健康咨询", "体质测评", "基础食谱推荐"]'),
('premium', '健康优享会员', '全面健康管理与个性化服务', 99.9, 1, '["高级健康咨询", "全套五诊分析", "个性化食谱", "季节性养生方案"]'),
('family', '家庭健康套餐', '全家人的健康管理服务', 199.9, 1, '["家庭成员体质分析", "家庭共享健康方案", "定制家庭食谱", "农场认养服务"]');

-- 初始化一些示例医生数据
INSERT INTO doctors (id, name, title, hospital, department, specialties, experience_years, rating)
VALUES 
('doc_001', '张医生', '主任医师', '北京中医院', '内科', '["气虚", "阳虚", "中医内科"]', 15, 4.8),
('doc_002', '李医生', '副主任医师', '上海中医药大学附属医院', '妇科', '["血瘀", "痰湿", "妇科调理"]', 12, 4.7),
('doc_003', '王医生', '主治医师', '广州中医药大学第一附属医院', '针灸科', '["针灸", "经络调理", "疼痛管理"]', 8, 4.5);

-- 初始化一些示例产品数据
INSERT INTO products (id, name, description, category, origin, producer, price, stock_quantity, constitution_benefits, health_benefits, season, is_seasonal)
VALUES 
('prod_001', '有机黑木耳', '长白山特产，富含多种氨基酸和维生素', '食材', '吉林长白山', '健康农场', 58.0, 100, '["气虚", "阴虚"]', '["补血养颜", "提高免疫力"]', 'ALL', false),
('prod_002', '野生蓝莓', '东北特产野生蓝莓，富含花青素', '食材', '黑龙江', '森林农场', 128.0, 50, '["阴虚", "血瘀"]', '["明目", "抗氧化"]', 'SUMMER', true),
('prod_003', '有机燕麦片', '精选燕麦，富含膳食纤维', '食材', '内蒙古', '草原牧场', 45.0, 200, '["痰湿", "湿热"]', '["降低胆固醇", "促进消化"]', 'ALL', false),
('prod_004', '枸杞茶', '宁夏特产枸杞制成，滋补肝肾', '茶饮', '宁夏', '枸杞之乡', 68.0, 100, '["阴虚", "气虚"]', '["养肝明目", "改善睡眠"]', 'WINTER', true),
('prod_005', '红枣桂圆茶', '补血安神茶饮', '茶饮', '新疆', '和田农场', 78.0, 80, '["气血两虚"]', '["补血", "安神"]', 'AUTUMN', true);