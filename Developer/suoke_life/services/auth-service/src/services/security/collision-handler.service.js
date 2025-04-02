/**
 * 碰撞处理服务
 * 用于处理设备指纹碰撞和多设备指纹冲突的情况
 */
const config = require('../../config');
const { logger } = require('@suoke/shared').utils;
const securityLogService = require('../security-log.service');
const deviceService = require('../device.service');

/**
 * 检测设备指纹是否发生碰撞
 * @param {string} fingerprint 设备指纹
 * @param {string} userId 当前用户ID
 * @returns {Promise<Object>} 碰撞检测结果
 */
const detectFingerprintCollision = async (fingerprint, userId) => {
  try {
    if (!fingerprint || !userId) {
      return {
        collision: false,
        details: null
      };
    }
    
    // 通过指纹查找关联的设备
    const { db } = require('../../config/database');
    const devices = await db('user_devices')
      .where('device_fingerprint', fingerprint)
      .select('id', 'user_id', 'device_name', 'is_trusted', 'last_used_at');
    
    // 没有找到关联设备，不存在碰撞
    if (!devices || devices.length === 0) {
      return {
        collision: false,
        details: null
      };
    }
    
    // 仅查找到当前用户的设备，不存在碰撞
    if (devices.length === 1 && devices[0].user_id === userId) {
      return {
        collision: false,
        details: null
      };
    }
    
    // 找到多个设备，但都属于当前用户
    const otherUserDevices = devices.filter(device => device.user_id !== userId);
    if (otherUserDevices.length === 0) {
      return {
        collision: false,
        details: {
          type: 'same_user_multiple_devices',
          deviceCount: devices.length
        }
      };
    }
    
    // 找到属于其他用户的设备，存在碰撞
    // 获取涉及的用户信息
    const userIds = [...new Set(devices.map(device => device.user_id))];
    const users = await db('users')
      .whereIn('id', userIds)
      .select('id', 'username', 'email');
    
    // 构建用户映射
    const userMap = {};
    users.forEach(user => {
      userMap[user.id] = {
        username: user.username,
        email: user.email
      };
    });
    
    // 记录碰撞事件
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.DEVICE_FINGERPRINT_COLLISION,
      {
        userId,
        fingerprint,
        collidingUsers: userIds.filter(id => id !== userId),
        deviceCount: devices.length
      }
    );
    
    return {
      collision: true,
      details: {
        type: 'cross_user_collision',
        users: userIds.map(id => ({
          id,
          username: userMap[id]?.username
        })),
        deviceCount: devices.length,
        devices: devices.map(device => ({
          id: device.id,
          userId: device.user_id,
          name: device.device_name,
          isTrusted: device.is_trusted,
          lastUsed: device.last_used_at
        }))
      }
    };
  } catch (error) {
    logger.error(`检测设备指纹碰撞错误: ${error.message}`, { error, userId, fingerprint });
    
    return {
      collision: false,
      details: null,
      error: error.message
    };
  }
};

/**
 * 处理设备指纹碰撞
 * @param {string} fingerprint 设备指纹
 * @param {string} userId 当前用户ID
 * @param {Object} deviceInfo 设备信息
 * @returns {Promise<Object>} 处理结果
 */
const handleFingerprintCollision = async (fingerprint, userId, deviceInfo) => {
  try {
    // 检测碰撞
    const collisionResult = await detectFingerprintCollision(fingerprint, userId);
    
    // 没有碰撞，直接返回
    if (!collisionResult.collision) {
      return {
        handled: false,
        action: 'none',
        originalFingerprint: fingerprint,
        newFingerprint: null
      };
    }
    
    // 根据碰撞类型采取不同处理策略
    const { type } = collisionResult.details;
    
    if (type === 'same_user_multiple_devices') {
      // 同一用户的多个设备，通常不需要特殊处理
      return {
        handled: true,
        action: 'keep_existing',
        originalFingerprint: fingerprint,
        newFingerprint: null
      };
    }
    
    if (type === 'cross_user_collision') {
      // 不同用户的设备碰撞，创建一个增强的指纹
      const enhancedFingerprint = await generateEnhancedFingerprint(fingerprint, userId, deviceInfo);
      
      // 记录更新
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.DEVICE_FINGERPRINT_UPDATED,
        {
          userId,
          originalFingerprint: fingerprint,
          newFingerprint: enhancedFingerprint,
          reason: 'cross_user_collision'
        }
      );
      
      return {
        handled: true,
        action: 'create_enhanced_fingerprint',
        originalFingerprint: fingerprint,
        newFingerprint: enhancedFingerprint
      };
    }
    
    // 默认情况
    return {
      handled: false,
      action: 'unhandled_collision_type',
      originalFingerprint: fingerprint,
      newFingerprint: null
    };
  } catch (error) {
    logger.error(`处理设备指纹碰撞错误: ${error.message}`, { error, userId, fingerprint });
    
    return {
      handled: false,
      action: 'error',
      originalFingerprint: fingerprint,
      newFingerprint: null,
      error: error.message
    };
  }
};

/**
 * 生成增强的设备指纹
 * @private
 * @param {string} baseFingerprint 基础指纹
 * @param {string} userId 用户ID
 * @param {Object} deviceInfo 设备信息
 * @returns {Promise<string>} 增强的指纹
 */
const generateEnhancedFingerprint = async (baseFingerprint, userId, deviceInfo) => {
  try {
    // 处理设备信息
    const normalizedInfo = deviceService.normalizeDeviceInfo(deviceInfo);
    
    // 提取额外信息
    const extras = [
      normalizedInfo.browser,
      normalizedInfo.browserVersion,
      normalizedInfo.os,
      normalizedInfo.osVersion,
      userId.substring(0, 8)
    ].filter(Boolean);
    
    // 添加伪随机成分，确保即使相同设备、相同用户也能生成不同指纹
    const timestamp = Date.now().toString().substring(8);
    
    // 生成增强指纹
    const crypto = require('crypto');
    const enhancedData = baseFingerprint + '|' + extras.join('|') + '|' + timestamp;
    
    return crypto.createHash('sha256').update(enhancedData).digest('hex');
  } catch (error) {
    logger.error(`生成增强指纹错误: ${error.message}`, { error, userId });
    
    // 如果增强指纹生成失败，在基础指纹上添加用户ID和时间戳
    const fallbackData = `${baseFingerprint}_${userId.substring(0, 8)}_${Date.now().toString(36)}`;
    return require('crypto').createHash('sha256').update(fallbackData).digest('hex');
  }
};

module.exports = {
  detectFingerprintCollision,
  handleFingerprintCollision
};