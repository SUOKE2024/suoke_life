/**
 * 知识偏好模型
 */
const Joi = require('joi');

// 知识偏好表名
const TABLE_NAME = 'user_knowledge_preferences';

// 知识偏好创建验证模式
const createSchema = Joi.object({
  userId: Joi.string().required().description('用户ID'),
  interestedDomains: Joi.array().items(Joi.string()).description('感兴趣的知识领域'),
  preferredContentTypes: Joi.array().items(Joi.string()).description('偏好的内容类型'),
  contentLevel: Joi.string().valid('初级', '中级', '高级').description('内容级别')
});

// 知识偏好更新验证模式
const updateSchema = Joi.object({
  interestedDomains: Joi.array().items(Joi.string()).description('感兴趣的知识领域'),
  preferredContentTypes: Joi.array().items(Joi.string()).description('偏好的内容类型'),
  contentLevel: Joi.string().valid('初级', '中级', '高级').description('内容级别')
});

// 访问历史验证模式
const viewHistorySchema = Joi.object({
  userId: Joi.string().required().description('用户ID'),
  contentId: Joi.string().required().description('内容ID'),
  contentType: Joi.string().required().description('内容类型'),
  domain: Joi.string().description('知识领域'),
  title: Joi.string().description('内容标题'),
  viewedAt: Joi.date().required().description('访问时间')
});

// 收藏验证模式
const favoriteSchema = Joi.object({
  userId: Joi.string().required().description('用户ID'),
  contentId: Joi.string().required().description('内容ID'),
  contentType: Joi.string().required().description('内容类型'),
  domain: Joi.string().description('知识领域'),
  title: Joi.string().description('内容标题'),
  addedAt: Joi.date().required().description('添加时间')
});

// 数据库表结构
const tableStructure = `
  CREATE TABLE IF NOT EXISTS user_knowledge_preferences (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    interested_domains JSON,
    preferred_content_types JSON,
    content_level VARCHAR(10),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  )
`;

// 访问历史表结构
const viewHistoryTableStructure = `
  CREATE TABLE IF NOT EXISTS user_content_view_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    domain VARCHAR(100),
    title VARCHAR(255),
    viewed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_content (user_id, content_id),
    INDEX idx_viewed_at (viewed_at)
  )
`;

// 收藏表结构
const favoritesTableStructure = `
  CREATE TABLE IF NOT EXISTS user_content_favorites (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    domain VARCHAR(100),
    title VARCHAR(255),
    added_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_user_content (user_id, content_id),
    INDEX idx_added_at (added_at)
  )
`;

// 知识图谱交互历史表结构
const knowledgeGraphInteractionTableStructure = `
  CREATE TABLE IF NOT EXISTS user_knowledge_graph_interactions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    query_text TEXT,
    node_ids JSON,
    relation_ids JSON,
    interaction_type VARCHAR(50) NOT NULL,
    interaction_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_interaction (user_id, interaction_type),
    INDEX idx_interaction_at (interaction_at)
  )
`;

// 推荐反馈表结构
const recommendationFeedbackTableStructure = `
  CREATE TABLE IF NOT EXISTS user_recommendation_feedback (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    feedback_type VARCHAR(20) NOT NULL,
    feedback_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_content (user_id, content_id),
    INDEX idx_feedback_at (feedback_at)
  )
`;

module.exports = {
  TABLE_NAME,
  createSchema,
  updateSchema,
  viewHistorySchema,
  favoriteSchema,
  tableStructure,
  viewHistoryTableStructure,
  favoritesTableStructure,
  knowledgeGraphInteractionTableStructure,
  recommendationFeedbackTableStructure
};