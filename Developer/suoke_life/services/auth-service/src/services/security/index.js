/**
 * 安全服务
 * 整合安全相关所有功能的中央入口点
 */
const anomalyDetection = require('./anomaly-detection.service');
const deviceVerification = require('./device-verification.service');
const collisionHandler = require('./collision-handler.service');
const notification = require('./notification.service');
const { logger } = require('@suoke/shared').utils;
const securityLogService = require('../security-log.service');

/**
 * 处理登录安全流程
 * @param {Object} data 登录数据
 * @param {string} data.userId 用户ID
 * @param {Object} data.deviceInfo 设备信息
 * @param {string} data.ipAddress IP地址
 * @param {string} data.userAgent 用户代理
 * @param {string} data.sessionId 会话ID
 * @returns {Promise<Object>} 安全处理结果
 */
const processLoginSecurity = async (data) => {
  try {
    const { userId, deviceInfo, ipAddress, userAgent, sessionId } = data;
    
    // 1. 检测设备指纹碰撞
    let deviceId = data.deviceId;
    let fingerprint = deviceInfo?.fingerprint;
    
    if (fingerprint) {
      const collisionResult = await collisionHandler.detectFingerprintCollision(fingerprint, userId);
      
      if (collisionResult.collision) {
        // 处理碰撞
        const handleResult = await collisionHandler.handleFingerprintCollision(fingerprint, userId, deviceInfo);
        
        if (handleResult.handled && handleResult.newFingerprint) {
          // 更新设备指纹
          fingerprint = handleResult.newFingerprint;
          
          if (deviceInfo) {
            deviceInfo.fingerprint = fingerprint;
          }
        }
        
        // 记录碰撞处理
        await securityLogService.logSecurityEvent(
          securityLogService.EVENT_TYPES.DEVICE_FINGERPRINT_PROCESSED,
          {
            userId,
            originalFingerprint: collisionResult.originalFingerprint,
            newFingerprint: fingerprint,
            collision: true,
            collisionType: collisionResult.details?.type
          }
        );
      }
    }
    
    // 2. 分析登录行为，检测异常
    const securityResult = await anomalyDetection.analyzeLoginAttempt({
      userId,
      ipAddress,
      userAgent,
      deviceInfo,
      deviceId
    });
    
    // 3. 根据分析结果决定是否需要额外验证
    let verificationRequired = securityResult.requiresVerification;
    let verificationInfo = null;
    
    // 4. 如果需要验证，启动设备验证流程
    if (verificationRequired) {
      verificationInfo = await deviceVerification.initiateDeviceVerification(
        userId, 
        deviceInfo,
        {
          sessionId,
          ip: ipAddress
        }
      );
      
      // 5. 如果是可疑行为，发送通知
      if (securityResult.suspicious) {
        await notification.sendSecurityNotification(
          userId,
          notification.NOTIFICATION_TYPES.SUSPICIOUS_ACTIVITY,
          {
            activity: `来自${ipAddress || '未知IP'}的可疑登录尝试`,
            deviceName: deviceInfo?.name || '未知设备',
            location: deviceInfo?.location || '未知位置',
            time: new Date().toISOString(),
            riskFactors: securityResult.riskFactors
          }
        );
      }
    }
    // 如果是新设备但不需要验证，仍然发送通知
    else if (securityResult.riskFactors.includes('new_device')) {
      await notification.sendSecurityNotification(
        userId,
        notification.NOTIFICATION_TYPES.NEW_DEVICE_LOGIN,
        {
          deviceName: deviceInfo?.name || '未知设备',
          location: deviceInfo?.location || '未知位置',
          time: new Date().toISOString(),
          ipAddress
        }
      );
    }
    
    return {
      securityChecked: true,
      deviceFingerprint: fingerprint,
      verificationRequired,
      riskLevel: securityResult.riskLevel,
      riskFactors: securityResult.riskFactors,
      verificationInfo
    };
  } catch (error) {
    logger.error(`处理登录安全流程失败: ${error.message}`, { error, userId: data?.userId });
    
    // 出错时返回默认结果，不阻止登录流程
    return {
      securityChecked: false,
      error: error.message,
      verificationRequired: false
    };
  }
};

/**
 * 验证设备验证码
 * @param {string} verificationId 验证ID
 * @param {string} code 验证码
 * @returns {Promise<Object>} 验证结果
 */
const verifyDevice = async (verificationId, code) => {
  return await deviceVerification.verifyDeviceCode(verificationId, code);
};

/**
 * 记录登录成功事件，包括安全相关处理
 * @param {string} userId 用户ID
 * @param {Object} data 登录数据
 * @returns {Promise<void>}
 */
const recordLoginSuccess = async (userId, data = {}) => {
  try {
    // 重置失败登录计数
    await anomalyDetection.resetFailedLoginAttempts(userId);
    
    // 记录登录事件
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.LOGIN_SUCCESS,
      {
        userId,
        ipAddress: data.ipAddress,
        deviceId: data.deviceId,
        userAgent: data.userAgent,
        sessionId: data.sessionId
      }
    );
  } catch (error) {
    logger.error(`记录登录成功失败: ${error.message}`, { error, userId });
  }
};

/**
 * 记录登录失败事件，包括安全相关处理
 * @param {string} userId 用户ID
 * @param {Object} data 登录数据
 * @returns {Promise<Object>} 处理结果
 */
const recordLoginFailure = async (userId, data = {}) => {
  try {
    // 记录失败登录尝试
    const failureResult = await anomalyDetection.recordFailedLoginAttempt(userId, {
      ipAddress: data.ipAddress,
      userAgent: data.userAgent,
      reason: data.reason || 'invalid_credentials'
    });
    
    // 记录日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.LOGIN_FAILED,
      {
        userId,
        ipAddress: data.ipAddress,
        userAgent: data.userAgent,
        reason: data.reason || 'invalid_credentials',
        attemptCount: failureResult.failedAttempts
      }
    );
    
    return failureResult;
  } catch (error) {
    logger.error(`记录登录失败事件错误: ${error.message}`, { error, userId });
    
    return {
      shouldLockAccount: false,
      failedAttempts: 0,
      error: error.message
    };
  }
};

module.exports = {
  // 公开子服务以便直接访问其功能
  anomalyDetection,
  deviceVerification,
  collisionHandler,
  notification,
  
  // 公开主要功能
  processLoginSecurity,
  verifyDevice,
  recordLoginSuccess,
  recordLoginFailure
};