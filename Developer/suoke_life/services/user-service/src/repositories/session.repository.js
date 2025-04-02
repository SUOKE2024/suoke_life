/**
 * 会话仓库
 */
const { db } = require('../utils/db');
const { sessionModel } = require('../models');
const { logger } = require('@suoke/shared').utils;

class SessionRepository {
  /**
   * 创建会话
   */
  async create(sessionData) {
    try {
      const sessionId = sessionModel.generateSessionId();
      const session = {
        id: sessionId,
        ...sessionData,
        created_at: new Date()
      };

      const query = `
        INSERT INTO ${sessionModel.TABLE_NAME} 
        (id, user_id, device_info, ip_address, user_agent, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `;

      await db.query(query, [
        session.id,
        session.user_id,
        JSON.stringify(session.device_info),
        session.ip_address,
        session.user_agent,
        session.expires_at,
        session.created_at
      ]);

      return session;
    } catch (error) {
      logger.error('创建会话失败', { error: error.message, sessionData });
      throw error;
    }
  }

  /**
   * 更新会话
   */
  async update(sessionId, updateData) {
    try {
      const query = `
        UPDATE ${sessionModel.TABLE_NAME}
        SET last_activity = CURRENT_TIMESTAMP,
            device_info = ?,
            ip_address = ?,
            user_agent = ?,
            expires_at = ?
        WHERE id = ?
      `;

      await db.query(query, [
        JSON.stringify(updateData.device_info),
        updateData.ip_address,
        updateData.user_agent,
        updateData.expires_at,
        sessionId
      ]);

      return true;
    } catch (error) {
      logger.error('更新会话失败', { error: error.message, sessionId, updateData });
      throw error;
    }
  }

  /**
   * 获取会话
   */
  async findById(sessionId) {
    try {
      const query = `
        SELECT * FROM ${sessionModel.TABLE_NAME}
        WHERE id = ? AND expires_at > CURRENT_TIMESTAMP
      `;

      const [session] = await db.query(query, [sessionId]);
      
      if (session) {
        session.device_info = JSON.parse(session.device_info);
      }

      return session;
    } catch (error) {
      logger.error('获取会话失败', { error: error.message, sessionId });
      throw error;
    }
  }

  /**
   * 获取用户的所有会话
   */
  async findByUserId(userId, options = {}) {
    try {
      const { page = 1, pageSize = 10, active = true } = options;
      const offset = (page - 1) * pageSize;

      let query = `
        SELECT * FROM ${sessionModel.TABLE_NAME}
        WHERE user_id = ?
      `;

      if (active) {
        query += ' AND expires_at > CURRENT_TIMESTAMP';
      }

      query += ' ORDER BY last_activity DESC LIMIT ? OFFSET ?';

      const sessions = await db.query(query, [userId, pageSize, offset]);
      
      // 解析JSON字段
      sessions.forEach(session => {
        session.device_info = JSON.parse(session.device_info);
      });

      return sessions;
    } catch (error) {
      logger.error('获取用户会话失败', { error: error.message, userId, options });
      throw error;
    }
  }

  /**
   * 删除会话
   */
  async delete(sessionId) {
    try {
      const query = `
        DELETE FROM ${sessionModel.TABLE_NAME}
        WHERE id = ?
      `;

      await db.query(query, [sessionId]);
      return true;
    } catch (error) {
      logger.error('删除会话失败', { error: error.message, sessionId });
      throw error;
    }
  }

  /**
   * 删除用户的所有会话
   */
  async deleteByUserId(userId) {
    try {
      const query = `
        DELETE FROM ${sessionModel.TABLE_NAME}
        WHERE user_id = ?
      `;

      await db.query(query, [userId]);
      return true;
    } catch (error) {
      logger.error('删除用户会话失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 清理过期会话
   */
  async cleanupExpiredSessions() {
    try {
      const query = `
        DELETE FROM ${sessionModel.TABLE_NAME}
        WHERE expires_at <= CURRENT_TIMESTAMP
      `;

      const result = await db.query(query);
      return result.affectedRows;
    } catch (error) {
      logger.error('清理过期会话失败', { error: error.message });
      throw error;
    }
  }
}

module.exports = new SessionRepository(); 