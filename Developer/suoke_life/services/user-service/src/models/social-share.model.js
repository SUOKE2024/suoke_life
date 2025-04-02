/**
 * 社交分享模型
 */
const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');

// 社交分享表名
const TABLE_NAME = 'social_shares';

// 分享类型
const SHARE_TYPES = {
  CONTENT: 'content',   // 知识内容分享
  PROFILE: 'profile',   // 个人档案分享
  HEALTH_RECORD: 'health_record', // 健康记录分享
  REGIMEN: 'regimen'    // 养生方案分享
};

// 分享平台
const SHARE_PLATFORMS = {
  WECHAT: 'wechat',
  WEIBO: 'weibo',
  QQ: 'qq',
  EMAIL: 'email',
  LINK: 'link',
  INTERNAL: 'internal' // 平台内部分享
};

// 社交分享创建验证模式
const createSchema = Joi.object({
  userId: Joi.string().required().description('分享者用户ID'),
  shareType: Joi.string().valid(...Object.values(SHARE_TYPES)).required().description('分享类型'),
  contentId: Joi.string().required().description('分享内容ID'),
  title: Joi.string().max(200).required().description('分享标题'),
  description: Joi.string().max(500).description('分享描述'),
  imageUrl: Joi.string().uri().description('分享图片URL'),
  platform: Joi.string().valid(...Object.values(SHARE_PLATFORMS)).required().description('分享平台'),
  recipientId: Joi.string().description('接收者ID（当为内部分享时）'),
  recipientEmail: Joi.string().email().description('接收者邮箱（当为邮件分享时）'),
  customAttributes: Joi.object().description('自定义属性')
});

// 社交分享更新验证模式
const updateSchema = Joi.object({
  title: Joi.string().max(200).description('分享标题'),
  description: Joi.string().max(500).description('分享描述'),
  imageUrl: Joi.string().uri().description('分享图片URL'),
  customAttributes: Joi.object().description('自定义属性')
});

// 社交分享状态
const SHARE_STATUS = {
  PENDING: 'pending',   // 待处理
  SHARED: 'shared',     // 已分享
  VIEWED: 'viewed',     // 已查看
  INTERACTED: 'interacted', // 已互动
  EXPIRED: 'expired'    // 已过期
};

// 数据库表结构
const tableStructure = `
  CREATE TABLE IF NOT EXISTS ${TABLE_NAME} (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    share_type VARCHAR(20) NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    platform VARCHAR(20) NOT NULL,
    recipient_id VARCHAR(36),
    recipient_email VARCHAR(255),
    custom_attributes JSON,
    share_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    share_url VARCHAR(500),
    view_count INT NOT NULL DEFAULT 0,
    interaction_count INT NOT NULL DEFAULT 0,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_content (user_id, content_id),
    INDEX idx_share_status (share_status),
    INDEX idx_platform (platform),
    INDEX idx_created_at (created_at)
  )
`;

// 社交分享互动表结构
const shareInteractionTableStructure = `
  CREATE TABLE IF NOT EXISTS social_share_interactions (
    id VARCHAR(36) PRIMARY KEY,
    share_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36),
    interaction_type VARCHAR(20) NOT NULL, /* view, like, comment, reshare */
    comment_text TEXT,
    anonymous BOOLEAN DEFAULT FALSE,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (share_id) REFERENCES ${TABLE_NAME}(id) ON DELETE CASCADE,
    INDEX idx_share_id (share_id),
    INDEX idx_user_id (user_id),
    INDEX idx_interaction_type (interaction_type),
    INDEX idx_created_at (created_at)
  )
`;

/**
 * 创建分享记录
 * @param {Object} shareData - 分享数据
 * @returns {Object} 创建的分享记录
 */
function createShare(shareData) {
  const id = shareData.id || uuidv4();
  const now = new Date();
  
  return {
    id,
    userId: shareData.userId,
    shareType: shareData.shareType,
    contentId: shareData.contentId,
    title: shareData.title,
    description: shareData.description || '',
    imageUrl: shareData.imageUrl || null,
    platform: shareData.platform,
    recipientId: shareData.recipientId || null,
    recipientEmail: shareData.recipientEmail || null,
    customAttributes: shareData.customAttributes || null,
    shareStatus: shareData.shareStatus || SHARE_STATUS.PENDING,
    shareUrl: shareData.shareUrl || null,
    viewCount: shareData.viewCount || 0,
    interactionCount: shareData.interactionCount || 0,
    expiresAt: shareData.expiresAt || null,
    createdAt: shareData.createdAt || now,
    updatedAt: shareData.updatedAt || now
  };
}

module.exports = {
  TABLE_NAME,
  SHARE_TYPES,
  SHARE_PLATFORMS,
  SHARE_STATUS,
  createSchema,
  updateSchema,
  tableStructure,
  shareInteractionTableStructure,
  createShare
};