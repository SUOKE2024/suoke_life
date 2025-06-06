-- 索克生活数据库初始化脚本
-- Suoke Life Database Initialization Script

-- 创建主数据库
CREATE DATABASE IF NOT EXISTS suoke_life
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '索克生活主数据库';

-- 创建智能体服务数据库
CREATE DATABASE IF NOT EXISTS suoke_xiaoai
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '小艾智能体数据库';

CREATE DATABASE IF NOT EXISTS suoke_xiaoke
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '小克智能体数据库';

CREATE DATABASE IF NOT EXISTS suoke_laoke
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '老克智能体数据库';

CREATE DATABASE IF NOT EXISTS suoke_soer
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '索儿智能体数据库';

-- 创建诊断服务数据库
CREATE DATABASE IF NOT EXISTS suoke_diagnosis_look
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '望诊服务数据库';

CREATE DATABASE IF NOT EXISTS suoke_diagnosis_listen
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '闻诊服务数据库';

CREATE DATABASE IF NOT EXISTS suoke_diagnosis_inquiry
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '问诊服务数据库';

CREATE DATABASE IF NOT EXISTS suoke_diagnosis_palpation
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '切诊服务数据库';

CREATE DATABASE IF NOT EXISTS suoke_diagnosis_calculation
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '算诊服务数据库';

-- 创建核心服务数据库
CREATE DATABASE IF NOT EXISTS suoke_users
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '用户服务数据库';

CREATE DATABASE IF NOT EXISTS suoke_health_data
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '健康数据服务数据库';

CREATE DATABASE IF NOT EXISTS suoke_blockchain
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '区块链服务数据库';

CREATE DATABASE IF NOT EXISTS suoke_auth
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '认证服务数据库';

CREATE DATABASE IF NOT EXISTS suoke_messaging
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '消息总线数据库';

-- 创建用户和权限
CREATE USER IF NOT EXISTS 'suoke_admin'@'%' IDENTIFIED BY 'suoke_admin_password';
CREATE USER IF NOT EXISTS 'suoke_app'@'%' IDENTIFIED BY 'suoke_app_password';
CREATE USER IF NOT EXISTS 'suoke_readonly'@'%' IDENTIFIED BY 'suoke_readonly_password';

-- 授予权限
-- 管理员权限
GRANT ALL PRIVILEGES ON suoke_life.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_xiaoai.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_xiaoke.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_laoke.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_soer.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_diagnosis_look.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_diagnosis_listen.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_diagnosis_inquiry.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_diagnosis_palpation.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_diagnosis_calculation.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_users.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_health_data.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_blockchain.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_auth.* TO 'suoke_admin'@'%';
GRANT ALL PRIVILEGES ON suoke_messaging.* TO 'suoke_admin'@'%';

-- 应用权限
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_life.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_xiaoai.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_xiaoke.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_laoke.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_soer.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_diagnosis_look.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_diagnosis_listen.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_diagnosis_inquiry.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_diagnosis_palpation.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_diagnosis_calculation.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_users.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_health_data.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_blockchain.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_auth.* TO 'suoke_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON suoke_messaging.* TO 'suoke_app'@'%';

-- 只读权限
GRANT SELECT ON suoke_life.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_xiaoai.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_xiaoke.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_laoke.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_soer.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_diagnosis_look.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_diagnosis_listen.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_diagnosis_inquiry.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_diagnosis_palpation.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_diagnosis_calculation.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_users.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_health_data.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_blockchain.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_auth.* TO 'suoke_readonly'@'%';
GRANT SELECT ON suoke_messaging.* TO 'suoke_readonly'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 创建基础表结构
USE suoke_life;

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key)
) COMMENT '系统配置表';

-- 服务注册表
CREATE TABLE IF NOT EXISTS service_registry (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    service_version VARCHAR(50) NOT NULL,
    service_url VARCHAR(500) NOT NULL,
    health_check_url VARCHAR(500),
    status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_service_name (service_name),
    INDEX idx_status (status)
) COMMENT '服务注册表';

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    service_name VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(255),
    resource_id VARCHAR(255),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_service_name (service_name),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) COMMENT '审计日志表';

-- 插入初始配置数据
INSERT INTO system_config (config_key, config_value, description) VALUES
('system.version', '1.0.0', '系统版本'),
('system.name', '索克生活', '系统名称'),
('system.description', 'AI中医健康管理平台', '系统描述'),
('database.version', '1.0.0', '数据库版本'),
('migration.auto_migrate', 'false', '是否自动迁移'),
('backup.enabled', 'true', '是否启用备份'),
('backup.interval', '86400', '备份间隔(秒)'),
('backup.retention', '7', '备份保留天数')
ON DUPLICATE KEY UPDATE 
    config_value = VALUES(config_value),
    updated_at = CURRENT_TIMESTAMP; 