/**
 * 用户会话管理服务
 * 负责处理用户会话的创建、获取、删除等操作
 */
const { v4: uuidv4 } = require('uuid');
const geoip = require('geoip-lite');
const { db } = require('../config/database');
const { logger } = require('@suoke/shared').utils;
const config = require('../config');
const { redis } = require('../utils/redis');
const securityLogService = require('./security-log.service');

/**
 * 会话状态枚举
 */
const SESSION_STATUS = {
  ACTIVE: 'active',     // 活动会话
  EXPIRED: 'expired',   // 已过期
  REVOKED: 'revoked',   // 已撤销
  SUSPICIOUS: 'suspicious' // 可疑会话
};

/**
 * 创建新用户会话
 * @param {string} userId 用户ID
 * @param {Object} data 会话数据
 * @param {string} data.tokenId 令牌ID
 * @param {string} data.ipAddress IP地址
 * @param {string} data.userAgent 用户代理
 * @param {Object} data.deviceInfo 设备信息
 * @param {Date} data.expiresAt 过期时间
 * @returns {Promise<Object>} 创建的会话
 */
const createSession = async (userId, data) => {
  try {
    // 准备会话数据
    const sessionId = uuidv4();
    const { tokenId, ipAddress, userAgent, deviceInfo = {}, expiresAt } = data;
    
    // 获取IP地理位置
    let location = null;
    if (ipAddress) {
      const geo = geoip.lookup(ipAddress);
      if (geo) {
        location = `${geo.city || ''}, ${geo.region || ''}, ${geo.country || ''}`.trim();
        if (location === ',,') location = null;
      }
    }
    
    // 提取设备信息
    const deviceName = deviceInfo.name || extractDeviceName(userAgent) || '未知设备';
    const deviceType = deviceInfo.type || extractDeviceType(userAgent) || '未知类型';
    const deviceOs = deviceInfo.os || extractDeviceOS(userAgent) || '未知系统';
    
    // 检测是否可疑会话
    const isSuspicious = await detectSuspiciousLogin(userId, ipAddress, userAgent);
    
    // 判断是否需要设置为当前会话
    const existingSessions = await db('user_sessions')
      .where({ user_id: userId, is_current: true })
      .count('id as count')
      .first();
    
    const isCurrent = existingSessions && existingSessions.count === 0;
    
    // 创建会话记录
    const sessionData = {
      id: sessionId,
      user_id: userId,
      token_id: tokenId,
      device_info: JSON.stringify({
        name: deviceName,
        type: deviceType,
        os: deviceOs,
        ...deviceInfo
      }),
      ip_address: ipAddress,
      user_agent: userAgent,
      location,
      is_current: isCurrent,
      status: isSuspicious ? SESSION_STATUS.SUSPICIOUS : SESSION_STATUS.ACTIVE,
      created_at: new Date(),
      last_active_at: new Date(),
      expires_at: expiresAt
    };
    
    await db('user_sessions').insert(sessionData);
    
    // 缓存会话
    await cacheSession(sessionId, {
      ...sessionData,
      device_info: JSON.parse(sessionData.device_info)
    });
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.SESSION_CREATED,
      {
        userId,
        sessionId,
        ipAddress,
        userAgent,
        deviceName,
        isSuspicious
      }
    );
    
    // 如果是可疑登录，发送安全通知
    if (isSuspicious) {
      // 异步发送通知，不等待结果
      sendSuspiciousLoginNotification(userId, {
        sessionId,
        ipAddress,
        location,
        deviceName,
        time: new Date().toISOString()
      }).catch(err => {
        logger.error(`发送可疑登录通知失败: ${err.message}`, { userId, sessionId });
      });
    }
    
    return {
      id: sessionId,
      userId,
      tokenId,
      deviceInfo: {
        name: deviceName,
        type: deviceType,
        os: deviceOs,
        ...deviceInfo
      },
      ipAddress,
      userAgent,
      location,
      isCurrent,
      status: isSuspicious ? SESSION_STATUS.SUSPICIOUS : SESSION_STATUS.ACTIVE,
      createdAt: sessionData.created_at,
      lastActiveAt: sessionData.last_active_at,
      expiresAt
    };
  } catch (error) {
    logger.error(`创建用户会话失败: ${error.message}`, { userId, error });
    throw error;
  }
};

/**
 * 获取用户会话
 * @param {string} sessionId 会话ID
 * @returns {Promise<Object>} 会话信息
 */
const getSession = async (sessionId) => {
  try {
    // 首先尝试从缓存获取
    const cachedSession = await getSessionFromCache(sessionId);
    if (cachedSession) {
      return formatSessionData(cachedSession);
    }
    
    // 缓存未命中，从数据库获取
    const session = await db('user_sessions')
      .where({ id: sessionId })
      .first();
    
    if (!session) {
      return null;
    }
    
    // 缓存会话
    await cacheSession(sessionId, session);
    
    return formatSessionData(session);
  } catch (error) {
    logger.error(`获取会话失败: ${error.message}`, { sessionId, error });
    throw error;
  }
};

/**
 * 通过令牌ID获取会话
 * @param {string} tokenId 令牌ID
 * @returns {Promise<Object>} 会话信息
 */
const getSessionByTokenId = async (tokenId) => {
  try {
    const session = await db('user_sessions')
      .where({ token_id: tokenId })
      .first();
    
    if (!session) {
      return null;
    }
    
    return formatSessionData(session);
  } catch (error) {
    logger.error(`通过令牌ID获取会话失败: ${error.message}`, { tokenId, error });
    throw error;
  }
};

/**
 * 获取用户的所有会话
 * @param {string} userId 用户ID
 * @param {Object} options 选项
 * @param {boolean} options.activeOnly 是否只返回活动会话
 * @param {number} options.limit 限制数量
 * @param {number} options.offset 偏移量
 * @returns {Promise<Array>} 会话列表
 */
const getUserSessions = async (userId, options = {}) => {
  try {
    const { activeOnly = true, limit = 10, offset = 0 } = options;
    
    let query = db('user_sessions')
      .where({ user_id: userId });
    
    if (activeOnly) {
      query = query.where({ status: SESSION_STATUS.ACTIVE })
        .orWhere({ status: SESSION_STATUS.SUSPICIOUS, user_id: userId });
    }
    
    const sessions = await query
      .orderBy('last_active_at', 'desc')
      .limit(limit)
      .offset(offset);
    
    // 获取总数
    const totalResult = await db('user_sessions')
      .where({ user_id: userId })
      .count('id as total')
      .first();
    
    const total = totalResult ? totalResult.total : 0;
    
    return {
      sessions: sessions.map(formatSessionData),
      pagination: {
        total,
        limit,
        offset,
        hasMore: offset + sessions.length < total
      }
    };
  } catch (error) {
    logger.error(`获取用户会话列表失败: ${error.message}`, { userId, error });
    throw error;
  }
};

/**
 * 更新会话最后活动时间
 * @param {string} sessionId 会话ID
 * @returns {Promise<boolean>} 是否成功
 */
const updateSessionActivity = async (sessionId) => {
  try {
    await db('user_sessions')
      .where({ id: sessionId })
      .update({
        last_active_at: new Date()
      });
    
    // 更新缓存
    const sessionKey = `session:${sessionId}`;
    const cachedSession = await redis.get(sessionKey);
    
    if (cachedSession) {
      const session = JSON.parse(cachedSession);
      session.last_active_at = new Date();
      await redis.setex(sessionKey, config.session?.cacheTTL || 3600, JSON.stringify(session));
    }
    
    return true;
  } catch (error) {
    logger.error(`更新会话活动时间失败: ${error.message}`, { sessionId, error });
    return false;
  }
};

/**
 * 设置当前会话
 * @param {string} userId 用户ID
 * @param {string} sessionId 会话ID
 * @returns {Promise<boolean>} 是否成功
 */
const setCurrentSession = async (userId, sessionId) => {
  try {
    // 事务处理
    await db.transaction(async (trx) => {
      // 将所有会话设为非当前
      await trx('user_sessions')
        .where({ user_id: userId, is_current: true })
        .update({ is_current: false });
      
      // 将指定会话设为当前
      await trx('user_sessions')
        .where({ id: sessionId, user_id: userId })
        .update({ is_current: true });
      
      // 记录安全日志
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.SESSION_CHANGED,
        {
          userId,
          sessionId
        }
      );
    });
    
    return true;
  } catch (error) {
    logger.error(`设置当前会话失败: ${error.message}`, { userId, sessionId, error });
    return false;
  }
};

/**
 * 撤销会话
 * @param {string} sessionId 会话ID
 * @param {Object} options 选项
 * @param {string} options.userId 操作用户ID
 * @param {string} options.reason 撤销原因
 * @returns {Promise<boolean>} 是否成功
 */
const revokeSession = async (sessionId, options = {}) => {
  try {
    const { userId, reason = '用户手动撤销' } = options;
    
    // 获取会话信息
    const session = await getSession(sessionId);
    
    if (!session) {
      return false;
    }
    
    // 更新会话状态
    await db('user_sessions')
      .where({ id: sessionId })
      .update({
        status: SESSION_STATUS.REVOKED,
        last_active_at: new Date()
      });
    
    // 从缓存中删除
    await redis.del(`session:${sessionId}`);
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.SESSION_REVOKED,
      {
        userId: userId || session.userId,
        sessionId,
        reason,
        targetUserId: session.userId,
        ipAddress: session.ipAddress
      }
    );
    
    return true;
  } catch (error) {
    logger.error(`撤销会话失败: ${error.message}`, { sessionId, error });
    return false;
  }
};

/**
 * 撤销用户的所有会话
 * @param {string} userId 用户ID
 * @param {Object} options 选项
 * @param {string} options.excludeSessionId 排除的会话ID
 * @param {string} options.reason 撤销原因
 * @returns {Promise<number>} 撤销的会话数量
 */
const revokeAllUserSessions = async (userId, options = {}) => {
  try {
    const { excludeSessionId, reason = '用户退出所有设备' } = options;
    
    // 查询需要撤销的会话
    let query = db('user_sessions')
      .where({
        user_id: userId,
        status: SESSION_STATUS.ACTIVE
      })
      .orWhere({
        user_id: userId,
        status: SESSION_STATUS.SUSPICIOUS
      });
    
    if (excludeSessionId) {
      query = query.whereNot({ id: excludeSessionId });
    }
    
    const sessionsToRevoke = await query.select('id');
    const sessionIds = sessionsToRevoke.map(s => s.id);
    
    if (sessionIds.length === 0) {
      return 0;
    }
    
    // 批量更新会话状态
    await db('user_sessions')
      .whereIn('id', sessionIds)
      .update({
        status: SESSION_STATUS.REVOKED,
        last_active_at: new Date()
      });
    
    // 从缓存中批量删除
    if (sessionIds.length > 0) {
      const sessionKeys = sessionIds.map(id => `session:${id}`);
      await redis.del(sessionKeys);
    }
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.ALL_SESSIONS_REVOKED,
      {
        userId,
        excludeSessionId,
        count: sessionIds.length,
        reason
      }
    );
    
    return sessionIds.length;
  } catch (error) {
    logger.error(`撤销用户所有会话失败: ${error.message}`, { userId, error });
    throw error;
  }
};

/**
 * 清理过期会话
 * @returns {Promise<number>} 清理的会话数量
 */
const cleanupExpiredSessions = async () => {
  try {
    const now = new Date();
    
    // 查询过期但未标记为过期的会话
    const expiredSessions = await db('user_sessions')
      .where('expires_at', '<', now)
      .whereNot({ status: SESSION_STATUS.EXPIRED })
      .select('id', 'user_id');
    
    if (expiredSessions.length === 0) {
      return 0;
    }
    
    const sessionIds = expiredSessions.map(s => s.id);
    
    // 批量更新会话状态
    await db('user_sessions')
      .whereIn('id', sessionIds)
      .update({
        status: SESSION_STATUS.EXPIRED,
        last_active_at: now
      });
    
    // 从缓存中批量删除
    if (sessionIds.length > 0) {
      const sessionKeys = sessionIds.map(id => `session:${id}`);
      await redis.del(sessionKeys);
    }
    
    // 按用户分组记录安全日志
    const userGroups = {};
    expiredSessions.forEach(session => {
      if (!userGroups[session.user_id]) {
        userGroups[session.user_id] = [];
      }
      userGroups[session.user_id].push(session.id);
    });
    
    // 为每个用户记录一条日志
    for (const [userId, sessions] of Object.entries(userGroups)) {
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.SESSIONS_EXPIRED,
        {
          userId,
          count: sessions.length,
          sessionIds: sessions
        }
      );
    }
    
    return sessionIds.length;
  } catch (error) {
    logger.error(`清理过期会话失败: ${error.message}`, { error });
    throw error;
  }
};

/**
 * 将会话数据缓存到Redis
 * @param {string} sessionId 会话ID
 * @param {Object} sessionData 会话数据
 * @private
 */
const cacheSession = async (sessionId, sessionData) => {
  try {
    const sessionKey = `session:${sessionId}`;
    const ttl = config.session?.cacheTTL || 3600; // 默认缓存1小时
    
    // 如果设备信息是JSON字符串，解析为对象
    if (typeof sessionData.device_info === 'string') {
      try {
        sessionData.device_info = JSON.parse(sessionData.device_info);
      } catch (e) {
        // 保持原样
      }
    }
    
    await redis.setex(sessionKey, ttl, JSON.stringify(sessionData));
  } catch (error) {
    logger.warn(`缓存会话失败: ${error.message}`, { sessionId, error });
    // 不抛出异常，缓存失败不影响主流程
  }
};

/**
 * 从缓存中获取会话
 * @param {string} sessionId 会话ID
 * @returns {Promise<Object>} 会话数据
 * @private
 */
const getSessionFromCache = async (sessionId) => {
  try {
    const sessionKey = `session:${sessionId}`;
    const cachedSession = await redis.get(sessionKey);
    
    if (!cachedSession) {
      return null;
    }
    
    return JSON.parse(cachedSession);
  } catch (error) {
    logger.warn(`从缓存获取会话失败: ${error.message}`, { sessionId, error });
    return null;
  }
};

/**
 * 格式化会话数据
 * @param {Object} session 会话数据
 * @returns {Object} 格式化后的会话数据
 * @private
 */
const formatSessionData = (session) => {
  // 如果设备信息是JSON字符串，解析为对象
  let deviceInfo = session.device_info;
  if (typeof deviceInfo === 'string') {
    try {
      deviceInfo = JSON.parse(deviceInfo);
    } catch (e) {
      deviceInfo = { name: '未知设备' };
    }
  }
  
  return {
    id: session.id,
    userId: session.user_id,
    tokenId: session.token_id,
    deviceInfo,
    ipAddress: session.ip_address,
    userAgent: session.user_agent,
    location: session.location,
    isCurrent: session.is_current,
    status: session.status,
    createdAt: session.created_at,
    lastActiveAt: session.last_active_at,
    expiresAt: session.expires_at
  };
};

/**
 * 从用户代理字符串中提取设备名称
 * @param {string} userAgent 用户代理字符串
 * @returns {string} 设备名称
 * @private
 */
const extractDeviceName = (userAgent) => {
  if (!userAgent) return null;
  
  // 移动设备匹配
  const mobileRegex = /(iPhone|iPad|iPod|Android|BlackBerry|Windows Phone)/i;
  const mobileMatch = userAgent.match(mobileRegex);
  
  if (mobileMatch) {
    return mobileMatch[0];
  }
  
  // 桌面设备匹配
  if (userAgent.includes('Windows')) {
    return 'Windows PC';
  }
  
  if (userAgent.includes('Macintosh') || userAgent.includes('Mac OS X')) {
    return 'Mac';
  }
  
  if (userAgent.includes('Linux')) {
    return 'Linux';
  }
  
  return '未知设备';
};

/**
 * 从用户代理字符串中提取设备类型
 * @param {string} userAgent 用户代理字符串
 * @returns {string} 设备类型
 * @private
 */
const extractDeviceType = (userAgent) => {
  if (!userAgent) return null;
  
  if (/(iPhone|Android.*Mobile|BlackBerry|Windows Phone)/i.test(userAgent)) {
    return '手机';
  }
  
  if (/(iPad|Android(?!.*Mobile))/i.test(userAgent)) {
    return '平板';
  }
  
  if (/(Windows|Macintosh|Linux)/i.test(userAgent)) {
    return '电脑';
  }
  
  return '未知类型';
};

/**
 * 从用户代理字符串中提取操作系统
 * @param {string} userAgent 用户代理字符串
 * @returns {string} 操作系统
 * @private
 */
const extractDeviceOS = (userAgent) => {
  if (!userAgent) return null;
  
  if (userAgent.includes('Windows NT 10.0')) return 'Windows 10';
  if (userAgent.includes('Windows NT 6.3')) return 'Windows 8.1';
  if (userAgent.includes('Windows NT 6.2')) return 'Windows 8';
  if (userAgent.includes('Windows NT 6.1')) return 'Windows 7';
  if (userAgent.includes('Windows NT 6.0')) return 'Windows Vista';
  if (userAgent.includes('Windows NT 5.1')) return 'Windows XP';
  if (userAgent.includes('Windows NT')) return 'Windows';
  
  if (userAgent.includes('Mac OS X')) {
    const macOSRegex = /Mac OS X (\d+[._]\d+[._]\d+|\d+[._]\d+)/i;
    const macOSMatch = userAgent.match(macOSRegex);
    if (macOSMatch) {
      const version = macOSMatch[1].replace(/_/g, '.');
      return `macOS ${version}`;
    }
    return 'macOS';
  }
  
  if (userAgent.includes('Android')) {
    const androidRegex = /Android (\d+(\.\d+)*)/i;
    const androidMatch = userAgent.match(androidRegex);
    if (androidMatch) {
      return `Android ${androidMatch[1]}`;
    }
    return 'Android';
  }
  
  if (userAgent.includes('iOS') || userAgent.includes('iPhone OS')) {
    const iosRegex = /OS (\d+[_\.]\d+[_\.]\d+|\d+[_\.]\d+)/i;
    const iosMatch = userAgent.match(iosRegex);
    if (iosMatch) {
      const version = iosMatch[1].replace(/_/g, '.');
      return `iOS ${version}`;
    }
    return 'iOS';
  }
  
  if (userAgent.includes('Linux')) return 'Linux';
  
  return '未知系统';
};

/**
 * 检测可疑登录
 * @param {string} userId 用户ID
 * @param {string} ipAddress IP地址
 * @param {string} userAgent 用户代理
 * @returns {Promise<boolean>} 是否为可疑登录
 * @private
 */
const detectSuspiciousLogin = async (userId, ipAddress, userAgent) => {
  try {
    if (!ipAddress) return false;
    
    // 获取用户过去的会话记录
    const previousSessions = await db('user_sessions')
      .where({ user_id: userId, status: SESSION_STATUS.ACTIVE })
      .orderBy('last_active_at', 'desc')
      .limit(5);
    
    if (previousSessions.length === 0) {
      // 这是用户的第一个会话，不标记为可疑
      return false;
    }
    
    // 检查IP地址是否匹配用户的常用IP
    const knownIPs = new Set(previousSessions.map(s => s.ip_address));
    if (!knownIPs.has(ipAddress)) {
      // 检查地理位置变化
      const geo = geoip.lookup(ipAddress);
      
      // 检查用户最近的会话地理位置
      const lastSession = previousSessions[0];
      
      if (lastSession.ip_address && lastSession.ip_address !== ipAddress) {
        const lastGeo = geoip.lookup(lastSession.ip_address);
        
        // 如果地理位置相差较大
        if (lastGeo && geo && lastGeo.country !== geo.country) {
          // 检查会话时间间隔
          const lastActive = new Date(lastSession.last_active_at);
          const now = new Date();
          const hoursDiff = (now - lastActive) / (1000 * 60 * 60);
          
          // 如果短时间内从不同国家登录，标记为可疑
          if (hoursDiff < 24) {
            logger.warn(`可疑登录检测: 用户 ${userId} 在 ${hoursDiff.toFixed(2)} 小时内从不同国家登录`, { 
              previousCountry: lastGeo.country, 
              currentCountry: geo.country 
            });
            return true;
          }
        }
      }
    }
    
    // 检查设备信息变化
    const currentDeviceType = extractDeviceType(userAgent);
    const previousDeviceTypes = new Set(
      previousSessions
        .map(s => extractDeviceType(s.user_agent))
        .filter(Boolean)
    );
    
    // 如果这是一个新设备类型，标记为可疑
    if (currentDeviceType && !previousDeviceTypes.has(currentDeviceType)) {
      // 但只有在短时间内切换设备类型时才标记
      const lastSession = previousSessions[0];
      const lastActive = new Date(lastSession.last_active_at);
      const now = new Date();
      const hoursDiff = (now - lastActive) / (1000 * 60 * 60);
      
      if (hoursDiff < 12) {
        logger.warn(`可疑登录检测: 用户 ${userId} 在 ${hoursDiff.toFixed(2)} 小时内切换设备类型`, { 
          previousDevice: extractDeviceType(lastSession.user_agent), 
          currentDevice: currentDeviceType
        });
        return true;
      }
    }
    
    return false;
  } catch (error) {
    logger.error(`检测可疑登录失败: ${error.message}`, { userId, ipAddress, error });
    return false; // 出错时不标记为可疑
  }
};

/**
 * 发送可疑登录通知
 * @param {string} userId 用户ID
 * @param {Object} data 通知数据
 * @private
 */
const sendSuspiciousLoginNotification = async (userId, data) => {
  try {
    // 获取用户信息
    const user = await db('users').where({ id: userId }).first();
    if (!user) return;
    
    // 检查用户是否开启安全通知
    const userSettings = await db('user_security_settings')
      .where({ user_id: userId })
      .first();
    
    if (!userSettings || !userSettings.suspicious_activity_notifications_enabled) {
      return;
    }
    
    // 根据用户联系方式发送通知
    // 这里只记录日志，实际实现可以通过消息队列发送邮件或短信
    logger.info(`发送可疑登录通知给用户 ${userId}`, { 
      notificationType: 'suspicious_login',
      userId,
      sessionId: data.sessionId,
      location: data.location || '未知位置',
      device: data.deviceName || '未知设备',
      ipAddress: data.ipAddress,
      time: data.time
    });
    
    // 实际发送过程需要使用通知服务
    
  } catch (error) {
    logger.error(`发送可疑登录通知失败: ${error.message}`, { userId, error });
  }
};

/**
 * 更新会话状态
 * @param {string} sessionId 会话ID
 * @param {string} status 新状态
 * @returns {Promise<boolean>} 是否成功
 */
const updateSessionStatus = async (sessionId, status) => {
  try {
    // 检查状态是否有效
    const validStatuses = Object.values(SESSION_STATUS);
    if (!validStatuses.includes(status)) {
      logger.error(`无效的会话状态: ${status}`, { sessionId });
      throw new Error('无效的会话状态');
    }
    
    // 更新会话状态
    await db('user_sessions')
      .where({ id: sessionId })
      .update({
        status: status,
        last_active_at: new Date()
      });
    
    // 更新缓存
    const sessionKey = `session:${sessionId}`;
    const cachedSession = await redis.get(sessionKey);
    
    if (cachedSession) {
      const session = JSON.parse(cachedSession);
      session.status = status;
      session.last_active_at = new Date();
      await redis.setex(sessionKey, config.session?.cacheTTL || 3600, JSON.stringify(session));
    }
    
    return true;
  } catch (error) {
    logger.error(`更新会话状态失败: ${error.message}`, { sessionId, status, error });
    return false;
  }
};

/**
 * 验证会话是否有效
 * @param {string} sessionId 会话ID
 * @param {string} userId 用户ID
 * @returns {Promise<boolean>} 会话是否有效
 */
const isSessionValid = async (sessionId, userId) => {
  try {
    // 首先尝试从缓存获取
    const cachedSession = await getSessionFromCache(sessionId);
    if (cachedSession) {
      // 验证会话状态和用户ID
      return (
        cachedSession.user_id === userId &&
        (cachedSession.status === SESSION_STATUS.ACTIVE || 
         cachedSession.status === SESSION_STATUS.SUSPICIOUS) &&
        new Date(cachedSession.expires_at) > new Date()
      );
    }
    
    // 缓存未命中，从数据库获取
    const session = await db('user_sessions')
      .where({ 
        id: sessionId,
        user_id: userId
      })
      .first();
    
    if (!session) {
      return false;
    }
    
    // 检查会话是否有效
    const isValid = (
      (session.status === SESSION_STATUS.ACTIVE || 
       session.status === SESSION_STATUS.SUSPICIOUS) &&
      new Date(session.expires_at) > new Date()
    );
    
    // 缓存会话
    if (isValid) {
      await cacheSession(sessionId, session);
    }
    
    return isValid;
  } catch (error) {
    logger.error(`验证会话有效性失败: ${error.message}`, { sessionId, userId, error });
    return false;
  }
};

/**
 * 通过ID获取会话详情
 * @param {string} sessionId 会话ID
 * @param {string} userId 用户ID
 * @returns {Promise<Object>} 会话详情
 */
const getSessionById = async (sessionId, userId) => {
  try {
    // 首先尝试从缓存获取
    const cachedSession = await getSessionFromCache(sessionId);
    if (cachedSession && cachedSession.user_id === userId) {
      return formatSessionData(cachedSession);
    }
    
    // 缓存未命中，从数据库获取
    const session = await db('user_sessions')
      .where({ 
        id: sessionId,
        user_id: userId
      })
      .first();
    
    if (!session) {
      return null;
    }
    
    // 缓存会话
    await cacheSession(sessionId, session);
    
    return formatSessionData(session);
  } catch (error) {
    logger.error(`获取会话详情失败: ${error.message}`, { sessionId, userId, error });
    return null;
  }
};

/**
 * 更新会话过期时间
 * @param {string} sessionId 会话ID
 * @param {number} expiresIn 过期时间（秒）
 * @returns {Promise<void>}
 */
const updateSessionExpiry = async (sessionId, expiresIn) => {
  try {
    const { db } = require('../config/database');
    const expiresAt = new Date(Date.now() + expiresIn * 1000);
    
    // 更新数据库中的会话过期时间
    await db('user_sessions')
      .where('id', sessionId)
      .update({
        expires_at: expiresAt,
        updated_at: new Date()
      });
    
    // 更新Redis中的会话过期时间(如果存在)
    const redisKey = `session:${sessionId}`;
    const exists = await redis.exists(redisKey);
    
    if (exists) {
      // 获取当前会话数据
      const sessionData = await redis.get(redisKey);
      if (sessionData) {
        const session = JSON.parse(sessionData);
        // 更新过期时间
        session.expires_at = expiresAt.toISOString();
        // 重新存储并设置过期时间
        await redis.set(redisKey, JSON.stringify(session), 'EX', expiresIn);
      }
    }
    
    logger.info(`会话 ${sessionId} 过期时间已更新: ${expiresAt.toISOString()}`);
  } catch (error) {
    logger.error(`更新会话过期时间错误: ${error.message}`, { error, sessionId });
    throw error;
  }
};

module.exports = {
  SESSION_STATUS,
  createSession,
  getSession,
  getSessionByTokenId,
  getUserSessions,
  updateSessionActivity,
  setCurrentSession,
  revokeSession,
  revokeAllUserSessions,
  cleanupExpiredSessions,
  updateSessionStatus,
  isSessionValid,
  getSessionById,
  updateSessionExpiry
}; 