-- 确保使用正确的数据库
USE suoke_users;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id CHAR(36) PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('user', 'admin', 'moderator') NOT NULL DEFAULT 'user',
  status ENUM('active', 'inactive', 'suspended') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 用户档案表
CREATE TABLE IF NOT EXISTS user_profiles (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  full_name VARCHAR(100),
  avatar VARCHAR(255),
  phone VARCHAR(20),
  address TEXT,
  bio TEXT,
  date_of_birth DATE,
  gender ENUM('male', 'female', 'other', 'prefer_not_to_say'),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 用户知识偏好表
CREATE TABLE IF NOT EXISTS user_knowledge_preferences (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  domain_preferences JSON,
  content_type_preferences JSON,
  difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'intermediate',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 用户内容查看历史表
CREATE TABLE IF NOT EXISTS user_content_view_history (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  content_id VARCHAR(100) NOT NULL,
  content_type VARCHAR(50) NOT NULL,
  view_duration INT,
  viewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_content (user_id, content_id)
);

-- 用户收藏内容表
CREATE TABLE IF NOT EXISTS user_content_favorites (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  content_id VARCHAR(100) NOT NULL,
  content_type VARCHAR(50) NOT NULL,
  favorited_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY uk_user_content (user_id, content_id)
);

-- 用户知识图谱交互表
CREATE TABLE IF NOT EXISTS user_knowledge_graph_interactions (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  node_id VARCHAR(100) NOT NULL,
  interaction_type ENUM('viewed', 'expanded', 'queried', 'saved'),
  interaction_metadata JSON,
  interaction_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_node (user_id, node_id)
);

-- 社交分享表
CREATE TABLE IF NOT EXISTS social_shares (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  content_id VARCHAR(100),
  content_type VARCHAR(50) NOT NULL,
  share_type ENUM('wechat', 'weibo', 'email', 'link') NOT NULL,
  share_status ENUM('active', 'expired', 'deleted') NOT NULL DEFAULT 'active',
  share_link VARCHAR(255) NOT NULL,
  share_title VARCHAR(200),
  share_description TEXT,
  share_image VARCHAR(255),
  expiry_date TIMESTAMP NULL,
  view_count INT UNSIGNED NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_content (content_id, content_type)
);

-- 社交分享互动表
CREATE TABLE IF NOT EXISTS social_share_interactions (
  id CHAR(36) PRIMARY KEY,
  share_id CHAR(36) NOT NULL,
  interaction_type ENUM('view', 'like', 'comment', 'share') NOT NULL,
  interaction_source VARCHAR(100),
  interaction_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  interaction_ip VARCHAR(45),
  interaction_user_agent TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (share_id) REFERENCES social_shares(id) ON DELETE CASCADE,
  INDEX idx_share_time (share_id, interaction_time)
);

-- 用户兴趣向量表
CREATE TABLE IF NOT EXISTS user_interest_vectors (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  vector_data BLOB NOT NULL,
  vector_dimension INT UNSIGNED NOT NULL,
  vector_version VARCHAR(20) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY uk_user_version (user_id, vector_version)
);

-- 用户匹配表
CREATE TABLE IF NOT EXISTS user_matches (
  id CHAR(36) PRIMARY KEY,
  user_id_a CHAR(36) NOT NULL,
  user_id_b CHAR(36) NOT NULL,
  match_score DECIMAL(5,4) NOT NULL,
  match_type ENUM('interest', 'knowledge', 'activity', 'composite') NOT NULL,
  match_reason JSON,
  match_status ENUM('pending', 'accepted', 'rejected', 'ignored') NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id_a) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id_b) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY uk_user_pair (user_id_a, user_id_b),
  CHECK (user_id_a < user_id_b)
);

-- 用户连接表
CREATE TABLE IF NOT EXISTS user_connections (
  id CHAR(36) PRIMARY KEY,
  requester_id CHAR(36) NOT NULL,
  recipient_id CHAR(36) NOT NULL,
  connection_status ENUM('pending', 'accepted', 'rejected', 'blocked') NOT NULL DEFAULT 'pending',
  match_id CHAR(36),
  message TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (match_id) REFERENCES user_matches(id) ON DELETE SET NULL,
  UNIQUE KEY uk_user_pair (requester_id, recipient_id)
);

-- 插入测试数据: 管理员用户
INSERT INTO users (id, username, email, password_hash, role, status)
VALUES (
  '11111111-1111-1111-1111-111111111111',
  'admin',
  'admin@suoke.life',
  '$2b$10$D8xMOyDpzxJ1Uq.8CoJa9.rCyl7iQMVFdT3ovbi5zKMdOBGGfZ8Ri', -- 密码: admin123
  'admin',
  'active'
);

-- 插入测试数据: 普通用户
INSERT INTO users (id, username, email, password_hash, role, status)
VALUES (
  '22222222-2222-2222-2222-222222222222',
  'user1',
  'user1@example.com',
  '$2b$10$D8xMOyDpzxJ1Uq.8CoJa9.rCyl7iQMVFdT3ovbi5zKMdOBGGfZ8Ri', -- 密码: admin123
  'user',
  'active'
);

-- 插入普通用户档案
INSERT INTO user_profiles (id, user_id, full_name, avatar, phone, address, bio, date_of_birth, gender)
VALUES (
  '33333333-3333-3333-3333-333333333333',
  '22222222-2222-2222-2222-222222222222',
  '张三',
  '/avatars/default.png',
  '13800138000',
  '北京市海淀区中关村',
  '我是一名健康生活爱好者',
  '1985-05-15',
  'male'
);

-- 插入用户知识偏好
INSERT INTO user_knowledge_preferences (id, user_id, domain_preferences, content_type_preferences, difficulty_level)
VALUES (
  '44444444-4444-4444-4444-444444444444',
  '22222222-2222-2222-2222-222222222222',
  '{"tcm": 0.9, "nutrition": 0.8, "wellness": 0.7}',
  '{"article": 0.8, "video": 0.6, "infographic": 0.9}',
  'intermediate'
); 