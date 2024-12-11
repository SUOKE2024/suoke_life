# 数据库设计文档

## 1. 数据库概述

### 1.1 数据库选型
- 主数据库：MySQL 8.0
- 缓存数据库：Redis
- 本地数据库：SQLite

### 1.2 设计原则
- 数据安全性优先
- 性能可扩展
- 数据一致性
- 冗余适度

## 2. 数据库表设计

### 2.1 用户相关表

#### users（用户表）
```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1,
    last_login TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_phone (phone)
);
```

#### user_profiles（用户档案表）
```sql
CREATE TABLE user_profiles (
    user_id CHAR(36) PRIMARY KEY,
    nickname VARCHAR(50),
    avatar_url VARCHAR(255),
    gender TINYINT,
    birthday DATE,
    location VARCHAR(100),
    bio TEXT,
    preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 2.2 数据分析相关表

#### behavior_data（行为数据表）
```sql
CREATE TABLE behavior_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    behavior_type VARCHAR(50) NOT NULL,
    behavior_data JSON NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    quality_score FLOAT,
    INDEX idx_user_time (user_id, timestamp),
    INDEX idx_type (behavior_type),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### user_graphs（用户图谱表）
```sql
CREATE TABLE user_graphs (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    graph_data JSON NOT NULL,
    analysis_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1,
    INDEX idx_user (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 2.3 AI相关表

#### ai_conversations（AI对话记录表）
```sql
CREATE TABLE ai_conversations (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    session_id CHAR(36) NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    context JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50),
    feedback TINYINT,
    INDEX idx_user_session (user_id, session_id),
    INDEX idx_created (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### recommendations（推荐记录表）
```sql
CREATE TABLE recommendations (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    type VARCHAR(50) NOT NULL,
    content JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1,
    feedback JSON,
    INDEX idx_user_type (user_id, type),
    INDEX idx_created (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 2.4 系统相关表

#### system_logs（系统日志表）
```sql
CREATE TABLE system_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    context JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    trace_id VARCHAR(100),
    INDEX idx_level_time (level, created_at),
    INDEX idx_trace (trace_id)
);
```

#### metrics（性能指标表）
```sql
CREATE TABLE metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    labels JSON,
    INDEX idx_name_time (metric_name, timestamp)
);
```

### 2.5 智能助手相关表

#### assistant_profiles（助手配置表）
```sql
CREATE TABLE assistant_profiles (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    type ENUM('生活助理', '知识助理', '商务助理') NOT NULL,
    personality JSON,
### 3.1 版本控制
- 使用数据库迁移工具
- 版本号管理
- 回滚机制

### 3.2 数据备份
- 定时全量备份
- 实时增量备份
- 多地域备份

## 4. 性能优化

### 4.1 索引策略
- 合理使用索引
- 避免过度索引
- 定期维护索引

### 4.2 分区策略
- 按时间分区
- 按用户ID分区
- 热数据分离

## 5. 安全策略

### 5.1 访问控制
- 最小权限原则
- 角色基础访问控制
- SQL注入防护

### 5.2 数据加密
- 敏感数据加密
- 传输加密
- 备份加密 