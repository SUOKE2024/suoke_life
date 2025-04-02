/**
 * 安全日志服务
 * 用于记录所有关键的安全事件，如登录尝试、密码更改、令牌撤销等
 */

const Redis = require('ioredis');
const config = require('../config');
const securityConfig = require('../config/security');
const { logger } = require('@suoke/shared').utils;
const { v4: uuidv4 } = require('uuid');

// 创建Redis客户端用于存储安全日志
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port,
  keyPrefix: 'security_log:'
});

// 使用安全配置中定义的事件类型
const EVENT_TYPES = securityConfig.SECURITY_EVENT_TYPES;

/**
 * 记录安全事件
 * @param {string} eventType 事件类型
 * @param {Object} data 事件数据
 * @returns {Promise<string>} 事件ID
 */
const logSecurityEvent = async (eventType, data) => {
  try {
    if (!Object.values(EVENT_TYPES).includes(eventType)) {
      logger.warn(`尝试记录未知的安全事件类型: ${eventType}`);
      eventType = 'unknown';
    }

    const eventId = uuidv4();
    const timestamp = new Date().toISOString();
    
    // 准备日志数据
    const securityLog = {
      id: eventId,
      type: eventType,
      timestamp,
      ...data,
      // 确保不记录敏感信息
      ...((data.password || data.token) && {
        sensitive: true,
        sensitiveFieldsRemoved: Object.keys(data).filter(key => 
          ['password', 'token', 'accessToken', 'refreshToken'].includes(key)
        )
      })
    };
    
    // 移除敏感字段
    const sanitizedLog = { ...securityLog };
    delete sanitizedLog.password;
    delete sanitizedLog.token;
    delete sanitizedLog.accessToken;
    delete sanitizedLog.refreshToken;

    // 存储到Redis，设置过期时间
    const expiryDays = securityConfig.SECURITY_LOGS.retentionDays || 30;
    await redis.setex(
      `${eventType}:${eventId}`,
      expiryDays * 24 * 60 * 60,
      JSON.stringify(sanitizedLog)
    );
    
    // 如果有用户ID，添加到用户的安全日志索引
    if (data.userId) {
      await redis.zadd(
        `user:${data.userId}:events`,
        new Date(timestamp).getTime(),
        `${eventType}:${eventId}`
      );
      // 限制每个用户的事件数量，保留最近的100条
      await redis.zremrangebyrank(`user:${data.userId}:events`, 0, -101);
    }
    
    // 如果是重要的安全事件，也记录到系统日志
    if (securityConfig.SECURITY_LOGS.highPriorityEvents.includes(eventType)) {
      const logLevel = eventType === EVENT_TYPES.SUSPICIOUS_ACTIVITY ? 'warn' : 'info';
      logger[logLevel](`安全事件: ${eventType}`, sanitizedLog);
    }
    
    return eventId;
  } catch (error) {
    logger.error(`记录安全事件失败: ${error.message}`, { error });
    return null;
  }
};

/**
 * 获取用户的安全日志
 * @param {string} userId 用户ID
 * @param {Object} options 选项
 * @returns {Promise<Array>} 安全日志列表
 */
const getUserSecurityLogs = async (userId, options = {}) => {
  try {
    const { limit = 20, offset = 0, startTime, endTime } = options;
    
    let eventKeys;
    if (startTime || endTime) {
      // 如果指定了时间范围，使用zrangebyscore
      const min = startTime ? new Date(startTime).getTime() : '-inf';
      const max = endTime ? new Date(endTime).getTime() : '+inf';
      eventKeys = await redis.zrangebyscore(
        `user:${userId}:events`,
        min,
        max,
        'LIMIT',
        offset,
        limit
      );
    } else {
      // 否则使用zrevrange获取最近的事件（按时间倒序）
      eventKeys = await redis.zrevrange(
        `user:${userId}:events`,
        offset,
        offset + limit - 1
      );
    }
    
    if (!eventKeys || eventKeys.length === 0) {
      return [];
    }
    
    // 获取每个事件的详细信息
    const eventPromises = eventKeys.map(key => redis.get(key));
    const eventStrings = await Promise.all(eventPromises);
    
    // 解析事件数据并按时间排序
    return eventStrings
      .filter(Boolean)
      .map(str => {
        try {
          return JSON.parse(str);
        } catch (e) {
          logger.error(`解析安全日志失败: ${e.message}`);
          return null;
        }
      })
      .filter(Boolean)
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  } catch (error) {
    logger.error(`获取用户安全日志失败: ${error.message}`, { error, userId });
    return [];
  }
};

/**
 * 清除过期的安全日志（管理任务）
 * @returns {Promise<number>} 清除的日志数量
 */
const cleanupExpiredLogs = async () => {
  try {
    // 此方法通常由定时任务调用，不在API中暴露
    // 实现清理过期日志的逻辑
    // ...
    return 0;
  } catch (error) {
    logger.error(`清理过期安全日志失败: ${error.message}`, { error });
    return 0;
  }
};

module.exports = {
  EVENT_TYPES,
  logSecurityEvent,
  getUserSecurityLogs,
  cleanupExpiredLogs
}; 