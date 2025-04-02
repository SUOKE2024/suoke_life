/**
 * 异常检测服务
 * 用于检测可疑登录尝试和不正常的账户活动
 */
const config = require('../../config');
const { logger } = require('@suoke/shared').utils;
const Redis = require('ioredis');
const securityLogService = require('../security-log.service');
const geoip = require('geoip-lite');

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port,
  keyPrefix: 'security_anomaly:'
});

/**
 * 分析登录尝试，检测可疑行为
 * @param {Object} loginData 登录数据
 * @param {string} loginData.userId 用户ID
 * @param {string} loginData.ipAddress IP地址
 * @param {string} loginData.userAgent 用户代理
 * @param {Object} loginData.deviceInfo 设备信息
 * @param {string} loginData.deviceId 设备ID
 * @returns {Promise<Object>} 检测结果
 */
const analyzeLoginAttempt = async (loginData) => {
  try {
    const { userId, ipAddress, userAgent, deviceInfo, deviceId } = loginData;
    
    // 检测结果
    const result = {
      suspicious: false,
      riskLevel: 'low', // low, medium, high
      riskFactors: [],
      requiresVerification: false,
      action: 'allow'
    };
    
    // 没有用户ID则不进行检测
    if (!userId) {
      return result;
    }
    
    // 获取用户的历史登录信息
    const userKey = `user:${userId}:logins`;
    const recentLogins = await redis.lrange(userKey, 0, 9); // 最近10次登录
    
    // 解析历史登录数据
    const parsedLogins = recentLogins.map(login => {
      try {
        return JSON.parse(login);
      } catch (e) {
        return null;
      }
    }).filter(Boolean);
    
    // 检查IP地址是否是新的
    const isNewIp = !parsedLogins.some(login => login.ipAddress === ipAddress);
    
    if (isNewIp && ipAddress) {
      result.riskFactors.push('new_ip_address');
      
      // 获取IP地理位置
      const geo = geoip.lookup(ipAddress);
      
      if (geo) {
        // 检查是否是新的国家
        const hasLoginFromCountry = parsedLogins.some(login => {
          const loginGeo = login.geo;
          return loginGeo && loginGeo.country === geo.country;
        });
        
        if (!hasLoginFromCountry && parsedLogins.length > 0) {
          result.riskFactors.push('new_country');
          result.riskLevel = 'medium';
          
          // 计算地理距离异常
          const recentLoginTime = parsedLogins[0]?.timestamp;
          const recentLoginGeo = parsedLogins[0]?.geo;
          
          if (recentLoginTime && recentLoginGeo) {
            const hoursSinceLastLogin = (Date.now() - new Date(recentLoginTime).getTime()) / (1000 * 60 * 60);
            
            if (hoursSinceLastLogin < 24 && geo.country !== recentLoginGeo.country) {
              result.riskFactors.push('impossible_travel');
              result.riskLevel = 'high';
              result.requiresVerification = true;
            }
          }
        }
      }
    }
    
    // 检查设备是否是新的
    const isNewDevice = !deviceId || !parsedLogins.some(login => login.deviceId === deviceId);
    
    if (isNewDevice) {
      result.riskFactors.push('new_device');
      
      // 新设备 + 新IP是中等风险
      if (isNewIp) {
        result.riskLevel = Math.max(result.riskLevel === 'high' ? 3 : result.riskLevel === 'medium' ? 2 : 1, 2);
        result.riskLevel = ['low', 'medium', 'high'][result.riskLevel - 1];
      }
    }
    
    // 检查用户代理是否异常
    if (userAgent) {
      const isNewUserAgent = !parsedLogins.some(login => login.userAgent === userAgent);
      
      if (isNewUserAgent && parsedLogins.length > 0) {
        result.riskFactors.push('new_user_agent');
      }
      
      // 检查是否是爬虫或自动化工具
      const botPatterns = ['bot', 'crawler', 'spider', 'headless', 'automation', 'selenium', 'phantomjs', 'puppeteer'];
      const isBotAgent = botPatterns.some(pattern => userAgent.toLowerCase().includes(pattern));
      
      if (isBotAgent) {
        result.riskFactors.push('bot_user_agent');
        result.riskLevel = 'high';
        result.requiresVerification = true;
      }
    }
    
    // 检查最近是否有失败的登录尝试
    const failedLoginCountKey = `user:${userId}:failed_logins`;
    const recentFailedCount = await redis.get(failedLoginCountKey);
    
    if (recentFailedCount && parseInt(recentFailedCount) >= 3) {
      result.riskFactors.push('recent_failed_attempts');
      result.riskLevel = Math.max(result.riskLevel === 'high' ? 3 : result.riskLevel === 'medium' ? 2 : 1, 2);
      result.riskLevel = ['low', 'medium', 'high'][result.riskLevel - 1];
    }
    
    // 高风险登录需要验证
    if (result.riskLevel === 'high') {
      result.suspicious = true;
      result.requiresVerification = true;
    } else if (result.riskLevel === 'medium') {
      result.suspicious = true;
      // 中等风险，只有在有多个风险因素时才需要验证
      result.requiresVerification = result.riskFactors.length >= 2;
    }
    
    // 如果检测到可疑活动，记录到安全日志
    if (result.suspicious) {
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.SUSPICIOUS_ACTIVITY_DETECTED,
        {
          userId,
          ipAddress,
          deviceId,
          riskLevel: result.riskLevel,
          riskFactors: result.riskFactors,
          timestamp: new Date().toISOString()
        }
      );
    }
    
    // 保存本次登录信息
    const loginInfo = {
      userId,
      ipAddress,
      userAgent,
      deviceId,
      geo: ipAddress ? geoip.lookup(ipAddress) : null,
      timestamp: new Date().toISOString()
    };
    
    await redis.lpush(userKey, JSON.stringify(loginInfo));
    await redis.ltrim(userKey, 0, 19); // 只保留最近20次登录
    
    return result;
  } catch (error) {
    logger.error(`分析登录尝试失败: ${error.message}`, { error });
    // 出错时返回低风险结果，允许登录
    return {
      suspicious: false,
      riskLevel: 'low',
      riskFactors: ['detection_error'],
      requiresVerification: false,
      action: 'allow'
    };
  }
};

/**
 * 记录失败的登录尝试
 * @param {string} userId 用户ID
 * @param {Object} attemptData 尝试数据
 * @returns {Promise<void>}
 */
const recordFailedLoginAttempt = async (userId, attemptData = {}) => {
  try {
    if (!userId) return;
    
    const key = `user:${userId}:failed_logins`;
    const count = await redis.incr(key);
    
    // 设置过期时间（1小时）
    if (count === 1) {
      await redis.expire(key, 60 * 60);
    }
    
    // 检查是否达到账户锁定阈值
    const lockThreshold = config.authentication?.passwordLogin?.maxFailedAttempts || 5;
    
    if (count >= lockThreshold) {
      // 记录账户锁定事件
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.ACCOUNT_LOCKED,
        {
          userId,
          reason: 'exceeded_max_failed_attempts',
          attemptsCount: count,
          ...attemptData
        }
      );
      
      // 返回是否应该锁定账户
      return {
        shouldLockAccount: true,
        failedAttempts: count
      };
    }
    
    return {
      shouldLockAccount: false,
      failedAttempts: count
    };
  } catch (error) {
    logger.error(`记录失败登录尝试错误: ${error.message}`, { error, userId });
    return {
      shouldLockAccount: false,
      failedAttempts: 0
    };
  }
};

/**
 * 重置失败登录尝试计数
 * @param {string} userId 用户ID
 * @returns {Promise<void>}
 */
const resetFailedLoginAttempts = async (userId) => {
  try {
    if (!userId) return;
    
    const key = `user:${userId}:failed_logins`;
    await redis.del(key);
  } catch (error) {
    logger.error(`重置失败登录尝试计数错误: ${error.message}`, { error, userId });
  }
};

module.exports = {
  analyzeLoginAttempt,
  recordFailedLoginAttempt,
  resetFailedLoginAttempts
};