/**
 * 安全通知服务
 * 用于发送安全相关的通知，如新设备登录、可疑活动检测等
 */
const config = require('../../config');
const { logger } = require('@suoke/shared').utils;
const securityLogService = require('../security-log.service');
const Redis = require('ioredis');

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port,
  keyPrefix: 'security_notification:'
});

// 通知类型
const NOTIFICATION_TYPES = {
  NEW_DEVICE_LOGIN: 'new_device_login',
  SUSPICIOUS_ACTIVITY: 'suspicious_activity',
  PASSWORD_CHANGED: 'password_changed',
  TWO_FACTOR_ENABLED: 'two_factor_enabled',
  TWO_FACTOR_DISABLED: 'two_factor_disabled',
  ACCOUNT_LOCKED: 'account_locked',
  EMAIL_CHANGED: 'email_changed',
  PHONE_CHANGED: 'phone_changed',
  RECOVERY_CODES_GENERATED: 'recovery_codes_generated',
  REMOTE_LOGOUT: 'remote_logout'
};

// 通知渠道
const NOTIFICATION_CHANNELS = {
  EMAIL: 'email',
  SMS: 'sms',
  PUSH: 'push',
  IN_APP: 'in_app'
};

/**
 * 发送安全通知
 * @param {string} userId 用户ID
 * @param {string} type 通知类型
 * @param {Object} data 通知数据
 * @param {Array<string>} channels 通知渠道
 * @returns {Promise<Object>} 通知结果
 */
const sendSecurityNotification = async (userId, type, data = {}, channels = []) => {
  try {
    if (!userId || !type) {
      throw new Error('用户ID和通知类型不能为空');
    }
    
    // 检查用户是否已禁用此类通知
    const userSettings = await getUserNotificationSettings(userId);
    
    if (userSettings && userSettings[type] === false) {
      return {
        sent: false,
        reason: 'user_disabled',
        type
      };
    }
    
    // 检查是否需要限流
    const shouldThrottle = await checkNotificationThrottle(userId, type);
    if (shouldThrottle) {
      return {
        sent: false,
        reason: 'throttled',
        type
      };
    }
    
    // 获取用户联系方式
    const { db } = require('../../config/database');
    const user = await db('users')
      .where('id', userId)
      .select('email', 'phone', 'username', 'notification_token')
      .first();
    
    if (!user) {
      throw new Error('用户不存在');
    }
    
    // 确定通知渠道
    const effectiveChannels = channels.length > 0 
      ? channels 
      : getDefaultChannelsForType(type, user);
    
    // 创建通知记录
    const notificationId = `${userId}:${type}:${Date.now()}`;
    const notificationRecord = {
      userId,
      type,
      data: JSON.stringify(data),
      channels: effectiveChannels.join(','),
      status: 'pending',
      createdAt: new Date().toISOString()
    };
    
    // 存储通知记录
    await redis.hmset(notificationId, notificationRecord);
    await redis.expire(notificationId, 7 * 24 * 60 * 60); // 保存7天
    
    // 添加到用户的通知列表
    await redis.lpush(`user:${userId}:notifications`, notificationId);
    await redis.ltrim(`user:${userId}:notifications`, 0, 99); // 只保留最近100条
    
    // 记录限流
    await recordNotificationThrottle(userId, type);
    
    // 初始化结果
    const results = {};
    
    // 发送通知到各个渠道
    for (const channel of effectiveChannels) {
      try {
        let sent = false;
        
        if (channel === NOTIFICATION_CHANNELS.EMAIL && user.email) {
          sent = await sendEmailNotification(user.email, type, data, user);
        } else if (channel === NOTIFICATION_CHANNELS.SMS && user.phone) {
          sent = await sendSmsNotification(user.phone, type, data, user);
        } else if (channel === NOTIFICATION_CHANNELS.PUSH && user.notification_token) {
          sent = await sendPushNotification(user.notification_token, type, data, user);
        } else if (channel === NOTIFICATION_CHANNELS.IN_APP) {
          sent = await storeInAppNotification(userId, type, data);
        }
        
        results[channel] = sent;
        
        if (sent) {
          await redis.hset(notificationId, `${channel}_sent`, 'true');
          await redis.hset(notificationId, `${channel}_sent_at`, new Date().toISOString());
        }
      } catch (channelError) {
        logger.error(`发送${channel}通知失败: ${channelError.message}`, { 
          error: channelError, userId, type 
        });
        results[channel] = false;
      }
    }
    
    // 更新通知状态
    const sentToAnyChannel = Object.values(results).some(Boolean);
    await redis.hset(
      notificationId, 
      'status', 
      sentToAnyChannel ? 'sent' : 'failed'
    );
    
    // 记录日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.SECURITY_NOTIFICATION_SENT,
      {
        userId,
        notificationType: type,
        channels: effectiveChannels,
        results
      }
    );
    
    return {
      sent: sentToAnyChannel,
      channels: results,
      notificationId
    };
  } catch (error) {
    logger.error(`发送安全通知失败: ${error.message}`, { error, userId, type });
    
    return {
      sent: false,
      error: error.message
    };
  }
};

/**
 * 获取用户通知设置
 * @private
 * @param {string} userId 用户ID
 * @returns {Promise<Object>} 通知设置
 */
const getUserNotificationSettings = async (userId) => {
  try {
    // 从Redis缓存中获取设置
    const cachedSettings = await redis.get(`user:${userId}:notification_settings`);
    if (cachedSettings) {
      return JSON.parse(cachedSettings);
    }
    
    // 如果缓存中没有，从数据库获取
    const { db } = require('../../config/database');
    const settings = await db('user_security_settings')
      .where('user_id', userId)
      .select('suspicious_activity_notifications_enabled')
      .first();
    
    // 构建默认设置
    const defaultSettings = {
      [NOTIFICATION_TYPES.NEW_DEVICE_LOGIN]: true,
      [NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY]: settings ? 
        !!settings.suspicious_activity_notifications_enabled : true,
      [NOTIFICATION_TYPES.PASSWORD_CHANGED]: true,
      [NOTIFICATION_TYPES.TWO_FACTOR_ENABLED]: true,
      [NOTIFICATION_TYPES.TWO_FACTOR_DISABLED]: true,
      [NOTIFICATION_TYPES.ACCOUNT_LOCKED]: true,
      [NOTIFICATION_TYPES.EMAIL_CHANGED]: true,
      [NOTIFICATION_TYPES.PHONE_CHANGED]: true,
      [NOTIFICATION_TYPES.RECOVERY_CODES_GENERATED]: true,
      [NOTIFICATION_TYPES.REMOTE_LOGOUT]: true
    };
    
    // 缓存设置
    await redis.set(
      `user:${userId}:notification_settings`,
      JSON.stringify(defaultSettings),
      'EX',
      3600 // 缓存1小时
    );
    
    return defaultSettings;
  } catch (error) {
    logger.error(`获取用户通知设置失败: ${error.message}`, { error, userId });
    
    // 返回默认所有通知都启用
    return {
      [NOTIFICATION_TYPES.NEW_DEVICE_LOGIN]: true,
      [NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY]: true,
      [NOTIFICATION_TYPES.PASSWORD_CHANGED]: true,
      [NOTIFICATION_TYPES.TWO_FACTOR_ENABLED]: true,
      [NOTIFICATION_TYPES.TWO_FACTOR_DISABLED]: true,
      [NOTIFICATION_TYPES.ACCOUNT_LOCKED]: true,
      [NOTIFICATION_TYPES.EMAIL_CHANGED]: true,
      [NOTIFICATION_TYPES.PHONE_CHANGED]: true,
      [NOTIFICATION_TYPES.RECOVERY_CODES_GENERATED]: true,
      [NOTIFICATION_TYPES.REMOTE_LOGOUT]: true
    };
  }
};

/**
 * 获取通知类型的默认渠道
 * @private
 * @param {string} type 通知类型
 * @param {Object} user 用户信息
 * @returns {Array<string>} 通知渠道
 */
const getDefaultChannelsForType = (type, user) => {
  const { EMAIL, SMS, PUSH, IN_APP } = NOTIFICATION_CHANNELS;
  
  // 根据通知类型和用户信息确定默认渠道
  switch (type) {
    case NOTIFICATION_TYPES.NEW_DEVICE_LOGIN:
    case NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY:
    case NOTIFICATION_TYPES.ACCOUNT_LOCKED:
      // 高安全性通知发送到所有可用渠道
      return [
        user.email ? EMAIL : null,
        user.phone ? SMS : null,
        user.notification_token ? PUSH : null,
        IN_APP
      ].filter(Boolean);
      
    case NOTIFICATION_TYPES.PASSWORD_CHANGED:
    case NOTIFICATION_TYPES.EMAIL_CHANGED:
    case NOTIFICATION_TYPES.PHONE_CHANGED:
    case NOTIFICATION_TYPES.TWO_FACTOR_DISABLED:
      // 安全敏感型通知发送到邮箱和短信
      return [
        user.email ? EMAIL : null,
        user.phone ? SMS : null,
        IN_APP
      ].filter(Boolean);
      
    case NOTIFICATION_TYPES.TWO_FACTOR_ENABLED:
    case NOTIFICATION_TYPES.RECOVERY_CODES_GENERATED:
    case NOTIFICATION_TYPES.REMOTE_LOGOUT:
      // 常规安全通知
      return [
        user.email ? EMAIL : null,
        IN_APP
      ].filter(Boolean);
      
    default:
      // 默认只发送邮件和应用内通知
      return [
        user.email ? EMAIL : null,
        IN_APP
      ].filter(Boolean);
  }
};

/**
 * 检查通知限流
 * @private
 * @param {string} userId 用户ID
 * @param {string} type 通知类型
 * @returns {Promise<boolean>} 是否应该限流
 */
const checkNotificationThrottle = async (userId, type) => {
  try {
    const key = `throttle:${userId}:${type}`;
    
    // 检查是否在限流期内
    const lastSent = await redis.get(key);
    
    if (!lastSent) {
      return false;
    }
    
    // 根据通知类型确定限流时间
    const now = Date.now();
    const lastSentTime = parseInt(lastSent);
    const throttleTime = getThrottleTimeForType(type);
    
    return now - lastSentTime < throttleTime;
  } catch (error) {
    logger.error(`检查通知限流失败: ${error.message}`, { error, userId, type });
    return false;
  }
};

/**
 * 记录通知限流
 * @private
 * @param {string} userId 用户ID
 * @param {string} type 通知类型
 * @returns {Promise<void>}
 */
const recordNotificationThrottle = async (userId, type) => {
  try {
    const key = `throttle:${userId}:${type}`;
    const now = Date.now();
    
    // 记录发送时间，并设置过期时间
    const throttleTime = getThrottleTimeForType(type);
    
    await redis.set(key, now, 'PX', throttleTime);
  } catch (error) {
    logger.error(`记录通知限流失败: ${error.message}`, { error, userId, type });
  }
};

/**
 * 获取通知类型的限流时间
 * @private
 * @param {string} type 通知类型
 * @returns {number} 限流时间（毫秒）
 */
const getThrottleTimeForType = (type) => {
  const MINUTE = 60 * 1000;
  const HOUR = 60 * MINUTE;
  
  // 根据通知类型返回不同的限流时间
  switch (type) {
    case NOTIFICATION_TYPES.NEW_DEVICE_LOGIN:
      return 15 * MINUTE;
      
    case NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY:
      return 30 * MINUTE;
      
    case NOTIFICATION_TYPES.ACCOUNT_LOCKED:
      return 5 * MINUTE;
      
    case NOTIFICATION_TYPES.PASSWORD_CHANGED:
    case NOTIFICATION_TYPES.EMAIL_CHANGED:
    case NOTIFICATION_TYPES.PHONE_CHANGED:
    case NOTIFICATION_TYPES.TWO_FACTOR_DISABLED:
    case NOTIFICATION_TYPES.TWO_FACTOR_ENABLED:
      return 1 * HOUR;
      
    case NOTIFICATION_TYPES.RECOVERY_CODES_GENERATED:
    case NOTIFICATION_TYPES.REMOTE_LOGOUT:
      return 3 * HOUR;
      
    default:
      return 1 * HOUR;
  }
};

/**
 * 发送邮件通知
 * @private
 * @param {string} email 邮箱
 * @param {string} type 通知类型
 * @param {Object} data 通知数据
 * @param {Object} user 用户信息
 * @returns {Promise<boolean>} 是否发送成功
 */
const sendEmailNotification = async (email, type, data, user) => {
  try {
    const emailService = require('../email.service');
    
    if (!emailService) {
      logger.error('邮件服务未配置');
      return false;
    }
    
    // 确定模板和主题
    let template = 'security-notification';
    let subject = '安全通知 - 索克生活';
    
    switch (type) {
      case NOTIFICATION_TYPES.NEW_DEVICE_LOGIN:
        template = 'new-device-login';
        subject = '新设备登录通知 - 索克生活';
        break;
        
      case NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY:
        template = 'suspicious-activity';
        subject = '可疑活动通知 - 索克生活';
        break;
        
      case NOTIFICATION_TYPES.PASSWORD_CHANGED:
        template = 'password-changed';
        subject = '密码已更改 - 索克生活';
        break;
        
      // 为其他类型指定模板...
    }
    
    // 发送邮件
    await emailService.sendEmail({
      to: email,
      subject,
      template,
      data: {
        username: user.username,
        ...data
      }
    });
    
    return true;
  } catch (error) {
    logger.error(`发送邮件通知失败: ${error.message}`, { error, email, type });
    return false;
  }
};

/**
 * 发送短信通知
 * @private
 * @param {string} phone 手机号
 * @param {string} type 通知类型
 * @param {Object} data 通知数据
 * @param {Object} user 用户信息
 * @returns {Promise<boolean>} 是否发送成功
 */
const sendSmsNotification = async (phone, type, data, user) => {
  try {
    const smsService = require('../sms.service');
    
    if (!smsService) {
      logger.error('短信服务未配置');
      return false;
    }
    
    // 根据通知类型构建短信内容
    let templateId;
    let templateParams = {};
    
    switch (type) {
      case NOTIFICATION_TYPES.NEW_DEVICE_LOGIN:
        templateId = 'security_new_device';
        templateParams = {
          deviceName: data.deviceName || '未知设备',
          time: data.time || new Date().toISOString(),
          location: data.location || '未知位置'
        };
        break;
        
      case NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY:
        templateId = 'security_suspicious';
        templateParams = {
          activity: data.activity || '可疑活动',
          time: data.time || new Date().toISOString()
        };
        break;
        
      // 为其他类型指定模板...
        
      default:
        templateId = 'security_general';
        templateParams = {
          type: getNotificationTypeText(type),
          time: data.time || new Date().toISOString()
        };
    }
    
    // 发送短信
    const result = await smsService.sendTemplateMessage(
      phone,
      templateId,
      templateParams
    );
    
    return result.success;
  } catch (error) {
    logger.error(`发送短信通知失败: ${error.message}`, { error, phone, type });
    return false;
  }
};

/**
 * 发送推送通知
 * @private
 * @param {string} token 推送token
 * @param {string} type 通知类型
 * @param {Object} data 通知数据
 * @param {Object} user 用户信息
 * @returns {Promise<boolean>} 是否发送成功
 */
const sendPushNotification = async (token, type, data, user) => {
  try {
    // 推送通知服务的实现...
    // 暂时模拟成功
    logger.debug(`模拟推送通知: ${type}`, { userId: user.id, token });
    return true;
  } catch (error) {
    logger.error(`发送推送通知失败: ${error.message}`, { error, token, type });
    return false;
  }
};

/**
 * 存储应用内通知
 * @private
 * @param {string} userId 用户ID
 * @param {string} type 通知类型
 * @param {Object} data 通知数据
 * @returns {Promise<boolean>} 是否成功
 */
const storeInAppNotification = async (userId, type, data) => {
  try {
    // 构造通知内容
    const notification = {
      id: `${Date.now()}-${Math.random().toString(36).substring(2, 10)}`,
      userId,
      type,
      title: getNotificationTitle(type),
      message: getNotificationMessage(type, data),
      data,
      read: false,
      createdAt: new Date().toISOString()
    };
    
    // 存储到Redis
    const key = `user:${userId}:in_app_notifications`;
    await redis.lpush(key, JSON.stringify(notification));
    await redis.ltrim(key, 0, 99); // 只保留最近100条
    
    return true;
  } catch (error) {
    logger.error(`存储应用内通知失败: ${error.message}`, { error, userId, type });
    return false;
  }
};

/**
 * 获取通知类型的文本表示
 * @private
 * @param {string} type 通知类型
 * @returns {string} 通知类型文本
 */
const getNotificationTypeText = (type) => {
  const typeMap = {
    [NOTIFICATION_TYPES.NEW_DEVICE_LOGIN]: '新设备登录',
    [NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY]: '可疑活动',
    [NOTIFICATION_TYPES.PASSWORD_CHANGED]: '密码已更改',
    [NOTIFICATION_TYPES.TWO_FACTOR_ENABLED]: '二因素认证已启用',
    [NOTIFICATION_TYPES.TWO_FACTOR_DISABLED]: '二因素认证已禁用',
    [NOTIFICATION_TYPES.ACCOUNT_LOCKED]: '账户已锁定',
    [NOTIFICATION_TYPES.EMAIL_CHANGED]: '邮箱已更改',
    [NOTIFICATION_TYPES.PHONE_CHANGED]: '手机号已更改',
    [NOTIFICATION_TYPES.RECOVERY_CODES_GENERATED]: '恢复码已生成',
    [NOTIFICATION_TYPES.REMOTE_LOGOUT]: '远程登出'
  };
  
  return typeMap[type] || '安全通知';
};

/**
 * 获取通知标题
 * @private
 * @param {string} type 通知类型
 * @returns {string} 通知标题
 */
const getNotificationTitle = (type) => {
  return `${getNotificationTypeText(type)} - 索克生活`;
};

/**
 * 获取通知消息
 * @private
 * @param {string} type 通知类型
 * @param {Object} data 通知数据
 * @returns {string} 通知消息
 */
const getNotificationMessage = (type, data) => {
  switch (type) {
    case NOTIFICATION_TYPES.NEW_DEVICE_LOGIN:
      return `您的账户刚刚在${data.deviceName || '新设备'}上登录，位于${data.location || '未知位置'}。如果不是您本人操作，请立即修改密码。`;
      
    case NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY:
      return `我们检测到您的账户有可疑活动：${data.activity || '不常见的登录模式'}。请检查您的账户安全。`;
      
    case NOTIFICATION_TYPES.PASSWORD_CHANGED:
      return `您的账户密码已经更改。如果不是您本人操作，请立即联系客服。`;
      
    case NOTIFICATION_TYPES.TWO_FACTOR_ENABLED:
      return `您的账户已成功启用二因素认证，提高了账户安全性。`;
      
    case NOTIFICATION_TYPES.TWO_FACTOR_DISABLED:
      return `您的账户已禁用二因素认证，这可能降低账户安全性。`;
      
    case NOTIFICATION_TYPES.ACCOUNT_LOCKED:
      return `由于${data.reason || '多次登录失败'}，您的账户已被临时锁定。请稍后再试或重置密码。`;
      
    case NOTIFICATION_TYPES.EMAIL_CHANGED:
      return `您的账户邮箱已更改为${data.newEmail || '新邮箱'}。如非本人操作，请立即联系客服。`;
      
    case NOTIFICATION_TYPES.PHONE_CHANGED:
      return `您的账户手机号已更改。如非本人操作，请立即联系客服。`;
      
    case NOTIFICATION_TYPES.RECOVERY_CODES_GENERATED:
      return `您的账户已生成新的恢复码。请妥善保存这些恢复码，以便在无法使用二因素认证时使用。`;
      
    case NOTIFICATION_TYPES.REMOTE_LOGOUT:
      return `您的账户已从${data.deviceName || '其他设备'}上登出。`;
      
    default:
      return `安全通知：有关您账户的活动。`;
  }
};

module.exports = {
  NOTIFICATION_TYPES,
  NOTIFICATION_CHANNELS,
  sendSecurityNotification
};