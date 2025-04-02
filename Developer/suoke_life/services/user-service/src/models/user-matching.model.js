/**
 * 用户兴趣匹配模型
 */
const Joi = require('joi');

// 用户兴趣匹配表名
const TABLE_NAME = 'user_interest_matches';

// 匹配状态枚举
const MATCH_STATUS = {
  SUGGESTED: 'suggested',    // 系统推荐
  ACCEPTED: 'accepted',      // 用户接受
  REJECTED: 'rejected',      // 用户拒绝
  PENDING: 'pending'         // 等待响应
};

// 匹配类型枚举
const MATCH_TYPES = {
  INTEREST: 'interest',      // 兴趣爱好匹配
  HEALTH_GOAL: 'health_goal', // 健康目标匹配
  LIFESTYLE: 'lifestyle',    // 生活方式匹配
  LOCATION: 'location',      // 地理位置匹配
  TCM_CONSTITUTION: 'tcm_constitution' // 中医体质匹配
};

// 匹配创建验证模式
const createSchema = Joi.object({
  userId: Joi.string().required().description('用户ID'),
  matchedUserId: Joi.string().required().description('匹配用户ID'),
  matchType: Joi.string().valid(...Object.values(MATCH_TYPES)).required().description('匹配类型'),
  matchScore: Joi.number().min(0).max(100).required().description('匹配分数'),
  matchStatus: Joi.string().valid(...Object.values(MATCH_STATUS)).required().description('匹配状态'),
  matchReason: Joi.string().max(500).required().description('匹配原因'),
  matchData: Joi.object().description('匹配详细数据')
});

// 匹配更新验证模式
const updateSchema = Joi.object({
  matchStatus: Joi.string().valid(...Object.values(MATCH_STATUS)).description('匹配状态'),
  matchScore: Joi.number().min(0).max(100).description('匹配分数'),
  matchReason: Joi.string().max(500).description('匹配原因'),
  matchData: Joi.object().description('匹配详细数据')
});

// 数据库表结构
const tableStructure = `
  CREATE TABLE IF NOT EXISTS ${TABLE_NAME} (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    matched_user_id VARCHAR(36) NOT NULL,
    match_type VARCHAR(20) NOT NULL,
    match_score FLOAT NOT NULL,
    match_status VARCHAR(20) NOT NULL,
    match_reason TEXT NOT NULL,
    match_data JSON,
    interaction_count INT DEFAULT 0,
    last_interaction_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (matched_user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_user_matched_user (user_id, matched_user_id),
    INDEX idx_user_match_type (user_id, match_type),
    INDEX idx_match_score (match_score),
    INDEX idx_match_status (match_status),
    INDEX idx_created_at (created_at)
  )
`;

// 匹配互动表结构
const matchInteractionsTableStructure = `
  CREATE TABLE IF NOT EXISTS user_match_interactions (
    id VARCHAR(36) PRIMARY KEY,
    match_id VARCHAR(36) NOT NULL,
    initiator_id VARCHAR(36) NOT NULL,
    interaction_type ENUM('view', 'message', 'invite', 'accept', 'reject', 'block') NOT NULL,
    message_text TEXT,
    interaction_data JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES ${TABLE_NAME}(id) ON DELETE CASCADE,
    FOREIGN KEY (initiator_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_match_interaction (match_id, interaction_type),
    INDEX idx_initiator (initiator_id),
    INDEX idx_created_at (created_at)
  )
`;

// 用户兴趣向量表
const userInterestVectorsTableStructure = `
  CREATE TABLE IF NOT EXISTS user_interest_vectors (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    interest_vector JSON NOT NULL,
    health_vector JSON,
    lifestyle_vector JSON,
    tcm_vector JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_user_id (user_id)
  )
`;

module.exports = {
  TABLE_NAME,
  MATCH_STATUS,
  MATCH_TYPES,
  createSchema,
  updateSchema,
  tableStructure,
  matchInteractionsTableStructure,
  userInterestVectorsTableStructure
};