/**
 * 知识偏好存储库
 */
const { v4: uuidv4 } = require('uuid');
const { pool } = require('../utils/db');
const { logger } = require('@suoke/shared').utils;
const { BusinessError } = require('@suoke/shared').utils;

class KnowledgePreferenceRepository {
  /**
   * 创建用户知识偏好
   * @param {Object} data 知识偏好数据
   * @returns {Promise<Object>} 创建的知识偏好
   */
  async create(data) {
    try {
      const id = uuidv4();
      const now = new Date();
      
      const { userId, interestedDomains, preferredContentTypes, contentLevel } = data;
      
      const query = `
        INSERT INTO user_knowledge_preferences (
          id, user_id, interested_domains, preferred_content_types, content_level, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `;
      
      await pool.query(query, [
        id,
        userId,
        JSON.stringify(interestedDomains || []),
        JSON.stringify(preferredContentTypes || []),
        contentLevel || '中级',
        now,
        now
      ]);
      
      return {
        id,
        userId,
        interestedDomains,
        preferredContentTypes,
        contentLevel,
        createdAt: now,
        updatedAt: now
      };
    } catch (error) {
      logger.error(`创建用户知识偏好失败: ${error.message}`, { error });
      throw new BusinessError('创建用户知识偏好失败', 500);
    }
  }
  
  /**
   * 根据用户ID获取知识偏好
   * @param {string} userId 用户ID
   * @returns {Promise<Object|null>} 知识偏好或null
   */
  async findByUserId(userId) {
    try {
      const query = `
        SELECT *
        FROM user_knowledge_preferences
        WHERE user_id = ?
      `;
      
      const [rows] = await pool.query(query, [userId]);
      
      if (rows.length === 0) {
        return null;
      }
      
      const preference = rows[0];
      
      return {
        id: preference.id,
        userId: preference.user_id,
        interestedDomains: JSON.parse(preference.interested_domains || '[]'),
        preferredContentTypes: JSON.parse(preference.preferred_content_types || '[]'),
        contentLevel: preference.content_level,
        createdAt: preference.created_at,
        updatedAt: preference.updated_at
      };
    } catch (error) {
      logger.error(`根据用户ID获取知识偏好失败: ${error.message}`, { userId, error });
      throw new BusinessError('获取用户知识偏好失败', 500);
    }
  }
  
  /**
   * 更新用户知识偏好
   * @param {string} id 知识偏好ID
   * @param {Object} data 更新数据
   * @returns {Promise<Object>} 更新后的知识偏好
   */
  async update(id, data) {
    try {
      const now = new Date();
      
      const { interestedDomains, preferredContentTypes, contentLevel } = data;
      
      const query = `
        UPDATE user_knowledge_preferences
        SET 
          interested_domains = ?,
          preferred_content_types = ?,
          content_level = ?,
          updated_at = ?
        WHERE id = ?
      `;
      
      await pool.query(query, [
        JSON.stringify(interestedDomains || []),
        JSON.stringify(preferredContentTypes || []),
        contentLevel || '中级',
        now,
        id
      ]);
      
      // 获取更新后的知识偏好
      const [rows] = await pool.query('SELECT * FROM user_knowledge_preferences WHERE id = ?', [id]);
      
      if (rows.length === 0) {
        throw new BusinessError('知识偏好不存在', 404);
      }
      
      const preference = rows[0];
      
      return {
        id: preference.id,
        userId: preference.user_id,
        interestedDomains: JSON.parse(preference.interested_domains || '[]'),
        preferredContentTypes: JSON.parse(preference.preferred_content_types || '[]'),
        contentLevel: preference.content_level,
        createdAt: preference.created_at,
        updatedAt: preference.updated_at
      };
    } catch (error) {
      logger.error(`更新用户知识偏好失败: ${error.message}`, { id, error });
      throw new BusinessError('更新用户知识偏好失败', 500);
    }
  }
  
  /**
   * 记录用户内容访问历史
   * @param {string} userId 用户ID
   * @param {Object} viewData 访问数据
   * @returns {Promise<Object>} 创建的访问记录
   */
  async recordContentView(userId, viewData) {
    try {
      const id = uuidv4();
      const now = new Date();
      
      const { contentId, contentType, domain, title, viewedAt } = viewData;
      
      const query = `
        INSERT INTO user_content_view_history (
          id, user_id, content_id, content_type, domain, title, viewed_at, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `;
      
      await pool.query(query, [
        id,
        userId,
        contentId,
        contentType,
        domain || null,
        title || null,
        viewedAt || now,
        now
      ]);
      
      return {
        id,
        userId,
        contentId,
        contentType,
        domain,
        title,
        viewedAt: viewedAt || now,
        createdAt: now
      };
    } catch (error) {
      logger.error(`记录用户内容访问历史失败: ${error.message}`, { userId, viewData, error });
      throw new BusinessError('记录用户内容访问历史失败', 500);
    }
  }
  
  /**
   * 获取用户访问历史
   * @param {string} userId 用户ID
   * @param {Object} options 查询选项
   * @returns {Promise<Array>} 访问历史列表
   */
  async getUserViewHistory(userId, options = {}) {
    try {
      const { limit = 10, page = 1, domain } = options;
      const offset = (page - 1) * limit;
      
      let query = `
        SELECT *
        FROM user_content_view_history
        WHERE user_id = ?
      `;
      
      const params = [userId];
      
      if (domain) {
        query += ' AND domain = ?';
        params.push(domain);
      }
      
      query += `
        ORDER BY viewed_at DESC
        LIMIT ? OFFSET ?
      `;
      
      params.push(limit, offset);
      
      const [rows] = await pool.query(query, params);
      
      return rows.map(row => ({
        id: row.id,
        userId: row.user_id,
        contentId: row.content_id,
        contentType: row.content_type,
        domain: row.domain,
        title: row.title,
        viewedAt: row.viewed_at,
        createdAt: row.created_at
      }));
    } catch (error) {
      logger.error(`获取用户访问历史失败: ${error.message}`, { userId, options, error });
      throw new BusinessError('获取用户访问历史失败', 500);
    }
  }
  
  /**
   * 添加内容到用户收藏
   * @param {string} userId 用户ID
   * @param {Object} favoriteData 收藏数据
   * @returns {Promise<Object>} 创建的收藏记录
   */
  async addToFavorites(userId, favoriteData) {
    try {
      const id = uuidv4();
      const now = new Date();
      
      const { contentId, contentType, domain, title, addedAt } = favoriteData;
      
      const query = `
        INSERT INTO user_content_favorites (
          id, user_id, content_id, content_type, domain, title, added_at, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `;
      
      await pool.query(query, [
        id,
        userId,
        contentId,
        contentType,
        domain || null,
        title || null,
        addedAt || now,
        now
      ]);
      
      return {
        id,
        userId,
        contentId,
        contentType,
        domain,
        title,
        addedAt: addedAt || now,
        createdAt: now
      };
    } catch (error) {
      logger.error(`添加内容到用户收藏失败: ${error.message}`, { userId, favoriteData, error });
      throw new BusinessError('添加内容到用户收藏失败', 500);
    }
  }
  
  /**
   * 从用户收藏中移除内容
   * @param {string} userId 用户ID
   * @param {string} contentId 内容ID
   * @returns {Promise<boolean>} 是否成功移除
   */
  async removeFromFavorites(userId, contentId) {
    try {
      const query = `
        DELETE FROM user_content_favorites
        WHERE user_id = ? AND content_id = ?
      `;
      
      const [result] = await pool.query(query, [userId, contentId]);
      
      return result.affectedRows > 0;
    } catch (error) {
      logger.error(`从用户收藏中移除内容失败: ${error.message}`, { userId, contentId, error });
      throw new BusinessError('从用户收藏中移除内容失败', 500);
    }
  }
  
  /**
   * 检查内容是否已被用户收藏
   * @param {string} userId 用户ID
   * @param {string} contentId 内容ID
   * @returns {Promise<Object|null>} 收藏记录或null
   */
  async checkFavoriteExists(userId, contentId) {
    try {
      const query = `
        SELECT *
        FROM user_content_favorites
        WHERE user_id = ? AND content_id = ?
      `;
      
      const [rows] = await pool.query(query, [userId, contentId]);
      
      if (rows.length === 0) {
        return null;
      }
      
      const favorite = rows[0];
      
      return {
        id: favorite.id,
        userId: favorite.user_id,
        contentId: favorite.content_id,
        contentType: favorite.content_type,
        domain: favorite.domain,
        title: favorite.title,
        addedAt: favorite.added_at,
        createdAt: favorite.created_at
      };
    } catch (error) {
      logger.error(`检查内容是否已被用户收藏失败: ${error.message}`, { userId, contentId, error });
      throw new BusinessError('检查内容收藏状态失败', 500);
    }
  }
  
  /**
   * 获取用户收藏列表
   * @param {string} userId 用户ID
   * @param {Object} options 查询选项
   * @returns {Promise<Array>} 收藏列表
   */
  async getUserFavorites(userId, options = {}) {
    try {
      const { limit = 10, page = 1, domain } = options;
      const offset = (page - 1) * limit;
      
      let query = `
        SELECT *
        FROM user_content_favorites
        WHERE user_id = ?
      `;
      
      const params = [userId];
      
      if (domain) {
        query += ' AND domain = ?';
        params.push(domain);
      }
      
      query += `
        ORDER BY added_at DESC
        LIMIT ? OFFSET ?
      `;
      
      params.push(limit, offset);
      
      const [rows] = await pool.query(query, params);
      
      return rows.map(row => ({
        id: row.id,
        userId: row.user_id,
        contentId: row.content_id,
        contentType: row.content_type,
        domain: row.domain,
        title: row.title,
        addedAt: row.added_at,
        createdAt: row.created_at
      }));
    } catch (error) {
      logger.error(`获取用户收藏列表失败: ${error.message}`, { userId, options, error });
      throw new BusinessError('获取用户收藏列表失败', 500);
    }
  }
}

module.exports = KnowledgePreferenceRepository;