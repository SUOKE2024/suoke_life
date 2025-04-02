/**
 * 社交分享存储库
 * 处理社交分享相关数据库操作
 */
const db = require('../utils/db');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');
const socialShareModel = require('../models/social-share.model');

/**
 * 创建分享
 * @param {Object} shareData - 分享数据
 * @returns {Promise<Object>} 创建的分享对象
 */
async function createShare(shareData) {
  try {
    const id = uuidv4();
    const now = new Date();
    
    const share = {
      id,
      user_id: shareData.userId,
      share_type: shareData.shareType,
      content_id: shareData.contentId,
      title: shareData.title,
      description: shareData.description || '',
      image_url: shareData.imageUrl || null,
      platform: shareData.platform,
      recipient_id: shareData.recipientId || null,
      recipient_email: shareData.recipientEmail || null,
      custom_attributes: shareData.customAttributes ? JSON.stringify(shareData.customAttributes) : null,
      share_status: shareData.shareStatus || socialShareModel.SHARE_STATUS.PENDING,
      share_url: shareData.shareUrl || null,
      view_count: 0,
      interaction_count: 0,
      expires_at: shareData.expiresAt || null,
      created_at: now,
      updated_at: now
    };
    
    const query = `
      INSERT INTO ${socialShareModel.TABLE_NAME} (
        id, user_id, share_type, content_id, title, description, image_url, 
        platform, recipient_id, recipient_email, custom_attributes, share_status, 
        share_url, view_count, interaction_count, expires_at, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    
    const values = [
      share.id, share.user_id, share.share_type, share.content_id, share.title, 
      share.description, share.image_url, share.platform, share.recipient_id, 
      share.recipient_email, share.custom_attributes, share.share_status, 
      share.share_url, share.view_count, share.interaction_count, 
      share.expires_at, share.created_at, share.updated_at
    ];
    
    await db.execute(query, values);
    
    return {
      id: share.id,
      userId: share.user_id,
      shareType: share.share_type,
      contentId: share.content_id,
      title: share.title,
      description: share.description,
      imageUrl: share.image_url,
      platform: share.platform,
      recipientId: share.recipient_id,
      recipientEmail: share.recipient_email,
      customAttributes: share.custom_attributes ? JSON.parse(share.custom_attributes) : null,
      shareStatus: share.share_status,
      shareUrl: share.share_url,
      viewCount: share.view_count,
      interactionCount: share.interaction_count,
      expiresAt: share.expires_at,
      createdAt: share.created_at,
      updatedAt: share.updated_at
    };
  } catch (error) {
    logger.error('创建分享失败', error);
    throw new Error('创建分享失败');
  }
}

/**
 * 更新分享
 * @param {string} shareId - 分享ID
 * @param {Object} updateData - 更新数据
 * @returns {Promise<boolean>} 操作结果
 */
async function updateShare(shareId, updateData) {
  try {
    const updates = [];
    const values = [];
    
    // 构建更新字段
    if (updateData.title !== undefined) {
      updates.push('title = ?');
      values.push(updateData.title);
    }
    
    if (updateData.description !== undefined) {
      updates.push('description = ?');
      values.push(updateData.description);
    }
    
    if (updateData.imageUrl !== undefined) {
      updates.push('image_url = ?');
      values.push(updateData.imageUrl);
    }
    
    if (updateData.shareStatus !== undefined) {
      updates.push('share_status = ?');
      values.push(updateData.shareStatus);
    }
    
    if (updateData.shareUrl !== undefined) {
      updates.push('share_url = ?');
      values.push(updateData.shareUrl);
    }
    
    if (updateData.viewCount !== undefined) {
      updates.push('view_count = ?');
      values.push(updateData.viewCount);
    }
    
    if (updateData.interactionCount !== undefined) {
      updates.push('interaction_count = ?');
      values.push(updateData.interactionCount);
    }
    
    if (updateData.expiresAt !== undefined) {
      updates.push('expires_at = ?');
      values.push(updateData.expiresAt);
    }
    
    if (updateData.customAttributes !== undefined) {
      updates.push('custom_attributes = ?');
      values.push(JSON.stringify(updateData.customAttributes));
    }
    
    // 如果没有更新字段，直接返回true
    if (updates.length === 0) {
      return true;
    }
    
    // 添加更新时间
    updates.push('updated_at = ?');
    values.push(new Date());
    
    // 添加分享ID
    values.push(shareId);
    
    const query = `
      UPDATE ${socialShareModel.TABLE_NAME}
      SET ${updates.join(', ')}
      WHERE id = ?
    `;
    
    const result = await db.execute(query, values);
    return result.affectedRows > 0;
  } catch (error) {
    logger.error(`更新分享失败: ${shareId}`, error);
    throw new Error('更新分享失败');
  }
}

/**
 * 获取分享
 * @param {string} shareId - 分享ID
 * @returns {Promise<Object|null>} 分享对象或null
 */
async function getShareById(shareId) {
  try {
    const query = `
      SELECT * FROM ${socialShareModel.TABLE_NAME}
      WHERE id = ?
    `;
    
    const rows = await db.query(query, [shareId]);
    
    if (rows.length === 0) {
      return null;
    }
    
    const share = rows[0];
    
    return {
      id: share.id,
      userId: share.user_id,
      shareType: share.share_type,
      contentId: share.content_id,
      title: share.title,
      description: share.description,
      imageUrl: share.image_url,
      platform: share.platform,
      recipientId: share.recipient_id,
      recipientEmail: share.recipient_email,
      customAttributes: share.custom_attributes ? JSON.parse(share.custom_attributes) : null,
      shareStatus: share.share_status,
      shareUrl: share.share_url,
      viewCount: share.view_count,
      interactionCount: share.interaction_count,
      expiresAt: share.expires_at,
      createdAt: share.created_at,
      updatedAt: share.updated_at
    };
  } catch (error) {
    logger.error(`获取分享失败: ${shareId}`, error);
    throw new Error('获取分享失败');
  }
}

/**
 * 获取用户的分享列表
 * @param {string} userId - 用户ID
 * @param {number} limit - 限制返回数量
 * @param {number} offset - 结果偏移量
 * @param {Object} filters - 过滤条件
 * @returns {Promise<Array>} 分享列表
 */
async function getUserShares(userId, limit = 20, offset = 0, filters = {}) {
  try {
    const conditions = ['user_id = ?'];
    const values = [userId];
    
    if (filters.shareType) {
      conditions.push('share_type = ?');
      values.push(filters.shareType);
    }
    
    if (filters.platform) {
      conditions.push('platform = ?');
      values.push(filters.platform);
    }
    
    if (filters.shareStatus) {
      conditions.push('share_status = ?');
      values.push(filters.shareStatus);
    }
    
    if (filters.contentId) {
      conditions.push('content_id = ?');
      values.push(filters.contentId);
    }
    
    const query = `
      SELECT * FROM ${socialShareModel.TABLE_NAME}
      WHERE ${conditions.join(' AND ')}
      ORDER BY created_at DESC
      LIMIT ? OFFSET ?
    `;
    
    values.push(limit, offset);
    
    const rows = await db.query(query, values);
    
    return rows.map(share => ({
      id: share.id,
      userId: share.user_id,
      shareType: share.share_type,
      contentId: share.content_id,
      title: share.title,
      description: share.description,
      imageUrl: share.image_url,
      platform: share.platform,
      recipientId: share.recipient_id,
      recipientEmail: share.recipient_email,
      customAttributes: share.custom_attributes ? JSON.parse(share.custom_attributes) : null,
      shareStatus: share.share_status,
      shareUrl: share.share_url,
      viewCount: share.view_count,
      interactionCount: share.interaction_count,
      expiresAt: share.expires_at,
      createdAt: share.created_at,
      updatedAt: share.updated_at
    }));
  } catch (error) {
    logger.error(`获取用户分享列表失败: ${userId}`, error);
    throw new Error('获取用户分享列表失败');
  }
}

/**
 * 删除分享
 * @param {string} shareId - 分享ID
 * @param {string} userId - 用户ID（验证操作权限）
 * @returns {Promise<boolean>} 操作结果
 */
async function deleteShare(shareId, userId) {
  try {
    const query = `
      DELETE FROM ${socialShareModel.TABLE_NAME}
      WHERE id = ? AND user_id = ?
    `;
    
    const result = await db.execute(query, [shareId, userId]);
    return result.affectedRows > 0;
  } catch (error) {
    logger.error(`删除分享失败: ${shareId}`, error);
    throw new Error('删除分享失败');
  }
}

/**
 * 记录分享互动
 * @param {Object} interactionData - 互动数据
 * @returns {Promise<Object>} 创建的互动记录
 */
async function recordShareInteraction(interactionData) {
  try {
    const id = uuidv4();
    const now = new Date();
    
    const interaction = {
      id,
      share_id: interactionData.shareId,
      user_id: interactionData.userId || null,
      interaction_type: interactionData.interactionType,
      comment_text: interactionData.commentText || null,
      anonymous: interactionData.anonymous || false,
      ip_address: interactionData.ipAddress || null,
      user_agent: interactionData.userAgent || null,
      created_at: now
    };
    
    const query = `
      INSERT INTO social_share_interactions (
        id, share_id, user_id, interaction_type, comment_text, 
        anonymous, ip_address, user_agent, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    
    const values = [
      interaction.id, interaction.share_id, interaction.user_id, 
      interaction.interaction_type, interaction.comment_text, 
      interaction.anonymous, interaction.ip_address, interaction.user_agent, 
      interaction.created_at
    ];
    
    await db.execute(query, values);
    
    // 更新分享的互动计数
    await updateShareInteractionCount(interactionData.shareId);
    
    // 如果是查看互动，更新查看计数
    if (interactionData.interactionType === 'view') {
      await updateShareViewCount(interactionData.shareId);
    }
    
    return {
      id: interaction.id,
      shareId: interaction.share_id,
      userId: interaction.user_id,
      interactionType: interaction.interaction_type,
      commentText: interaction.comment_text,
      anonymous: interaction.anonymous,
      ipAddress: interaction.ip_address,
      userAgent: interaction.user_agent,
      createdAt: interaction.created_at
    };
  } catch (error) {
    logger.error('记录分享互动失败', error);
    throw new Error('记录分享互动失败');
  }
}

/**
 * 更新分享互动计数
 * @param {string} shareId - 分享ID
 * @returns {Promise<boolean>} 操作结果
 */
async function updateShareInteractionCount(shareId) {
  try {
    const countQuery = `
      SELECT COUNT(*) as count 
      FROM social_share_interactions 
      WHERE share_id = ?
    `;
    
    const countRows = await db.query(countQuery, [shareId]);
    const interactionCount = countRows[0].count;
    
    const updateQuery = `
      UPDATE ${socialShareModel.TABLE_NAME}
      SET interaction_count = ?, updated_at = ?
      WHERE id = ?
    `;
    
    const result = await db.execute(updateQuery, [interactionCount, new Date(), shareId]);
    return result.affectedRows > 0;
  } catch (error) {
    logger.error(`更新分享互动计数失败: ${shareId}`, error);
    throw new Error('更新分享互动计数失败');
  }
}

/**
 * 更新分享查看计数
 * @param {string} shareId - 分享ID
 * @returns {Promise<boolean>} 操作结果
 */
async function updateShareViewCount(shareId) {
  try {
    const countQuery = `
      SELECT COUNT(*) as count 
      FROM social_share_interactions 
      WHERE share_id = ? AND interaction_type = 'view'
    `;
    
    const countRows = await db.query(countQuery, [shareId]);
    const viewCount = countRows[0].count;
    
    const updateQuery = `
      UPDATE ${socialShareModel.TABLE_NAME}
      SET view_count = ?, updated_at = ?
      WHERE id = ?
    `;
    
    const result = await db.execute(updateQuery, [viewCount, new Date(), shareId]);
    return result.affectedRows > 0;
  } catch (error) {
    logger.error(`更新分享查看计数失败: ${shareId}`, error);
    throw new Error('更新分享查看计数失败');
  }
}

/**
 * 获取分享互动列表
 * @param {string} shareId - 分享ID
 * @param {number} limit - 限制返回数量
 * @param {number} offset - 结果偏移量
 * @param {string} interactionType - 互动类型过滤
 * @returns {Promise<Array>} 互动列表
 */
async function getShareInteractions(shareId, limit = 20, offset = 0, interactionType = null) {
  try {
    const conditions = ['share_id = ?'];
    const values = [shareId];
    
    if (interactionType) {
      conditions.push('interaction_type = ?');
      values.push(interactionType);
    }
    
    const query = `
      SELECT * FROM social_share_interactions
      WHERE ${conditions.join(' AND ')}
      ORDER BY created_at DESC
      LIMIT ? OFFSET ?
    `;
    
    values.push(limit, offset);
    
    const rows = await db.query(query, values);
    
    return rows.map(interaction => ({
      id: interaction.id,
      shareId: interaction.share_id,
      userId: interaction.user_id,
      interactionType: interaction.interaction_type,
      commentText: interaction.comment_text,
      anonymous: interaction.anonymous === 1,
      ipAddress: interaction.ip_address,
      userAgent: interaction.user_agent,
      createdAt: interaction.created_at
    }));
  } catch (error) {
    logger.error(`获取分享互动列表失败: ${shareId}`, error);
    throw new Error('获取分享互动列表失败');
  }
}

module.exports = {
  createShare,
  updateShare,
  getShareById,
  getUserShares,
  deleteShare,
  recordShareInteraction,
  getShareInteractions
};