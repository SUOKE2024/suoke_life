-- 人工审核服务数据库初始化脚本
-- 创建审核相关的数据表

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 审核任务表
CREATE TABLE IF NOT EXISTS review_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'text',
    content_hash VARCHAR(64),
    source_id VARCHAR(255) NOT NULL,
    source_type VARCHAR(100) NOT NULL,
    submitter_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    assigned_to VARCHAR(255),
    ai_analysis JSONB,
    ai_task_id VARCHAR(255),
    estimated_time INTEGER DEFAULT 0,
    actual_time INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    deadline TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    
    -- 约束
    CONSTRAINT chk_status CHECK (status IN ('pending', 'assigned', 'in_progress', 'completed', 'cancelled', 'failed')),
    CONSTRAINT chk_priority CHECK (priority IN ('very_low', 'low', 'medium', 'high', 'very_high')),
    CONSTRAINT chk_content_type CHECK (content_type IN ('text', 'image', 'video', 'audio', 'document', 'mixed'))
);

-- 审核结果表
CREATE TABLE IF NOT EXISTS review_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES review_tasks(id) ON DELETE CASCADE,
    reviewer_id VARCHAR(255) NOT NULL,
    decision VARCHAR(50) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    comments TEXT,
    tags TEXT[],
    processing_time INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    
    -- 约束
    CONSTRAINT chk_decision CHECK (decision IN ('approved', 'rejected', 'needs_revision', 'escalated'))
);

-- 审核员档案表
CREATE TABLE IF NOT EXISTS reviewer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    specialties TEXT[],
    skill_level VARCHAR(20) DEFAULT 'junior',
    max_concurrent_tasks INTEGER DEFAULT 5,
    avg_processing_time DECIMAL(8,2) DEFAULT 0,
    accuracy_rate DECIMAL(3,2) DEFAULT 0,
    total_tasks_completed INTEGER DEFAULT 0,
    total_tasks_assigned INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    last_active_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    
    -- 约束
    CONSTRAINT chk_skill_level CHECK (skill_level IN ('junior', 'intermediate', 'senior', 'expert')),
    CONSTRAINT chk_reviewer_status CHECK (status IN ('active', 'inactive', 'suspended'))
);

-- 审核评论表
CREATE TABLE IF NOT EXISTS review_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES review_tasks(id) ON DELETE CASCADE,
    result_id UUID REFERENCES review_results(id) ON DELETE CASCADE,
    author_id VARCHAR(255) NOT NULL,
    author_type VARCHAR(20) NOT NULL DEFAULT 'reviewer',
    content TEXT NOT NULL,
    comment_type VARCHAR(50) DEFAULT 'general',
    parent_id UUID REFERENCES review_comments(id) ON DELETE CASCADE,
    is_internal BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    
    -- 约束
    CONSTRAINT chk_author_type CHECK (author_type IN ('reviewer', 'admin', 'system', 'submitter')),
    CONSTRAINT chk_comment_type CHECK (comment_type IN ('general', 'quality', 'compliance', 'suggestion', 'question'))
);

-- 审核统计表
CREATE TABLE IF NOT EXISTS review_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    reviewer_id VARCHAR(255),
    content_type VARCHAR(50),
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    approved_tasks INTEGER DEFAULT 0,
    rejected_tasks INTEGER DEFAULT 0,
    avg_processing_time DECIMAL(8,2) DEFAULT 0,
    avg_confidence DECIMAL(3,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(date, reviewer_id, content_type)
);

-- 工作流配置表
CREATE TABLE IF NOT EXISTS workflow_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    content_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    auto_assign BOOLEAN DEFAULT true,
    required_reviewers INTEGER DEFAULT 1,
    escalation_threshold DECIMAL(3,2) DEFAULT 0.5,
    time_limit INTEGER DEFAULT 3600, -- 秒
    rules JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- 任务分配历史表
CREATE TABLE IF NOT EXISTS task_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES review_tasks(id) ON DELETE CASCADE,
    reviewer_id VARCHAR(255) NOT NULL,
    assigned_by VARCHAR(255),
    assignment_type VARCHAR(20) DEFAULT 'manual',
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unassigned_at TIMESTAMP WITH TIME ZONE,
    reason VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    
    -- 约束
    CONSTRAINT chk_assignment_type CHECK (assignment_type IN ('manual', 'auto', 'escalated', 'reassigned'))
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_review_tasks_status ON review_tasks(status);
CREATE INDEX IF NOT EXISTS idx_review_tasks_priority ON review_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_review_tasks_assigned_to ON review_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_review_tasks_created_at ON review_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_review_tasks_content_type ON review_tasks(content_type);
CREATE INDEX IF NOT EXISTS idx_review_tasks_source ON review_tasks(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_review_tasks_submitter ON review_tasks(submitter_id);

CREATE INDEX IF NOT EXISTS idx_review_results_task_id ON review_results(task_id);
CREATE INDEX IF NOT EXISTS idx_review_results_reviewer_id ON review_results(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_review_results_decision ON review_results(decision);
CREATE INDEX IF NOT EXISTS idx_review_results_created_at ON review_results(created_at);

CREATE INDEX IF NOT EXISTS idx_reviewer_profiles_user_id ON reviewer_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_reviewer_profiles_status ON reviewer_profiles(status);
CREATE INDEX IF NOT EXISTS idx_reviewer_profiles_skill_level ON reviewer_profiles(skill_level);

CREATE INDEX IF NOT EXISTS idx_review_comments_task_id ON review_comments(task_id);
CREATE INDEX IF NOT EXISTS idx_review_comments_result_id ON review_comments(result_id);
CREATE INDEX IF NOT EXISTS idx_review_comments_author_id ON review_comments(author_id);

CREATE INDEX IF NOT EXISTS idx_review_statistics_date ON review_statistics(date);
CREATE INDEX IF NOT EXISTS idx_review_statistics_reviewer_id ON review_statistics(reviewer_id);

CREATE INDEX IF NOT EXISTS idx_task_assignments_task_id ON task_assignments(task_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_reviewer_id ON task_assignments(reviewer_id);

-- 全文搜索索引
CREATE INDEX IF NOT EXISTS idx_review_tasks_content_gin ON review_tasks USING gin(to_tsvector('chinese', content));
CREATE INDEX IF NOT EXISTS idx_review_comments_content_gin ON review_comments USING gin(to_tsvector('chinese', content));

-- 创建触发器函数：更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表创建更新时间戳触发器
CREATE TRIGGER update_review_tasks_updated_at BEFORE UPDATE ON review_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_review_results_updated_at BEFORE UPDATE ON review_results FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reviewer_profiles_updated_at BEFORE UPDATE ON reviewer_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_review_comments_updated_at BEFORE UPDATE ON review_comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_review_statistics_updated_at BEFORE UPDATE ON review_statistics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_configs_updated_at BEFORE UPDATE ON workflow_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建视图：审核任务详情视图
CREATE OR REPLACE VIEW review_task_details AS
SELECT 
    rt.id,
    rt.content,
    rt.content_type,
    rt.source_id,
    rt.source_type,
    rt.submitter_id,
    rt.status,
    rt.priority,
    rt.assigned_to,
    rt.ai_analysis,
    rt.estimated_time,
    rt.actual_time,
    rt.created_at,
    rt.updated_at,
    rt.assigned_at,
    rt.started_at,
    rt.completed_at,
    rt.deadline,
    rt.metadata,
    rp.name as reviewer_name,
    rp.skill_level as reviewer_skill_level,
    COUNT(rr.id) as result_count,
    MAX(rr.created_at) as last_result_at
FROM review_tasks rt
LEFT JOIN reviewer_profiles rp ON rt.assigned_to = rp.user_id
LEFT JOIN review_results rr ON rt.id = rr.task_id
GROUP BY rt.id, rp.name, rp.skill_level;

-- 创建视图：审核员工作负载视图
CREATE OR REPLACE VIEW reviewer_workload AS
SELECT 
    rp.user_id,
    rp.name,
    rp.skill_level,
    rp.max_concurrent_tasks,
    COUNT(rt.id) FILTER (WHERE rt.status IN ('assigned', 'in_progress')) as current_tasks,
    COUNT(rt.id) FILTER (WHERE rt.status = 'completed' AND rt.completed_at >= CURRENT_DATE - INTERVAL '30 days') as tasks_last_30_days,
    AVG(rt.actual_time) FILTER (WHERE rt.status = 'completed' AND rt.completed_at >= CURRENT_DATE - INTERVAL '30 days') as avg_time_last_30_days,
    rp.accuracy_rate,
    rp.last_active_at
FROM reviewer_profiles rp
LEFT JOIN review_tasks rt ON rp.user_id = rt.assigned_to
WHERE rp.status = 'active'
GROUP BY rp.user_id, rp.name, rp.skill_level, rp.max_concurrent_tasks, rp.accuracy_rate, rp.last_active_at;

-- 插入默认工作流配置
INSERT INTO workflow_configs (name, content_type, priority, auto_assign, required_reviewers, escalation_threshold, time_limit, rules) VALUES
('文本内容标准审核', 'text', 'medium', true, 1, 0.5, 1800, '{"quality_threshold": 0.7, "risk_threshold": 0.3}'),
('高优先级文本审核', 'text', 'high', true, 2, 0.3, 900, '{"quality_threshold": 0.8, "risk_threshold": 0.2, "double_review": true}'),
('图像内容审核', 'image', 'medium', true, 1, 0.4, 2400, '{"safety_threshold": 0.8, "quality_threshold": 0.6}'),
('医学内容专业审核', 'text', 'high', false, 1, 0.2, 3600, '{"require_medical_expert": true, "quality_threshold": 0.9}')
ON CONFLICT (name) DO NOTHING;

-- 插入示例审核员档案
INSERT INTO reviewer_profiles (user_id, name, email, specialties, skill_level, max_concurrent_tasks) VALUES
('reviewer_001', '张医生', 'zhang.doctor@example.com', ARRAY['医学内容', '健康建议'], 'expert', 3),
('reviewer_002', '李编辑', 'li.editor@example.com', ARRAY['文本质量', '内容合规'], 'senior', 5),
('reviewer_003', '王审核员', 'wang.reviewer@example.com', ARRAY['通用审核'], 'intermediate', 8)
ON CONFLICT (user_id) DO NOTHING;

-- 创建函数：自动分配任务
CREATE OR REPLACE FUNCTION auto_assign_task(task_id UUID)
RETURNS VARCHAR(255) AS $$
DECLARE
    task_record RECORD;
    best_reviewer VARCHAR(255);
    reviewer_record RECORD;
BEGIN
    -- 获取任务信息
    SELECT * INTO task_record FROM review_tasks WHERE id = task_id;
    
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;
    
    -- 查找最适合的审核员
    SELECT rw.user_id INTO best_reviewer
    FROM reviewer_workload rw
    WHERE rw.current_tasks < rw.max_concurrent_tasks
    AND (
        task_record.content_type = ANY(
            SELECT unnest(rp.specialties) 
            FROM reviewer_profiles rp 
            WHERE rp.user_id = rw.user_id
        )
        OR 'general' = ANY(
            SELECT unnest(rp.specialties) 
            FROM reviewer_profiles rp 
            WHERE rp.user_id = rw.user_id
        )
    )
    ORDER BY 
        rw.current_tasks ASC,
        rw.avg_time_last_30_days ASC NULLS LAST,
        rw.accuracy_rate DESC NULLS LAST
    LIMIT 1;
    
    -- 如果找到合适的审核员，分配任务
    IF best_reviewer IS NOT NULL THEN
        UPDATE review_tasks 
        SET assigned_to = best_reviewer, 
            status = 'assigned',
            assigned_at = CURRENT_TIMESTAMP
        WHERE id = task_id;
        
        INSERT INTO task_assignments (task_id, reviewer_id, assignment_type)
        VALUES (task_id, best_reviewer, 'auto');
    END IF;
    
    RETURN best_reviewer;
END;
$$ LANGUAGE plpgsql;

-- 创建函数：计算审核员准确率
CREATE OR REPLACE FUNCTION calculate_reviewer_accuracy(reviewer_user_id VARCHAR(255))
RETURNS DECIMAL(3,2) AS $$
DECLARE
    total_reviews INTEGER;
    accurate_reviews INTEGER;
    accuracy_rate DECIMAL(3,2);
BEGIN
    -- 计算总审核数（最近90天）
    SELECT COUNT(*) INTO total_reviews
    FROM review_results rr
    JOIN review_tasks rt ON rr.task_id = rt.id
    WHERE rr.reviewer_id = reviewer_user_id
    AND rr.created_at >= CURRENT_DATE - INTERVAL '90 days';
    
    IF total_reviews = 0 THEN
        RETURN 0.00;
    END IF;
    
    -- 计算准确审核数（基于置信度和后续反馈）
    SELECT COUNT(*) INTO accurate_reviews
    FROM review_results rr
    JOIN review_tasks rt ON rr.task_id = rt.id
    WHERE rr.reviewer_id = reviewer_user_id
    AND rr.created_at >= CURRENT_DATE - INTERVAL '90 days'
    AND rr.confidence >= 0.7; -- 简化的准确性判断
    
    accuracy_rate := ROUND((accurate_reviews::DECIMAL / total_reviews::DECIMAL), 2);
    
    -- 更新审核员档案
    UPDATE reviewer_profiles 
    SET accuracy_rate = accuracy_rate,
        total_tasks_completed = total_reviews
    WHERE user_id = reviewer_user_id;
    
    RETURN accuracy_rate;
END;
$$ LANGUAGE plpgsql;

-- 创建定时统计函数
CREATE OR REPLACE FUNCTION generate_daily_statistics(stat_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
BEGIN
    -- 删除当天已有的统计数据
    DELETE FROM review_statistics WHERE date = stat_date;
    
    -- 生成整体统计
    INSERT INTO review_statistics (date, total_tasks, completed_tasks, approved_tasks, rejected_tasks, avg_processing_time, avg_confidence)
    SELECT 
        stat_date,
        COUNT(*) as total_tasks,
        COUNT(*) FILTER (WHERE rt.status = 'completed') as completed_tasks,
        COUNT(*) FILTER (WHERE rr.decision = 'approved') as approved_tasks,
        COUNT(*) FILTER (WHERE rr.decision = 'rejected') as rejected_tasks,
        AVG(rt.actual_time) as avg_processing_time,
        AVG(rr.confidence) as avg_confidence
    FROM review_tasks rt
    LEFT JOIN review_results rr ON rt.id = rr.task_id
    WHERE rt.created_at::DATE = stat_date;
    
    -- 生成按审核员的统计
    INSERT INTO review_statistics (date, reviewer_id, total_tasks, completed_tasks, approved_tasks, rejected_tasks, avg_processing_time, avg_confidence)
    SELECT 
        stat_date,
        rt.assigned_to,
        COUNT(*) as total_tasks,
        COUNT(*) FILTER (WHERE rt.status = 'completed') as completed_tasks,
        COUNT(*) FILTER (WHERE rr.decision = 'approved') as approved_tasks,
        COUNT(*) FILTER (WHERE rr.decision = 'rejected') as rejected_tasks,
        AVG(rt.actual_time) as avg_processing_time,
        AVG(rr.confidence) as avg_confidence
    FROM review_tasks rt
    LEFT JOIN review_results rr ON rt.id = rr.task_id
    WHERE rt.created_at::DATE = stat_date
    AND rt.assigned_to IS NOT NULL
    GROUP BY rt.assigned_to;
    
    -- 生成按内容类型的统计
    INSERT INTO review_statistics (date, content_type, total_tasks, completed_tasks, approved_tasks, rejected_tasks, avg_processing_time, avg_confidence)
    SELECT 
        stat_date,
        rt.content_type,
        COUNT(*) as total_tasks,
        COUNT(*) FILTER (WHERE rt.status = 'completed') as completed_tasks,
        COUNT(*) FILTER (WHERE rr.decision = 'approved') as approved_tasks,
        COUNT(*) FILTER (WHERE rr.decision = 'rejected') as rejected_tasks,
        AVG(rt.actual_time) as avg_processing_time,
        AVG(rr.confidence) as avg_confidence
    FROM review_tasks rt
    LEFT JOIN review_results rr ON rt.id = rr.task_id
    WHERE rt.created_at::DATE = stat_date
    GROUP BY rt.content_type;
END;
$$ LANGUAGE plpgsql;

-- 创建清理过期数据的函数
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    cutoff_date TIMESTAMP WITH TIME ZONE;
BEGIN
    cutoff_date := CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;
    
    -- 清理已完成的旧任务（保留结果）
    WITH deleted AS (
        DELETE FROM review_tasks 
        WHERE status = 'completed' 
        AND completed_at < cutoff_date
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    -- 清理旧的统计数据（保留更长时间）
    DELETE FROM review_statistics 
    WHERE date < CURRENT_DATE - (days_to_keep * 2 || ' days')::INTERVAL;
    
    -- 清理旧的任务分配历史
    DELETE FROM task_assignments 
    WHERE assigned_at < cutoff_date;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 授权（如果需要特定用户）
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO human_review_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO human_review_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO human_review_user; 