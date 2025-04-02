/**
 * 会话服务
 */
const { sessionRepository } = require('../repositories');
const { logger } = require('@suoke/shared').utils;
const config = require('../config');

class SessionService {
  /**
   * 创建会话
   */
  async createSession(userId, deviceInfo, ipAddress, userAgent) {
    try {
      // 设置会话过期时间
      const expiresAt = new Date();
      expiresAt.setHours(expiresAt.getHours() + config.session.expiresIn);

      const sessionData = {
        user_id: userId,
        device_info: deviceInfo,
        ip_address: ipAddress,
        user_agent: userAgent,
        expires_at: expiresAt
      };

      const session = await sessionRepository.create(sessionData);
      logger.info('创建会话成功', { userId, sessionId: session.id });
      return session;
    } catch (error) {
      logger.error('创建会话失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 更新会话
   */
  async updateSession(sessionId, updateData) {
    try {
      // 检查会话是否存在且未过期
      const session = await sessionRepository.findById(sessionId);
      if (!session) {
        throw new Error('会话不存在或已过期');
      }

      // 更新会话
      await sessionRepository.update(sessionId, updateData);
      logger.info('更新会话成功', { sessionId });
      return true;
    } catch (error) {
      logger.error('更新会话失败', { error: error.message, sessionId });
      throw error;
    }
  }

  /**
   * 获取会话
   */
  async getSession(sessionId) {
    try {
      const session = await sessionRepository.findById(sessionId);
      if (!session) {
        throw new Error('会话不存在或已过期');
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
  async getUserSessions(userId, options = {}) {
    try {
      const sessions = await sessionRepository.findByUserId(userId, options);
      return sessions;
    } catch (error) {
      logger.error('获取用户会话失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 删除会话
   */
  async deleteSession(sessionId) {
    try {
      await sessionRepository.delete(sessionId);
      logger.info('删除会话成功', { sessionId });
      return true;
    } catch (error) {
      logger.error('删除会话失败', { error: error.message, sessionId });
      throw error;
    }
  }

  /**
   * 删除用户的所有会话
   */
  async deleteUserSessions(userId) {
    try {
      await sessionRepository.deleteByUserId(userId);
      logger.info('删除用户所有会话成功', { userId });
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
      const deletedCount = await sessionRepository.cleanupExpiredSessions();
      logger.info('清理过期会话成功', { deletedCount });
      return deletedCount;
    } catch (error) {
      logger.error('清理过期会话失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 验证会话
   */
  async validateSession(sessionId) {
    try {
      const session = await sessionRepository.findById(sessionId);
      if (!session) {
        return false;
      }

      // 检查会话是否过期
      if (new Date() > new Date(session.expires_at)) {
        await this.deleteSession(sessionId);
        return false;
      }

      return true;
    } catch (error) {
      logger.error('验证会话失败', { error: error.message, sessionId });
      return false;
    }
  }

  /**
   * 刷新会话
   */
  async refreshSession(sessionId) {
    try {
      const session = await sessionRepository.findById(sessionId);
      if (!session) {
        throw new Error('会话不存在或已过期');
      }

      // 设置新的过期时间
      const expiresAt = new Date();
      expiresAt.setHours(expiresAt.getHours() + config.session.expiresIn);

      await sessionRepository.update(sessionId, { expires_at: expiresAt });
      logger.info('刷新会话成功', { sessionId });
      return true;
    } catch (error) {
      logger.error('刷新会话失败', { error: error.message, sessionId });
      throw error;
    }
  }
}

module.exports = new SessionService(); 