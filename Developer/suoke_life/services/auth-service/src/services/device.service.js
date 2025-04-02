/**
 * 设备管理服务
 * 提供设备信息的存储、验证和管理功能
 */

const { v4: uuidv4 } = require('uuid');
const Redis = require('ioredis');
const { db } = require('../config/database');
const config = require('../config');
const { logger } = require('@suoke/shared').utils;
const securityLogService = require('./security-log.service');

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port
});

/**
 * 注册用户设备
 * @param {string} userId 用户ID
 * @param {Object} deviceInfo 设备信息
 * @param {boolean} isTrusted 是否为受信任设备
 * @returns {Promise<Object>} 注册的设备信息
 */
const registerDevice = async (userId, deviceInfo, isTrusted = false) => {
  try {
    // 生成设备ID
    const deviceId = uuidv4();
    const now = new Date();

    // 规范化设备信息
    const normalizedDeviceInfo = normalizeDeviceInfo(deviceInfo);
    
    // 计算设备指纹
    const deviceFingerprint = generateDeviceFingerprint(normalizedDeviceInfo);
    
    // 构建设备记录
    const deviceRecord = {
      id: deviceId,
      user_id: userId,
      device_type: normalizedDeviceInfo.deviceType || 'unknown',
      device_name: normalizedDeviceInfo.deviceName || 'Unknown Device',
      os_name: normalizedDeviceInfo.osName || 'unknown',
      os_version: normalizedDeviceInfo.osVersion || 'unknown',
      browser_name: normalizedDeviceInfo.browserName || 'unknown',
      browser_version: normalizedDeviceInfo.browserVersion || 'unknown',
      device_fingerprint: deviceFingerprint,
      is_trusted: isTrusted,
      last_used_at: now,
      created_at: now,
      updated_at: now
    };
    
    // 将设备信息存储到数据库
    await db('user_devices').insert(deviceRecord);
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      'device_registered',
      {
        userId,
        deviceId,
        deviceInfo: {
          deviceType: normalizedDeviceInfo.deviceType,
          deviceName: normalizedDeviceInfo.deviceName,
          osName: normalizedDeviceInfo.osName
        },
        isTrusted
      }
    );
    
    return {
      deviceId,
      ...deviceRecord
    };
  } catch (error) {
    logger.error(`注册设备错误: ${error.message}`, { error, userId, deviceInfo });
    throw error;
  }
};

/**
 * 识别设备
 * @param {string} userId 用户ID
 * @param {Object} deviceInfo 设备信息
 * @returns {Promise<Object>} 设备信息
 */
const identifyDevice = async (userId, deviceInfo) => {
  try {
    if (!deviceInfo) {
      return null;
    }
    
    // 规范化设备信息
    const normalizedDeviceInfo = normalizeDeviceInfo(deviceInfo);
    
    // 计算设备指纹
    const deviceFingerprint = generateDeviceFingerprint(normalizedDeviceInfo);
    
    // 查找用户的设备记录
    const device = await db('user_devices')
      .where({
        user_id: userId,
        device_fingerprint: deviceFingerprint
      })
      .orderBy('last_used_at', 'desc')
      .first();
    
    if (device) {
      // 更新设备最后使用时间
      await db('user_devices')
        .where('id', device.id)
        .update({
          last_used_at: new Date(),
          updated_at: new Date()
        });
      
      return device;
    }
    
    // 未找到现有设备，返回null
    return null;
  } catch (error) {
    logger.error(`识别设备错误: ${error.message}`, { error, userId });
    return null;
  }
};

/**
 * 标记设备为受信任
 * @param {string} userId 用户ID
 * @param {string} deviceId 设备ID
 * @returns {Promise<boolean>} 操作是否成功
 */
const trustDevice = async (userId, deviceId) => {
  try {
    // 验证设备属于该用户
    const device = await db('user_devices')
      .where({
        id: deviceId,
        user_id: userId
      })
      .first();
    
    if (!device) {
      throw new Error('设备不存在或不属于该用户');
    }
    
    // 更新设备为受信任
    await db('user_devices')
      .where('id', deviceId)
      .update({
        is_trusted: true,
        updated_at: new Date()
      });
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      'device_trusted',
      {
        userId,
        deviceId
      }
    );
    
    return true;
  } catch (error) {
    logger.error(`信任设备错误: ${error.message}`, { error, userId, deviceId });
    throw error;
  }
};

/**
 * 取消信任设备
 * @param {string} userId 用户ID
 * @param {string} deviceId 设备ID
 * @returns {Promise<boolean>} 操作是否成功
 */
const untrustDevice = async (userId, deviceId) => {
  try {
    // 验证设备属于该用户
    const device = await db('user_devices')
      .where({
        id: deviceId,
        user_id: userId
      })
      .first();
    
    if (!device) {
      throw new Error('设备不存在或不属于该用户');
    }
    
    // 更新设备为不受信任
    await db('user_devices')
      .where('id', deviceId)
      .update({
        is_trusted: false,
        updated_at: new Date()
      });
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      'device_untrusted',
      {
        userId,
        deviceId
      }
    );
    
    return true;
  } catch (error) {
    logger.error(`取消信任设备错误: ${error.message}`, { error, userId, deviceId });
    throw error;
  }
};

/**
 * 获取用户的设备列表
 * @param {string} userId 用户ID
 * @returns {Promise<Array>} 设备列表
 */
const getUserDevices = async (userId) => {
  try {
    const devices = await db('user_devices')
      .where('user_id', userId)
      .orderBy('last_used_at', 'desc')
      .select();
    
    return devices;
  } catch (error) {
    logger.error(`获取用户设备列表错误: ${error.message}`, { error, userId });
    throw error;
  }
};

/**
 * 删除设备
 * @param {string} userId 用户ID
 * @param {string} deviceId 设备ID
 * @returns {Promise<boolean>} 操作是否成功
 */
const removeDevice = async (userId, deviceId) => {
  try {
    // 验证设备属于该用户
    const device = await db('user_devices')
      .where({
        id: deviceId,
        user_id: userId
      })
      .first();
    
    if (!device) {
      throw new Error('设备不存在或不属于该用户');
    }
    
    // 删除设备
    await db('user_devices')
      .where('id', deviceId)
      .delete();
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      'device_removed',
      {
        userId,
        deviceId
      }
    );
    
    return true;
  } catch (error) {
    logger.error(`删除设备错误: ${error.message}`, { error, userId, deviceId });
    throw error;
  }
};

/**
 * 规范化设备信息
 * @param {Object} deviceInfo 原始设备信息
 * @returns {Object} 规范化后的设备信息
 */
const normalizeDeviceInfo = (deviceInfo) => {
  if (!deviceInfo) {
    return {
      deviceType: 'unknown',
      deviceName: 'Unknown Device',
      osName: 'unknown',
      osVersion: 'unknown',
      browserName: 'unknown',
      browserVersion: 'unknown'
    };
  }
  
  // 提取设备类型
  let deviceType = deviceInfo.deviceType || 'unknown';
  if (deviceInfo.userAgent) {
    if (/mobile|android|iphone|ipad|ipod/i.test(deviceInfo.userAgent)) {
      deviceType = 'mobile';
    } else if (/tablet|ipad/i.test(deviceInfo.userAgent)) {
      deviceType = 'tablet';
    } else {
      deviceType = 'desktop';
    }
  }
  
  // 提取设备名称
  let deviceName = deviceInfo.deviceName || 'Unknown Device';
  if (!deviceInfo.deviceName && deviceInfo.userAgent) {
    if (/iphone/i.test(deviceInfo.userAgent)) {
      deviceName = 'iPhone';
    } else if (/ipad/i.test(deviceInfo.userAgent)) {
      deviceName = 'iPad';
    } else if (/android/i.test(deviceInfo.userAgent)) {
      deviceName = 'Android Device';
    } else if (/windows/i.test(deviceInfo.userAgent)) {
      deviceName = 'Windows Device';
    } else if (/macintosh|mac os/i.test(deviceInfo.userAgent)) {
      deviceName = 'Mac Device';
    } else if (/linux/i.test(deviceInfo.userAgent)) {
      deviceName = 'Linux Device';
    }
  }
  
  // 提取操作系统
  let osName = deviceInfo.osName || 'unknown';
  let osVersion = deviceInfo.osVersion || 'unknown';
  if (!deviceInfo.osName && deviceInfo.userAgent) {
    if (/windows nt 10/i.test(deviceInfo.userAgent)) {
      osName = 'Windows';
      osVersion = '10';
    } else if (/windows nt 6.3/i.test(deviceInfo.userAgent)) {
      osName = 'Windows';
      osVersion = '8.1';
    } else if (/windows nt 6.2/i.test(deviceInfo.userAgent)) {
      osName = 'Windows';
      osVersion = '8';
    } else if (/windows nt 6.1/i.test(deviceInfo.userAgent)) {
      osName = 'Windows';
      osVersion = '7';
    } else if (/macintosh|mac os x/i.test(deviceInfo.userAgent)) {
      osName = 'macOS';
      const macOSVersionMatch = deviceInfo.userAgent.match(/mac os x (\d+[._]\d+[._]?\d*)/i);
      if (macOSVersionMatch) {
        osVersion = macOSVersionMatch[1].replace(/_/g, '.');
      }
    } else if (/iphone|ipad|ipod/i.test(deviceInfo.userAgent)) {
      osName = 'iOS';
      const iosVersionMatch = deviceInfo.userAgent.match(/os (\d+[_]\d+[_]?\d*)/i);
      if (iosVersionMatch) {
        osVersion = iosVersionMatch[1].replace(/_/g, '.');
      }
    } else if (/android/i.test(deviceInfo.userAgent)) {
      osName = 'Android';
      const androidVersionMatch = deviceInfo.userAgent.match(/android (\d+(\.\d+)+)/i);
      if (androidVersionMatch) {
        osVersion = androidVersionMatch[1];
      }
    } else if (/linux/i.test(deviceInfo.userAgent)) {
      osName = 'Linux';
    }
  }
  
  // 提取浏览器信息
  let browserName = deviceInfo.browserName || 'unknown';
  let browserVersion = deviceInfo.browserVersion || 'unknown';
  if (!deviceInfo.browserName && deviceInfo.userAgent) {
    if (/chrome/i.test(deviceInfo.userAgent) && !/edg|opr/i.test(deviceInfo.userAgent)) {
      browserName = 'Chrome';
      const chromeVersionMatch = deviceInfo.userAgent.match(/chrome\/(\d+(\.\d+)+)/i);
      if (chromeVersionMatch) {
        browserVersion = chromeVersionMatch[1];
      }
    } else if (/firefox/i.test(deviceInfo.userAgent)) {
      browserName = 'Firefox';
      const firefoxVersionMatch = deviceInfo.userAgent.match(/firefox\/(\d+(\.\d+)+)/i);
      if (firefoxVersionMatch) {
        browserVersion = firefoxVersionMatch[1];
      }
    } else if (/safari/i.test(deviceInfo.userAgent) && !/chrome|crios/i.test(deviceInfo.userAgent)) {
      browserName = 'Safari';
      const safariVersionMatch = deviceInfo.userAgent.match(/safari\/(\d+(\.\d+)+)/i);
      if (safariVersionMatch) {
        browserVersion = safariVersionMatch[1];
      }
    } else if (/edge|edg/i.test(deviceInfo.userAgent)) {
      browserName = 'Edge';
      const edgeVersionMatch = deviceInfo.userAgent.match(/edge\/(\d+(\.\d+)+)/i) || deviceInfo.userAgent.match(/edg\/(\d+(\.\d+)+)/i);
      if (edgeVersionMatch) {
        browserVersion = edgeVersionMatch[1];
      }
    } else if (/opr|opera/i.test(deviceInfo.userAgent)) {
      browserName = 'Opera';
      const operaVersionMatch = deviceInfo.userAgent.match(/opr\/(\d+(\.\d+)+)/i) || deviceInfo.userAgent.match(/opera\/(\d+(\.\d+)+)/i);
      if (operaVersionMatch) {
        browserVersion = operaVersionMatch[1];
      }
    }
  }
  
  return {
    deviceType,
    deviceName,
    osName,
    osVersion,
    browserName,
    browserVersion,
    userAgent: deviceInfo.userAgent || 'unknown',
    clientId: deviceInfo.clientId || null,
    appVersion: deviceInfo.appVersion || null
  };
};

/**
 * 生成设备指纹
 * @param {Object} deviceInfo 设备信息
 * @returns {string} 设备指纹哈希
 */
const generateDeviceFingerprint = (deviceInfo) => {
  try {
    const crypto = require('crypto');
    
    // 提取指纹相关字段
    const fingerprintData = [
      deviceInfo.deviceType || '',
      deviceInfo.osName || '',
      deviceInfo.osVersion || '',
      deviceInfo.browserName || '',
      deviceInfo.browserVersion || '',
      deviceInfo.userAgent || '',
      deviceInfo.clientId || '',
      deviceInfo.appVersion || ''
    ].join('|');
    
    // 生成哈希
    return crypto.createHash('sha256').update(fingerprintData).digest('hex');
  } catch (error) {
    logger.error(`生成设备指纹错误: ${error.message}`, { error });
    return 'unknown';
  }
};

/**
 * 注册新设备并自动信任
 * @param {string} userId 用户ID
 * @param {Object} deviceInfo 设备信息
 * @param {boolean} autoTrust 是否自动信任该设备
 * @returns {Promise<Object>} 新注册的设备信息
 */
const registerAndTrustDevice = async (userId, deviceInfo, autoTrust = false) => {
  try {
    // 注册设备
    const device = await registerDevice(userId, deviceInfo);
    
    // 如果autoTrust为true，自动信任设备
    if (autoTrust && device && device.id) {
      await trustDevice(userId, device.id);
      
      // 更新设备信息
      device.trusted = true;
      device.trustedAt = new Date().toISOString();
      
      // 记录安全日志
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.DEVICE_TRUSTED,
        {
          userId,
          deviceId: device.id,
          deviceName: device.device_name,
          autoTrusted: true
        }
      );
    }
    
    return device;
  } catch (error) {
    logger.error(`注册并信任设备失败: ${error.message}`, { error, userId });
    throw error;
  }
};

module.exports = {
  registerDevice,
  identifyDevice,
  trustDevice,
  untrustDevice,
  getUserDevices,
  removeDevice,
  normalizeDeviceInfo,
  generateDeviceFingerprint,
  registerAndTrustDevice
}; 