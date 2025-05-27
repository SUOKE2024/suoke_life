-- 索克生活人工审核系统数据库设计
-- Suoke Life Human Review System Database Schema
-- 
-- 创建日期: 2024-12-19
-- 版本: 1.0.0
-- 数据库: PostgreSQL 14+

-- 创建数据库（如果不存在）
-- CREATE DATABASE suoke_review WITH ENCODING 'UTF8' LC_COLLATE='zh_CN.UTF-8' LC_CTYPE='zh_CN.UTF-8';

-- 使用数据库
-- \c suoke_review;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- 创建枚举类型
CREATE TYPE review_status AS ENUM (
    'pending',          -- 待审核
    'in_progress',      -- 审核中
    'approved',         -- 已通过
    'rejected',         -- 已拒绝
    'needs_revision'    -- 需要修改
);

CREATE TYPE review_priority AS ENUM (
    'low',              -- 低优先级
    'normal',           -- 普通优先级
    'high',             -- 高优先级
    'urgent'            -- 紧急
);

CREATE TYPE review_type AS ENUM (
    'medical_diagnosis',        -- 医疗诊断
    'health_plan',             -- 健康计划
    'nutrition_advice',        -- 营养建议
    'product_recommendation',  -- 产品推荐
    'emergency_response',      -- 紧急响应
    'general_advice'           -- 一般建议
);

CREATE TYPE reviewer_status AS ENUM (
    'active',           -- 活跃
    'inactive',         -- 非活跃
    'suspended',        -- 暂停
    'offline'           -- 离线
);

-- 1. 审核员表
CREATE TABLE reviewers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reviewer_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    specialties TEXT[] NOT NULL DEFAULT '{}',
    qualifications JSONB DEFAULT '{}',
    max_concurrent_tasks INTEGER DEFAULT 5,
    current_tasks INTEGER DEFAULT 0,
    average_review_time DECIMAL(10,2) DEFAULT 30.0,
    status reviewer_status DEFAULT 'active',
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- 绩效统计
    total_reviews INTEGER DEFAULT 0,
    approved_reviews INTEGER DEFAULT 0,
    rejected_reviews INTEGER DEFAULT 0,
    quality_score DECIMAL(3,2) DEFAULT 1.0,
    
    -- 审核员认证信息
    license_number VARCHAR(100),
    license_expiry DATE,
    certification_level VARCHAR(50),
    
    CONSTRAINT valid_quality_score CHECK (quality_score >= 0 AND quality_score <= 1),
    CONSTRAINT valid_concurrent_tasks CHECK (current_tasks <= max_concurrent_tasks)
);

-- 2. 审核任务表
CREATE TABLE review_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(100) UNIQUE NOT NULL,
    review_type review_type NOT NULL,
    priority review_priority DEFAULT 'normal',
    status review_status DEFAULT 'pending',
    
    -- 任务内容
    content JSONB NOT NULL,
    original_content JSONB,
    revised_content JSONB,
    
    -- 用户和智能体信息
    user_id VARCHAR(100) NOT NULL,
    agent_id VARCHAR(50) NOT NULL,
    
    -- 审核员分配
    assigned_to UUID REFERENCES reviewers(id),
    assigned_at TIMESTAMP WITH TIME ZONE,
    
    -- 时间信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    estimated_completion TIMESTAMP WITH TIME ZONE,
    
    -- 审核结果
    review_comments TEXT,
    review_result JSONB,
    review_duration INTEGER, -- 审核用时（分钟）
    
    -- 风险评估
    risk_level VARCHAR(20) DEFAULT 'low',
    risk_factors TEXT[],
    auto_review_score DECIMAL(3,2),
    
    -- 质量控制
    quality_checked BOOLEAN DEFAULT false,
    quality_score DECIMAL(3,2),
    quality_comments TEXT,
    
    CONSTRAINT valid_auto_review_score CHECK (auto_review_score IS NULL OR (auto_review_score >= 0 AND auto_review_score <= 1)),
    CONSTRAINT valid_quality_score CHECK (quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1))
);

-- 3. 审核历史表
CREATE TABLE review_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES review_tasks(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES reviewers(id),
    action VARCHAR(50) NOT NULL, -- 'assigned', 'started', 'completed', 'reassigned'
    old_status review_status,
    new_status review_status,
    comments TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. 审核标准表
CREATE TABLE review_standards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    standard_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    review_type review_type NOT NULL,
    criteria JSONB NOT NULL,
    scoring_rules JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    version VARCHAR(20) DEFAULT '1.0',
    created_by UUID REFERENCES reviewers(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. 审核员培训记录表
CREATE TABLE reviewer_training (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reviewer_id UUID REFERENCES reviewers(id) ON DELETE CASCADE,
    training_type VARCHAR(100) NOT NULL,
    training_name VARCHAR(200) NOT NULL,
    training_content TEXT,
    completion_date DATE,
    score DECIMAL(5,2),
    certificate_url VARCHAR(500),
    is_mandatory BOOLEAN DEFAULT false,
    expires_at DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. 系统配置表
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. 审核统计表
CREATE TABLE review_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    reviewer_id UUID REFERENCES reviewers(id),
    
    -- 统计数据
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    approved_tasks INTEGER DEFAULT 0,
    rejected_tasks INTEGER DEFAULT 0,
    revision_tasks INTEGER DEFAULT 0,
    
    -- 时间统计
    average_review_time DECIMAL(10,2) DEFAULT 0,
    total_review_time INTEGER DEFAULT 0, -- 总审核时间（分钟）
    
    -- 质量统计
    quality_score DECIMAL(3,2) DEFAULT 1.0,
    error_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date, reviewer_id)
);

-- 8. 审核队列表（用于实时队列管理）
CREATE TABLE review_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES review_tasks(id) ON DELETE CASCADE,
    priority_score INTEGER NOT NULL, -- 优先级分数，用于排序
    queue_position INTEGER,
    estimated_wait_time INTEGER, -- 预估等待时间（分钟）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(task_id)
);

-- 9. 审核通知表
CREATE TABLE review_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipient_type VARCHAR(20) NOT NULL, -- 'reviewer', 'admin', 'user'
    recipient_id VARCHAR(100) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. 审核日志表
CREATE TABLE review_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES review_tasks(id),
    reviewer_id UUID REFERENCES reviewers(id),
    action VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
-- 审核员表索引
CREATE INDEX idx_reviewers_reviewer_id ON reviewers(reviewer_id);
CREATE INDEX idx_reviewers_status ON reviewers(status);
CREATE INDEX idx_reviewers_specialties ON reviewers USING GIN(specialties);
CREATE INDEX idx_reviewers_is_available ON reviewers(is_available);

-- 审核任务表索引
CREATE INDEX idx_review_tasks_task_id ON review_tasks(task_id);
CREATE INDEX idx_review_tasks_status ON review_tasks(status);
CREATE INDEX idx_review_tasks_priority ON review_tasks(priority);
CREATE INDEX idx_review_tasks_review_type ON review_tasks(review_type);
CREATE INDEX idx_review_tasks_assigned_to ON review_tasks(assigned_to);
CREATE INDEX idx_review_tasks_user_id ON review_tasks(user_id);
CREATE INDEX idx_review_tasks_agent_id ON review_tasks(agent_id);
CREATE INDEX idx_review_tasks_created_at ON review_tasks(created_at);
CREATE INDEX idx_review_tasks_status_priority ON review_tasks(status, priority);
CREATE INDEX idx_review_tasks_content ON review_tasks USING GIN(content);

-- 审核历史表索引
CREATE INDEX idx_review_history_task_id ON review_history(task_id);
CREATE INDEX idx_review_history_reviewer_id ON review_history(reviewer_id);
CREATE INDEX idx_review_history_created_at ON review_history(created_at);

-- 审核队列表索引
CREATE INDEX idx_review_queue_priority_score ON review_queue(priority_score DESC);
CREATE INDEX idx_review_queue_created_at ON review_queue(created_at);

-- 审核统计表索引
CREATE INDEX idx_review_statistics_date ON review_statistics(date);
CREATE INDEX idx_review_statistics_reviewer_id ON review_statistics(reviewer_id);
CREATE INDEX idx_review_statistics_date_reviewer ON review_statistics(date, reviewer_id);

-- 审核通知表索引
CREATE INDEX idx_review_notifications_recipient ON review_notifications(recipient_type, recipient_id);
CREATE INDEX idx_review_notifications_is_read ON review_notifications(is_read);
CREATE INDEX idx_review_notifications_created_at ON review_notifications(created_at);

-- 审核日志表索引
CREATE INDEX idx_review_logs_task_id ON review_logs(task_id);
CREATE INDEX idx_review_logs_reviewer_id ON review_logs(reviewer_id);
CREATE INDEX idx_review_logs_created_at ON review_logs(created_at);
CREATE INDEX idx_review_logs_action ON review_logs(action);

-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加更新时间触发器
CREATE TRIGGER update_reviewers_updated_at BEFORE UPDATE ON reviewers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_review_tasks_updated_at BEFORE UPDATE ON review_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_review_standards_updated_at BEFORE UPDATE ON review_standards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建审核员工作负载更新函数
CREATE OR REPLACE FUNCTION update_reviewer_workload()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.assigned_to IS NOT NULL THEN
        -- 分配任务时增加工作负载
        UPDATE reviewers 
        SET current_tasks = current_tasks + 1 
        WHERE id = NEW.assigned_to;
    ELSIF TG_OP = 'UPDATE' THEN
        -- 任务状态变更时更新工作负载
        IF OLD.assigned_to IS NOT NULL AND NEW.status IN ('approved', 'rejected', 'needs_revision') 
           AND OLD.status NOT IN ('approved', 'rejected', 'needs_revision') THEN
            -- 任务完成，减少工作负载
            UPDATE reviewers 
            SET current_tasks = current_tasks - 1,
                total_reviews = total_reviews + 1,
                approved_reviews = CASE WHEN NEW.status = 'approved' THEN approved_reviews + 1 ELSE approved_reviews END,
                rejected_reviews = CASE WHEN NEW.status = 'rejected' THEN rejected_reviews + 1 ELSE rejected_reviews END
            WHERE id = OLD.assigned_to;
        END IF;
        
        -- 重新分配任务
        IF OLD.assigned_to != NEW.assigned_to THEN
            IF OLD.assigned_to IS NOT NULL THEN
                UPDATE reviewers SET current_tasks = current_tasks - 1 WHERE id = OLD.assigned_to;
            END IF;
            IF NEW.assigned_to IS NOT NULL THEN
                UPDATE reviewers SET current_tasks = current_tasks + 1 WHERE id = NEW.assigned_to;
            END IF;
        END IF;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- 创建工作负载触发器
CREATE TRIGGER trigger_update_reviewer_workload
    AFTER INSERT OR UPDATE ON review_tasks
    FOR EACH ROW EXECUTE FUNCTION update_reviewer_workload();

-- 创建审核队列管理函数
CREATE OR REPLACE FUNCTION manage_review_queue()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'pending' THEN
        -- 新任务加入队列
        INSERT INTO review_queue (task_id, priority_score, estimated_wait_time)
        VALUES (
            NEW.id,
            CASE NEW.priority
                WHEN 'urgent' THEN 1000
                WHEN 'high' THEN 100
                WHEN 'normal' THEN 10
                WHEN 'low' THEN 1
            END,
            CASE NEW.priority
                WHEN 'urgent' THEN 15
                WHEN 'high' THEN 30
                WHEN 'normal' THEN 60
                WHEN 'low' THEN 120
            END
        );
    ELSIF TG_OP = 'UPDATE' AND OLD.status = 'pending' AND NEW.status != 'pending' THEN
        -- 任务开始处理，从队列移除
        DELETE FROM review_queue WHERE task_id = NEW.id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- 创建队列管理触发器
CREATE TRIGGER trigger_manage_review_queue
    AFTER INSERT OR UPDATE ON review_tasks
    FOR EACH ROW EXECUTE FUNCTION manage_review_queue();

-- 插入初始数据

-- 插入系统配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('review_time_limits', '{"urgent": 15, "high": 30, "normal": 60, "low": 120}', '各优先级审核时间限制（分钟）'),
('auto_approve_threshold', '0.8', '自动通过阈值'),
('auto_reject_threshold', '0.3', '自动拒绝阈值'),
('quality_check_ratio', '0.1', '质量抽检比例'),
('max_queue_size', '1000', '最大队列大小'),
('notification_settings', '{"email": true, "sms": false, "push": true}', '通知设置');

-- 插入审核标准
INSERT INTO review_standards (standard_id, name, review_type, criteria, description) VALUES
('medical_diagnosis_v1', '医疗诊断审核标准', 'medical_diagnosis', 
 '{"accuracy": 0.3, "safety": 0.4, "completeness": 0.2, "clarity": 0.1}',
 '医疗诊断类内容的审核标准'),
('health_plan_v1', '健康计划审核标准', 'health_plan',
 '{"feasibility": 0.3, "safety": 0.3, "personalization": 0.2, "evidence": 0.2}',
 '健康计划类内容的审核标准'),
('nutrition_advice_v1', '营养建议审核标准', 'nutrition_advice',
 '{"scientific": 0.4, "safety": 0.3, "practicality": 0.2, "clarity": 0.1}',
 '营养建议类内容的审核标准'),
('product_recommendation_v1', '产品推荐审核标准', 'product_recommendation',
 '{"safety": 0.4, "suitability": 0.3, "transparency": 0.2, "compliance": 0.1}',
 '产品推荐类内容的审核标准'),
('emergency_response_v1', '紧急响应审核标准', 'emergency_response',
 '{"urgency": 0.4, "accuracy": 0.3, "safety": 0.2, "clarity": 0.1}',
 '紧急响应类内容的审核标准');

-- 插入示例审核员（生产环境中应该通过管理界面添加）
INSERT INTO reviewers (reviewer_id, name, email, specialties, qualifications, max_concurrent_tasks) VALUES
('dr_zhang', '张医生', 'dr.zhang@suoke.life', 
 ARRAY['中医诊断', '体质辨识', '医疗建议'], 
 '{"license": "中医执业医师", "experience": "10年", "specialization": "中医内科"}', 3),
('nutritionist_li', '李营养师', 'nutritionist.li@suoke.life',
 ARRAY['营养分析', '饮食建议', '健康计划'],
 '{"license": "注册营养师", "experience": "8年", "specialization": "临床营养"}', 5),
('pharmacist_wang', '王药师', 'pharmacist.wang@suoke.life',
 ARRAY['药物建议', '产品推荐', '安全性评估'],
 '{"license": "执业药师", "experience": "12年", "specialization": "临床药学"}', 4),
('emergency_specialist', '急诊专家', 'emergency@suoke.life',
 ARRAY['紧急响应', '风险评估', '危急情况'],
 '{"license": "急诊科主治医师", "experience": "15年", "specialization": "急诊医学"}', 2);

-- 创建视图

-- 审核员工作负载视图
CREATE VIEW reviewer_workload_view AS
SELECT 
    r.id,
    r.reviewer_id,
    r.name,
    r.specialties,
    r.current_tasks,
    r.max_concurrent_tasks,
    ROUND(r.current_tasks::DECIMAL / r.max_concurrent_tasks, 2) AS utilization_rate,
    r.average_review_time,
    r.quality_score,
    r.status,
    r.is_available
FROM reviewers r
WHERE r.status = 'active';

-- 待审核任务视图
CREATE VIEW pending_tasks_view AS
SELECT 
    rt.id,
    rt.task_id,
    rt.review_type,
    rt.priority,
    rt.user_id,
    rt.agent_id,
    rt.created_at,
    rt.estimated_completion,
    rq.priority_score,
    rq.estimated_wait_time,
    r.name AS assigned_reviewer
FROM review_tasks rt
LEFT JOIN review_queue rq ON rt.id = rq.task_id
LEFT JOIN reviewers r ON rt.assigned_to = r.id
WHERE rt.status IN ('pending', 'in_progress')
ORDER BY rq.priority_score DESC, rt.created_at ASC;

-- 审核统计汇总视图
CREATE VIEW review_stats_summary AS
SELECT 
    DATE(created_at) AS review_date,
    COUNT(*) AS total_tasks,
    COUNT(CASE WHEN status = 'approved' THEN 1 END) AS approved_count,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) AS rejected_count,
    COUNT(CASE WHEN status = 'needs_revision' THEN 1 END) AS revision_count,
    AVG(review_duration) AS avg_review_time,
    AVG(CASE WHEN quality_score IS NOT NULL THEN quality_score END) AS avg_quality_score
FROM review_tasks
WHERE reviewed_at IS NOT NULL
GROUP BY DATE(created_at)
ORDER BY review_date DESC;

-- 创建函数：获取审核员推荐
CREATE OR REPLACE FUNCTION get_recommended_reviewer(
    p_review_type review_type,
    p_priority review_priority DEFAULT 'normal'
)
RETURNS TABLE(
    reviewer_id UUID,
    name VARCHAR(100),
    current_load DECIMAL,
    estimated_time INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.name,
        ROUND(r.current_tasks::DECIMAL / r.max_concurrent_tasks, 2) AS current_load,
        ROUND(r.average_review_time)::INTEGER AS estimated_time
    FROM reviewers r
    WHERE r.status = 'active' 
      AND r.is_available = true
      AND r.current_tasks < r.max_concurrent_tasks
      AND (
          CASE p_review_type
              WHEN 'medical_diagnosis' THEN r.specialties && ARRAY['中医诊断', '医疗建议']
              WHEN 'health_plan' THEN r.specialties && ARRAY['营养分析', '健康计划']
              WHEN 'nutrition_advice' THEN r.specialties && ARRAY['营养分析', '饮食建议']
              WHEN 'product_recommendation' THEN r.specialties && ARRAY['产品推荐', '安全性评估']
              WHEN 'emergency_response' THEN r.specialties && ARRAY['紧急响应', '危急情况']
              ELSE true
          END
      )
    ORDER BY 
        CASE p_priority
            WHEN 'urgent' THEN r.current_tasks
            ELSE r.current_tasks::DECIMAL / r.max_concurrent_tasks
        END ASC,
        r.quality_score DESC,
        r.average_review_time ASC
    LIMIT 3;
END;
$$ LANGUAGE plpgsql;

-- 创建函数：获取队列统计
CREATE OR REPLACE FUNCTION get_queue_statistics()
RETURNS TABLE(
    total_pending INTEGER,
    urgent_tasks INTEGER,
    high_priority_tasks INTEGER,
    average_wait_time DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER AS total_pending,
        COUNT(CASE WHEN rt.priority = 'urgent' THEN 1 END)::INTEGER AS urgent_tasks,
        COUNT(CASE WHEN rt.priority = 'high' THEN 1 END)::INTEGER AS high_priority_tasks,
        AVG(rq.estimated_wait_time) AS average_wait_time
    FROM review_tasks rt
    JOIN review_queue rq ON rt.id = rq.task_id
    WHERE rt.status = 'pending';
END;
$$ LANGUAGE plpgsql;

-- 授权（根据实际用户调整）
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO suoke_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO suoke_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO suoke_user;

-- 创建备份和维护脚本的存储过程
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- 清理旧的审核日志
    DELETE FROM review_logs 
    WHERE created_at < CURRENT_DATE - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- 清理已读的旧通知
    DELETE FROM review_notifications 
    WHERE is_read = true 
      AND created_at < CURRENT_DATE - INTERVAL '1 day' * (days_to_keep / 2);
    
    -- 清理旧的统计数据（保留更长时间）
    DELETE FROM review_statistics 
    WHERE date < CURRENT_DATE - INTERVAL '1 day' * (days_to_keep * 2);
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 数据库初始化完成
SELECT 'Database schema created successfully!' AS status; 