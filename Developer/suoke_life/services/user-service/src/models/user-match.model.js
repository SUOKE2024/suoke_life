/**
 * 用户匹配模型
 * 基于用户兴趣图谱的匹配功能
 */
const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');

// 用户匹配表名
const TABLE_NAME = 'user_matches';

// 匹配类型
const MATCH_TYPES = {
  INTEREST: 'interest',       // 兴趣匹配
  KNOWLEDGE: 'knowledge',     // 知识匹配
  HEALTH_FOCUS: 'health_focus', // 健康关注匹配
  LEARNING_PATH: 'learning_path', // 学习路径匹配
  COMBINED: 'combined'        // 综合匹配
};

// 匹配状态
const MATCH_STATUS = {
  PENDING: 'pending',     // 待处理
  SUGGESTED: 'suggested', // 已推荐
  CONNECTED: 'connected', // 已连接
  REJECTED: 'rejected',   // 已拒绝
  EXPIRED: 'expired'      // 已过期
};

// 用户匹配创建验证模式
const createSchema = Joi.object({
  userId: Joi.string().required().description('用户ID'),
  matchedUserId: Joi.string().required().description('匹配用户ID'),
  matchType: Joi.string().valid(...Object.values(MATCH_TYPES)).required().description('匹配类型'),
  matchScore: Joi.number().min(0).max(100).required().description('匹配分数'),
  matchReason: Joi.string().max(500).description('匹配原因'),
  matchedInterests: Joi.array().items(Joi.string()).description('匹配的兴趣列表'),
  matchedKnowledgeDomains: Joi.array().items(Joi.string()).description('匹配的知识领域'),
  matchStatus: Joi.string().valid(...Object.values(MATCH_STATUS)).description('匹配状态'),
  isHidden: Joi.boolean().description('是否对用户隐藏')
});

// 用户匹配更新验证模式
const updateSchema = Joi.object({
  matchScore: Joi.number().min(0).max(100).description('匹配分数'),
  matchReason: Joi.string().max(500).description('匹配原因'),
  matchedInterests: Joi.array().items(Joi.string()).description('匹配的兴趣列表'),
  matchedKnowledgeDomains: Joi.array().items(Joi.string()).description('匹配的知识领域'),
  matchStatus: Joi.string().valid(...Object.values(MATCH_STATUS)).description('匹配状态'),
  isHidden: Joi.boolean().description('是否对用户隐藏')
});

// 数据库表结构
const tableStructure = `
  CREATE TABLE IF NOT EXISTS ${TABLE_NAME} (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    matched_user_id VARCHAR(36) NOT NULL,
    match_type VARCHAR(20) NOT NULL,
    match_score FLOAT NOT NULL,
    match_reason TEXT,
    matched_interests JSON,
    matched_knowledge_domains JSON,
    match_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    is_hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_match (user_id, matched_user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_matched_user_id (matched_user_id),
    INDEX idx_match_status (match_status),
    INDEX idx_match_score (match_score),
    INDEX idx_created_at (created_at)
  )
`;

// 用户交互表结构
const userConnectionTableStructure = `
  CREATE TABLE IF NOT EXISTS user_connections (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    connected_user_id VARCHAR(36) NOT NULL,
    connection_status VARCHAR(20) NOT NULL, /* pending, accepted, rejected, blocked */
    connection_type VARCHAR(20) NOT NULL, /* friend, mentor, mentee, collaborator, knowledge_sharing */
    initiated_from_match_id VARCHAR(36),
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (initiated_from_match_id) REFERENCES ${TABLE_NAME}(id) ON DELETE SET NULL,
    UNIQUE KEY unique_connection (user_id, connected_user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_connected_user_id (connected_user_id),
    INDEX idx_connection_status (connection_status),
    INDEX idx_created_at (created_at)
  )
`;

// 用户兴趣向量表结构
const userInterestVectorTableStructure = `
  CREATE TABLE IF NOT EXISTS user_interest_vectors (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    vector_type VARCHAR(20) NOT NULL, /* interest, knowledge, health_focus, combined */
    vector_data LONGTEXT NOT NULL, /* JSON serialized vector data */
    vector_metadata JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_vector_type (user_id, vector_type),
    INDEX idx_user_id (user_id),
    INDEX idx_vector_type (vector_type),
    INDEX idx_updated_at (updated_at)
  )
`;

/**
 * 创建用户匹配
 * @param {Object} matchData - 匹配数据
 * @returns {Object} 创建的匹配对象
 */
function createMatch(matchData) {
  const id = matchData.id || uuidv4();
  const now = new Date();
  
  return {
    id,
    userId: matchData.userId,
    matchedUserId: matchData.matchedUserId,
    matchType: matchData.matchType,
    matchScore: matchData.matchScore,
    matchReason: matchData.matchReason || '',
    matchedInterests: matchData.matchedInterests || [],
    matchedKnowledgeDomains: matchData.matchedKnowledgeDomains || [],
    matchStatus: matchData.matchStatus || MATCH_STATUS.PENDING,
    isHidden: matchData.isHidden || false,
    createdAt: matchData.createdAt || now,
    updatedAt: matchData.updatedAt || now
  };
}

module.exports = {
  TABLE_NAME,
  MATCH_TYPES,
  MATCH_STATUS,
  createSchema,
  updateSchema,
  tableStructure,
  userConnectionTableStructure,
  userInterestVectorTableStructure,
  createMatch
};