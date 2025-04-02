-- 创建数据库 (如果不存在)
CREATE DATABASE IF NOT EXISTS soer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE soer_db;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(36) PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE INDEX idx_email (email),
  UNIQUE INDEX idx_username (username)
);

-- 创建儿童信息表
CREATE TABLE IF NOT EXISTS children (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  name VARCHAR(100) NOT NULL,
  gender ENUM('male', 'female', 'other') NOT NULL,
  birth_date DATE NOT NULL,
  height DECIMAL(5,2) NULL,
  weight DECIMAL(5,2) NULL,
  blood_type ENUM('A', 'B', 'AB', 'O', 'unknown') DEFAULT 'unknown',
  constitution_type VARCHAR(50) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id)
);

-- 创建体质评估记录表
CREATE TABLE IF NOT EXISTS constitution_assessments (
  id VARCHAR(36) PRIMARY KEY,
  child_id VARCHAR(36) NOT NULL,
  assessment_date DATE NOT NULL,
  constitution_type VARCHAR(50) NOT NULL,
  score INT NOT NULL,
  symptoms TEXT,
  recommendations TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
  INDEX idx_child_id (child_id),
  INDEX idx_assessment_date (assessment_date)
);

-- 创建生长记录表
CREATE TABLE IF NOT EXISTS growth_records (
  id VARCHAR(36) PRIMARY KEY,
  child_id VARCHAR(36) NOT NULL,
  record_date DATE NOT NULL,
  height DECIMAL(5,2) NOT NULL,
  weight DECIMAL(5,2) NOT NULL,
  head_circumference DECIMAL(5,2) NULL,
  bmi DECIMAL(5,2) GENERATED ALWAYS AS (weight / (height/100 * height/100)) STORED,
  notes TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
  INDEX idx_child_id (child_id),
  INDEX idx_record_date (record_date)
);

-- 创建食谱推荐表
CREATE TABLE IF NOT EXISTS diet_recommendations (
  id VARCHAR(36) PRIMARY KEY,
  child_id VARCHAR(36) NOT NULL,
  constitution_type VARCHAR(50) NOT NULL,
  season ENUM('spring', 'summer', 'autumn', 'winter', 'all') NOT NULL,
  meal_type ENUM('breakfast', 'lunch', 'dinner', 'snack', 'all') NOT NULL,
  food_name VARCHAR(100) NOT NULL,
  benefits TEXT NOT NULL,
  preparation TEXT,
  contraindications TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
  INDEX idx_child_id (child_id),
  INDEX idx_constitution_type (constitution_type),
  INDEX idx_season (season)
);

-- 创建健康知识表
CREATE TABLE IF NOT EXISTS health_knowledge (
  id VARCHAR(36) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  category ENUM('nutrition', 'disease', 'development', 'psychology', 'general') NOT NULL,
  tags VARCHAR(255),
  target_age_min INT,
  target_age_max INT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_category (category),
  INDEX idx_target_age (target_age_min, target_age_max),
  FULLTEXT INDEX ft_content (title, content)
);

-- 创建用户查询历史表
CREATE TABLE IF NOT EXISTS query_history (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  query_text TEXT NOT NULL,
  query_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  category VARCHAR(50),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_query_date (query_date)
);

-- 插入示例数据
INSERT INTO users (id, username, email) VALUES 
('1', 'test_user', 'test@example.com');

INSERT INTO children (id, user_id, name, gender, birth_date) VALUES 
('1', '1', '小明', 'male', '2019-05-10');

INSERT INTO constitution_assessments (id, child_id, assessment_date, constitution_type, score, symptoms, recommendations) VALUES 
('1', '1', '2023-06-15', '脾虚质', 78, '食欲不振，易腹泻', '增加富含蛋白质的食物，避免生冷食物');

INSERT INTO growth_records (id, child_id, record_date, height, weight, head_circumference) VALUES 
('1', '1', '2023-06-15', 110.5, 20.3, 51.2);

INSERT INTO diet_recommendations (id, child_id, constitution_type, season, meal_type, food_name, benefits, preparation) VALUES 
('1', '1', '脾虚质', 'all', 'breakfast', '小米粥', '健脾益胃，补中益气', '用小米煮粥，可加红枣增强功效');

INSERT INTO health_knowledge (id, title, content, category, tags, target_age_min, target_age_max) VALUES 
('1', '幼儿脾胃发育特点', '儿童脾胃功能尚未发育完全，消化能力相对较弱...', 'nutrition', '脾胃,消化,饮食', 1, 6); 