/**
 * 设备验证服务
 * 用于验证新设备和可疑设备
 */
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const config = require('../../config');
const { logger } = require('@suoke/shared').utils;
const Redis = require('ioredis');
const deviceService = require('../device.service');
const securityLogService = require('../security-log.service');
const sessionService = require('../session.service');
const emailService = require('../email.service');
const smsService = require('../sms.service');

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port,
  keyPrefix: 'device_verification:'
});

// 验证方式
const VERIFICATION_METHODS = {
  EMAIL: 'email',
  SMS: 'sms',
  TOTP: 'totp',
  PUSH: 'push',
  RECOVERY_CODE: 'recovery_code'
};

// 验证状态
const VERIFICATION_STATUS = {
  PENDING: 'pending',
  COMPLETED: 'completed',
  EXPIRED: 'expired',
  FAILED: 'failed'
};

/**
 * 初始化设备验证流程
 * @param {string} userId 用户ID
 * @param {Object} deviceInfo 设备信息
 * @param {Object} options 选项
 * @param {string} options.method 验证方法
 * @param {string} options.sessionId 会话ID
 * @param {string} options.ip 用户IP
 * @returns {Promise<Object>} 验证信息
 */
const initiateDeviceVerification = async (userId, deviceInfo, options = {}) => {
  try {
    // 获取用户联系方式和偏好
    const { db } = require('../../config/database');
    const user = await db('users')
      .where('id', userId)
      .select('email', 'phone', 'two_factor_enabled')
      .first();
    
    if (!user) {
      throw new Error('用户不存在');
    }
    
    // 确定验证方法
    let verificationMethod = options.method || VERIFICATION_METHODS.EMAIL;
    
    // 如果用户有二因素认证，优先使用那个
    if (user.two_factor_enabled) {
      verificationMethod = VERIFICATION_METHODS.TOTP;
    } 
    // 否则根据用户联系方式选择
    else if (!user.email && user.phone) {
      verificationMethod = VERIFICATION_METHODS.SMS;
    } else if (!user.phone && user.email) {
      verificationMethod = VERIFICATION_METHODS.EMAIL;
    }
    
    // 生成验证ID和验证码
    const verificationId = uuidv4();
    const verificationCode = crypto.randomInt(100000, 999999).toString();
    const expiresIn = 15 * 60; // 15分钟
    
    // 生成设备信息摘要
    const deviceName = deviceService.normalizeDeviceInfo(deviceInfo).deviceName || '未知设备';
    
    // 创建验证记录
    const verificationData = {
      userId,
      deviceInfo: JSON.stringify(deviceInfo),
      method: verificationMethod,
      code: verificationCode,
      status: VERIFICATION_STATUS.PENDING,
      attempts: 0,
      maxAttempts: 5,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + expiresIn * 1000).toISOString(),
      sessionId: options.sessionId,
      ip: options.ip
    };
    
    // 存储到Redis
    await redis.hmset(`verification:${verificationId}`, verificationData);
    await redis.expire(`verification:${verificationId}`, expiresIn);
    
    // 发送验证码
    let sentResult = false;
    
    if (verificationMethod === VERIFICATION_METHODS.EMAIL && user.email) {
      // 发送邮件验证码
      sentResult = await sendEmailVerification(user.email, verificationCode, {
        deviceName,
        ip: options.ip
      });
    } else if (verificationMethod === VERIFICATION_METHODS.SMS && user.phone) {
      // 发送短信验证码
      sentResult = await sendSmsVerification(user.phone, verificationCode, {
        deviceName
      });
    }
    
    // 记录日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.DEVICE_VERIFICATION,
      {
        userId,
        verificationId,
        method: verificationMethod,
        deviceInfo: deviceName,
        ip: options.ip,
        sent: sentResult
      }
    );
    
    return {
      verificationId,
      method: verificationMethod,
      expiresAt: verificationData.expiresAt,
      sent: sentResult,
      contact: verificationMethod === VERIFICATION_METHODS.EMAIL ? 
        maskEmail(user.email) : 
        (verificationMethod === VERIFICATION_METHODS.SMS ? maskPhone(user.phone) : null)
    };
  } catch (error) {
    logger.error(`初始化设备验证流程失败: ${error.message}`, { error, userId });
    throw error;
  }
};

/**
 * 验证设备验证码
 * @param {string} verificationId 验证ID
 * @param {string} code 验证码
 * @returns {Promise<Object>} 验证结果
 */
const verifyDeviceCode = async (verificationId, code) => {
  try {
    // 获取验证数据
    const verificationData = await redis.hgetall(`verification:${verificationId}`);
    
    if (!verificationData || Object.keys(verificationData).length === 0) {
      return {
        success: false,
        error: 'verification_not_found',
        message: '验证记录不存在或已过期'
      };
    }
    
    // 检查状态
    if (verificationData.status !== VERIFICATION_STATUS.PENDING) {
      return {
        success: false,
        error: 'invalid_status',
        message: `验证已${verificationData.status === VERIFICATION_STATUS.COMPLETED ? '完成' : '失效'}`
      };
    }
    
    // 检查是否过期
    const expiresAt = new Date(verificationData.expiresAt);
    if (expiresAt < new Date()) {
      await redis.hset(`verification:${verificationId}`, 'status', VERIFICATION_STATUS.EXPIRED);
      
      return {
        success: false,
        error: 'verification_expired',
        message: '验证已过期'
      };
    }
    
    // 增加尝试次数
    const attempts = parseInt(verificationData.attempts || 0) + 1;
    await redis.hset(`verification:${verificationId}`, 'attempts', attempts);
    
    // 检查尝试次数是否超过限制
    if (attempts > parseInt(verificationData.maxAttempts)) {
      await redis.hset(`verification:${verificationId}`, 'status', VERIFICATION_STATUS.FAILED);
      
      // 记录日志
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.DEVICE_VERIFICATION_FAILED,
        {
          userId: verificationData.userId,
          verificationId,
          reason: 'max_attempts_exceeded'
        }
      );
      
      return {
        success: false,
        error: 'max_attempts_exceeded',
        message: '超过最大尝试次数'
      };
    }
    
    // 验证码检查
    if (code !== verificationData.code) {
      // 记录日志
      if (attempts >= parseInt(verificationData.maxAttempts)) {
        await securityLogService.logSecurityEvent(
          securityLogService.EVENT_TYPES.DEVICE_VERIFICATION_FAILED,
          {
            userId: verificationData.userId,
            verificationId,
            reason: 'invalid_code',
            attempts
          }
        );
      }
      
      return {
        success: false,
        error: 'invalid_code',
        message: '验证码无效',
        remainingAttempts: parseInt(verificationData.maxAttempts) - attempts
      };
    }
    
    // 更新状态为已完成
    await redis.hset(`verification:${verificationId}`, 'status', VERIFICATION_STATUS.COMPLETED);
    
    // 如果有会话ID，更新会话状态
    if (verificationData.sessionId) {
      await sessionService.updateSessionStatus(verificationData.sessionId, 'active');
      
      // 更新设备信息
      try {
        const deviceInfo = JSON.parse(verificationData.deviceInfo || '{}');
        
        // 注册并信任设备
        const result = await deviceService.registerAndTrustDevice(
          verificationData.userId,
          deviceInfo,
          true // 自动信任
        );
        
        // 更新会话中的设备ID
        if (result && result.id) {
          await sessionService.updateSessionDevice(verificationData.sessionId, result.id);
        }
      } catch (deviceError) {
        logger.error(`更新设备信息失败: ${deviceError.message}`, { 
          error: deviceError, 
          userId: verificationData.userId 
        });
      }
    }
    
    // 记录日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.DEVICE_VERIFICATION_SUCCESS,
      {
        userId: verificationData.userId,
        verificationId,
        attempts
      }
    );
    
    return {
      success: true,
      userId: verificationData.userId,
      sessionId: verificationData.sessionId
    };
  } catch (error) {
    logger.error(`验证设备验证码失败: ${error.message}`, { error, verificationId });
    
    return {
      success: false,
      error: 'verification_error',
      message: '验证过程中发生错误'
    };
  }
};

/**
 * 发送邮件验证码
 * @private
 * @param {string} email 邮箱
 * @param {string} code 验证码
 * @param {Object} data 额外数据
 * @returns {Promise<boolean>} 是否发送成功
 */
const sendEmailVerification = async (email, code, data = {}) => {
  try {
    if (!emailService) {
      logger.error('邮件服务未配置');
      return false;
    }
    
    // 构建邮件数据
    const emailData = {
      to: email,
      subject: '设备验证 - 索克生活',
      template: 'device-verification',
      data: {
        code,
        deviceName: data.deviceName || '未知设备',
        ip: data.ip || '未知IP',
        expiresIn: '15分钟',
        ...data
      }
    };
    
    // 发送邮件
    await emailService.sendEmail(emailData);
    return true;
  } catch (error) {
    logger.error(`发送邮件验证码失败: ${error.message}`, { error, email });
    return false;
  }
};

/**
 * 发送短信验证码
 * @private
 * @param {string} phone 手机号
 * @param {string} code 验证码
 * @param {Object} data 额外数据
 * @returns {Promise<boolean>} 是否发送成功
 */
const sendSmsVerification = async (phone, code, data = {}) => {
  try {
    if (!smsService) {
      logger.error('短信服务未配置');
      return false;
    }
    
    // 发送短信
    const result = await smsService.sendVerificationCode(
      phone,
      code,
      smsService.CODE_TYPES.DEVICE_VERIFICATION,
      {
        deviceName: data.deviceName || '未知设备'
      }
    );
    
    return result.success;
  } catch (error) {
    logger.error(`发送短信验证码失败: ${error.message}`, { error, phone });
    return false;
  }
};

/**
 * 掩盖邮箱地址
 * @private
 * @param {string} email 邮箱
 * @returns {string} 掩盖后的邮箱
 */
const maskEmail = (email) => {
  if (!email) return '';
  
  const [username, domain] = email.split('@');
  if (!username || !domain) return email;
  
  const maskedUsername = username.length <= 3 
    ? username.charAt(0) + '***' 
    : username.charAt(0) + '***' + username.charAt(username.length - 1);
    
  return `${maskedUsername}@${domain}`;
};

/**
 * 掩盖手机号
 * @private
 * @param {string} phone 手机号
 * @returns {string} 掩盖后的手机号
 */
const maskPhone = (phone) => {
  if (!phone) return '';
  
  if (phone.length <= 7) {
    return phone.substring(0, 2) + '****' + phone.substring(phone.length - 2);
  }
  
  return phone.substring(0, 3) + '****' + phone.substring(phone.length - 4);
};

/**
 * 重新发送验证码
 * @param {string} verificationId 验证ID
 * @returns {Promise<Object>} 操作结果
 */
const resendVerificationCode = async (verificationId) => {
  try {
    // 获取验证数据
    const verificationData = await redis.hgetall(`verification:${verificationId}`);
    
    if (!verificationData || Object.keys(verificationData).length === 0) {
      return {
        sent: false,
        reason: 'verification_not_found',
        message: '验证记录不存在或已过期'
      };
    }
    
    // 检查状态
    if (verificationData.status !== VERIFICATION_STATUS.PENDING) {
      return {
        sent: false,
        reason: 'invalid_status',
        message: `验证已${verificationData.status === VERIFICATION_STATUS.COMPLETED ? '完成' : '失效'}`
      };
    }
    
    // 检查是否过期
    const expiresAt = new Date(verificationData.expiresAt);
    if (expiresAt < new Date()) {
      await redis.hset(`verification:${verificationId}`, 'status', VERIFICATION_STATUS.EXPIRED);
      
      return {
        sent: false,
        reason: 'verification_expired',
        message: '验证已过期'
      };
    }
    
    // 检查重发次数
    const resendCount = parseInt(await redis.hincrby(`verification:${verificationId}`, 'resendCount', 0));
    if (resendCount >= 3) {
      return {
        sent: false,
        reason: 'max_resend_reached',
        message: '已达到最大重发次数限制'
      };
    }
    
    // 生成新的验证码
    const newCode = crypto.randomInt(100000, 999999).toString();
    
    // 更新Redis中的验证码和重发次数
    await redis.hmset(`verification:${verificationId}`, {
      code: newCode,
      resendCount: resendCount + 1,
      updatedAt: new Date().toISOString()
    });
    
    // 重新设置过期时间
    await redis.expire(`verification:${verificationId}`, 15 * 60); // 15分钟
    
    // 尝试解析设备信息
    let deviceName = '未知设备';
    try {
      const deviceInfo = JSON.parse(verificationData.deviceInfo || '{}');
      deviceName = deviceService.normalizeDeviceInfo(deviceInfo).deviceName || '未知设备';
    } catch (error) {
      logger.warn(`解析设备信息失败: ${error.message}`, { verificationId });
    }
    
    // 发送新验证码
    let sentResult = false;
    
    // 获取用户联系方式
    const { db } = require('../../config/database');
    const user = await db('users')
      .where('id', verificationData.userId)
      .select('email', 'phone')
      .first();
    
    if (!user) {
      return {
        sent: false,
        reason: 'user_not_found',
        message: '用户不存在'
      };
    }
    
    // 根据验证方法发送新验证码
    if (verificationData.method === VERIFICATION_METHODS.EMAIL && user.email) {
      sentResult = await sendEmailVerification(user.email, newCode, {
        deviceName,
        ip: verificationData.ip
      });
    } else if (verificationData.method === VERIFICATION_METHODS.SMS && user.phone) {
      sentResult = await sendSmsVerification(user.phone, newCode, {
        deviceName
      });
    }
    
    if (!sentResult) {
      return {
        sent: false,
        reason: 'send_failed',
        message: '发送验证码失败'
      };
    }
    
    // 记录日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.DEVICE_VERIFICATION_RESENT,
      {
        userId: verificationData.userId,
        verificationId,
        method: verificationData.method,
        resendCount: resendCount + 1
      }
    );
    
    return {
      sent: true,
      method: verificationData.method,
      maskedDestination: verificationData.method === VERIFICATION_METHODS.EMAIL ? 
        maskEmail(user.email) : 
        (verificationData.method === VERIFICATION_METHODS.SMS ? maskPhone(user.phone) : null)
    };
  } catch (error) {
    logger.error(`重新发送验证码失败: ${error.message}`, { error, verificationId });
    
    return {
      sent: false,
      reason: 'system_error',
      message: '系统错误，请稍后再试'
    };
  }
};

/**
 * 切换验证方法
 * @param {string} verificationId 验证ID
 * @param {string} newMethod 新的验证方法
 * @returns {Promise<Object>} 操作结果
 */
const switchVerificationMethod = async (verificationId, newMethod) => {
  try {
    // 验证新方法是否有效
    if (!Object.values(VERIFICATION_METHODS).includes(newMethod)) {
      return {
        switched: false,
        reason: 'invalid_method',
        message: '无效的验证方法'
      };
    }
    
    // 获取验证数据
    const verificationData = await redis.hgetall(`verification:${verificationId}`);
    
    if (!verificationData || Object.keys(verificationData).length === 0) {
      return {
        switched: false,
        reason: 'verification_not_found',
        message: '验证记录不存在或已过期'
      };
    }
    
    // 检查状态
    if (verificationData.status !== VERIFICATION_STATUS.PENDING) {
      return {
        switched: false,
        reason: 'invalid_status',
        message: `验证已${verificationData.status === VERIFICATION_STATUS.COMPLETED ? '完成' : '失效'}`
      };
    }
    
    // 检查是否过期
    const expiresAt = new Date(verificationData.expiresAt);
    if (expiresAt < new Date()) {
      await redis.hset(`verification:${verificationId}`, 'status', VERIFICATION_STATUS.EXPIRED);
      
      return {
        switched: false,
        reason: 'verification_expired',
        message: '验证已过期'
      };
    }
    
    // 检查是否与当前方法相同
    if (verificationData.method === newMethod) {
      return {
        switched: false,
        reason: 'same_method',
        message: '新方法与当前方法相同'
      };
    }
    
    // 获取用户信息
    const { db } = require('../../config/database');
    const user = await db('users')
      .where('id', verificationData.userId)
      .select('email', 'phone')
      .first();
    
    if (!user) {
      return {
        switched: false,
        reason: 'user_not_found',
        message: '用户不存在'
      };
    }
    
    // 确认用户有新方法所需的联系方式
    if (newMethod === VERIFICATION_METHODS.EMAIL && !user.email) {
      return {
        switched: false,
        reason: 'email_not_available',
        message: '用户没有有效的邮箱地址'
      };
    }
    
    if (newMethod === VERIFICATION_METHODS.SMS && !user.phone) {
      return {
        switched: false,
        reason: 'phone_not_available',
        message: '用户没有有效的手机号'
      };
    }
    
    // 生成新的验证码
    const newCode = crypto.randomInt(100000, 999999).toString();
    
    // 尝试解析设备信息
    let deviceName = '未知设备';
    try {
      const deviceInfo = JSON.parse(verificationData.deviceInfo || '{}');
      deviceName = deviceService.normalizeDeviceInfo(deviceInfo).deviceName || '未知设备';
    } catch (error) {
      logger.warn(`解析设备信息失败: ${error.message}`, { verificationId });
    }
    
    // 发送新验证码
    let sentResult = false;
    
    if (newMethod === VERIFICATION_METHODS.EMAIL) {
      sentResult = await sendEmailVerification(user.email, newCode, {
        deviceName,
        ip: verificationData.ip
      });
    } else if (newMethod === VERIFICATION_METHODS.SMS) {
      sentResult = await sendSmsVerification(user.phone, newCode, {
        deviceName
      });
    }
    
    if (!sentResult) {
      return {
        switched: false,
        reason: 'send_failed',
        message: '发送验证码失败'
      };
    }
    
    // 更新Redis中的验证方法和验证码
    await redis.hmset(`verification:${verificationId}`, {
      method: newMethod,
      code: newCode,
      updatedAt: new Date().toISOString()
    });
    
    // 重新设置过期时间
    await redis.expire(`verification:${verificationId}`, 15 * 60); // 15分钟
    
    // 记录日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.DEVICE_VERIFICATION_METHOD_CHANGED,
      {
        userId: verificationData.userId,
        verificationId,
        oldMethod: verificationData.method,
        newMethod
      }
    );
    
    return {
      switched: true,
      method: newMethod,
      maskedDestination: newMethod === VERIFICATION_METHODS.EMAIL ? 
        maskEmail(user.email) : 
        (newMethod === VERIFICATION_METHODS.SMS ? maskPhone(user.phone) : null),
      message: `验证方法已切换到${newMethod === VERIFICATION_METHODS.EMAIL ? '邮箱' : '短信'}`
    };
  } catch (error) {
    logger.error(`切换验证方法失败: ${error.message}`, { error, verificationId, newMethod });
    
    return {
      switched: false,
      reason: 'system_error',
      message: '系统错误，请稍后再试'
    };
  }
};

/**
 * 使用恢复码验证设备
 * @param {string} verificationId 验证ID
 * @param {string} recoveryCode 恢复码
 * @returns {Promise<Object>} 验证结果
 */
const verifyWithRecoveryCode = async (verificationId, recoveryCode) => {
  try {
    // 获取验证数据
    const verificationData = await redis.hgetall(`verification:${verificationId}`);
    
    if (!verificationData || Object.keys(verificationData).length === 0) {
      return {
        verified: false,
        reason: 'verification_not_found',
        message: '验证记录不存在或已过期'
      };
    }
    
    // 检查状态
    if (verificationData.status !== VERIFICATION_STATUS.PENDING) {
      return {
        verified: false,
        reason: 'invalid_status',
        message: `验证已${verificationData.status === VERIFICATION_STATUS.COMPLETED ? '完成' : '失效'}`
      };
    }
    
    // 检查是否过期
    const expiresAt = new Date(verificationData.expiresAt);
    if (expiresAt < new Date()) {
      await redis.hset(`verification:${verificationId}`, 'status', VERIFICATION_STATUS.EXPIRED);
      
      return {
        verified: false,
        reason: 'verification_expired',
        message: '验证已过期'
      };
    }
    
    // 获取用户的恢复码
    const { db } = require('../../config/database');
    const hashedRecoveryCode = crypto.createHash('sha256').update(recoveryCode.trim()).digest('hex');
    
    const recoveryCodeRecord = await db('recovery_codes')
      .where({
        user_id: verificationData.userId,
        code: hashedRecoveryCode,
        used: false
      })
      .first();
    
    if (!recoveryCodeRecord) {
      // 记录失败尝试
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.RECOVERY_CODE_FAILED,
        {
          userId: verificationData.userId,
          verificationId,
          ip: verificationData.ip
        }
      );
      
      return {
        verified: false,
        reason: 'invalid_recovery_code',
        message: '恢复码无效或已使用'
      };
    }
    
    // 标记恢复码为已使用
    await db('recovery_codes')
      .where('id', recoveryCodeRecord.id)
      .update({
        used: true,
        used_at: db.fn.now()
      });
    
    // 更新验证状态
    await redis.hmset(`verification:${verificationId}`, {
      status: VERIFICATION_STATUS.COMPLETED,
      verifiedAt: new Date().toISOString(),
      verifiedMethod: 'recovery_code'
    });
    
    // 处理设备信息
    let deviceId = null;
    try {
      const deviceInfo = JSON.parse(verificationData.deviceInfo || '{}');
      
      // 注册并信任设备
      const result = await deviceService.registerAndTrustDevice(
        verificationData.userId,
        deviceInfo,
        true // 自动信任通过恢复码验证的设备
      );
      
      deviceId = result?.id;
      
      // 如果有会话ID，更新会话中的设备ID
      if (deviceId && verificationData.sessionId) {
        await sessionService.updateSessionDevice(verificationData.sessionId, deviceId);
      }
    } catch (deviceError) {
      logger.error(`更新设备信息失败: ${deviceError.message}`, { 
        error: deviceError, 
        userId: verificationData.userId 
      });
    }
    
    // 记录成功日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.RECOVERY_CODE_USED,
      {
        userId: verificationData.userId,
        verificationId,
        recoveryCodeId: recoveryCodeRecord.id,
        deviceId,
        ip: verificationData.ip
      }
    );
    
    return {
      verified: true,
      deviceId,
      userId: verificationData.userId,
      sessionId: verificationData.sessionId,
      message: '恢复码验证成功'
    };
  } catch (error) {
    logger.error(`使用恢复码验证失败: ${error.message}`, { error, verificationId });
    
    return {
      verified: false,
      reason: 'system_error',
      message: '系统错误，请稍后再试'
    };
  }
};

module.exports = {
  VERIFICATION_METHODS,
  VERIFICATION_STATUS,
  initiateDeviceVerification,
  verifyDeviceCode,
  resendVerificationCode,
  switchVerificationMethod,
  verifyWithRecoveryCode
};