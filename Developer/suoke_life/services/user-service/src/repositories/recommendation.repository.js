/**
 * 推荐功能数据库操作
 */
const db = require('../utils/db');
const logger = require('../utils/logger');
const uuid = require('uuid');

/**
 * 记录推荐反馈
 * @param {string} userId - 用户ID
 * @param {string} contentId - 内容ID
 * @param {string} feedbackType - 反馈类型 (clicked, liked, disliked, ignored)
 * @returns {Promise<boolean>} 操作结果
 */
async function recordRecommendationFeedback(userId, contentId, feedbackType) {
  try {
    const id = uuid.v4();
    const now = new Date();
    
    const query = `
      INSERT INTO user_recommendation_feedback (
        id, user_id, content_id, feedback_type, feedback_at, created_at
      ) VALUES (?, ?, ?, ?, ?, ?)
    `;
    
    const values = [id, userId, contentId, feedbackType, now, now];
    
    await db.execute(query, values);
    return true;
  } catch (error) {
    logger.error('记录推荐反馈失败', error);
    throw new Error('记录推荐反馈失败');
  }
}

/**
 * 获取用户推荐反馈历史
 * @param {string} userId - 用户ID
 * @param {number} limit - 限制结果数量
 * @param {number} offset - 结果偏移量
 * @returns {Promise<Array>} 反馈历史记录
 */
async function getUserRecommendationFeedback(userId, limit = 20, offset = 0) {
  try {
    const query = `
      SELECT 
        id, content_id, feedback_type, feedback_at, created_at
      FROM 
        user_recommendation_feedback
      WHERE 
        user_id = ?
      ORDER BY 
        feedback_at DESC
      LIMIT ? OFFSET ?
    `;
    
    const values = [userId, limit, offset];
    const rows = await db.query(query, values);
    
    return rows.map(row => ({
      id: row.id,
      contentId: row.content_id,
      feedbackType: row.feedback_type,
      feedbackAt: row.feedback_at,
      createdAt: row.created_at
    }));
  } catch (error) {
    logger.error('获取用户推荐反馈历史失败', error);
    throw new Error('获取用户推荐反馈历史失败');
  }
}

/**
 * 获取用户对特定内容的反馈
 * @param {string} userId - 用户ID
 * @param {string} contentId - 内容ID
 * @returns {Promise<Object|null>} 反馈信息或null
 */
async function getUserContentFeedback(userId, contentId) {
  try {
    const query = `
      SELECT 
        id, feedback_type, feedback_at
      FROM 
        user_recommendation_feedback
      WHERE 
        user_id = ? AND content_id = ?
      ORDER BY 
        feedback_at DESC
      LIMIT 1
    `;
    
    const values = [userId, contentId];
    const rows = await db.query(query, values);
    
    if (rows.length === 0) {
      return null;
    }
    
    return {
      id: rows[0].id,
      feedbackType: rows[0].feedback_type,
      feedbackAt: rows[0].feedback_at
    };
  } catch (error) {
    logger.error('获取用户内容反馈失败', error);
    throw new Error('获取用户内容反馈失败');
  }
}

/**
 * 删除用户推荐反馈
 * @param {string} userId - 用户ID
 * @param {string} feedbackId - 反馈ID
 * @returns {Promise<boolean>} 操作结果
 */
async function deleteRecommendationFeedback(userId, feedbackId) {
  try {
    const query = `
      DELETE FROM 
        user_recommendation_feedback
      WHERE 
        id = ? AND user_id = ?
    `;
    
    const values = [feedbackId, userId];
    const result = await db.execute(query, values);
    
    return result.affectedRows > 0;
  } catch (error) {
    logger.error('删除推荐反馈失败', error);
    throw new Error('删除推荐反馈失败');
  }
}

module.exports = {
  recordRecommendationFeedback,
  getUserRecommendationFeedback,
  getUserContentFeedback,
  deleteRecommendationFeedback
};