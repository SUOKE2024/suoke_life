/**
 * 双因素认证服务
 * 支持基于时间的一次性密码(TOTP)认证
 */

const crypto = require('crypto');
const speakeasy = require('speakeasy');
const qrcode = require('qrcode');
const Redis = require('ioredis');
const { v4: uuidv4 } = require('uuid');
const config = require('../config');
const { logger } = require('@suoke/shared').utils;
const securityLogService = require('./security-log.service');

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port
});

/**
 * 生成TOTP密钥和二维码
 * @param {string} userId 用户ID
 * @param {string} username 用户名
 * @returns {Promise<Object>} 密钥和二维码
 */
const generateTOTPSecret = async (userId, username) => {
  try {
    // 生成随机密钥
    const secret = speakeasy.generateSecret({
      length: 20,
      name: `${config.app.name || 'SuokeLife'}:${username}`,
      issuer: config.app.name || 'SuokeLife'
    });

    // 生成二维码
    const qrCodeUrl = await new Promise((resolve, reject) => {
      qrcode.toDataURL(secret.otpauth_url, (err, data) => {
        if (err) reject(err);
        else resolve(data);
      });
    });

    // 将密钥临时存储在Redis中，等待验证
    // 设置10分钟过期时间，用户必须在此时间内完成设置
    const setupId = uuidv4();
    await redis.setex(
      `2fa_setup:${userId}:${setupId}`,
      600, // 10分钟
      JSON.stringify({
        secret: secret.base32,
        otpauth_url: secret.otpauth_url,
        created_at: new Date().toISOString()
      })
    );

    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.TWO_FACTOR_ENABLED,
      {
        userId,
        setupId,
        method: 'TOTP',
        status: 'pending'
      }
    );

    return {
      setupId,
      secret: secret.base32,
      qrCode: qrCodeUrl
    };
  } catch (error) {
    logger.error(`生成TOTP密钥错误: ${error.message}`, { error, userId });
    throw new Error('无法生成二因素认证密钥');
  }
};

/**
 * 验证并激活TOTP设置
 * @param {string} userId 用户ID
 * @param {string} setupId 设置ID
 * @param {string} token 验证码
 * @returns {Promise<boolean>} 是否验证成功
 */
const verifyAndActivateTOTP = async (userId, setupId, token) => {
  try {
    // 从Redis获取密钥
    const setupData = await redis.get(`2fa_setup:${userId}:${setupId}`);
    if (!setupData) {
      throw new Error('设置已过期或无效');
    }

    const { secret } = JSON.parse(setupData);

    // 验证令牌
    const verified = speakeasy.totp.verify({
      secret,
      encoding: 'base32',
      token,
      window: 1 // 允许前后1个时间窗口的验证码
    });

    if (!verified) {
      throw new Error('验证码无效');
    }

    // 保存已验证的密钥到数据库
    const { db } = require('../config/database');
    await db('users')
      .where('id', userId)
      .update({
        two_factor_enabled: true,
        two_factor_secret: secret,
        two_factor_method: 'TOTP',
        updated_at: new Date()
      });

    // 生成恢复码
    const recoveryCodes = await generateRecoveryCodes(userId);

    // 删除临时设置数据
    await redis.del(`2fa_setup:${userId}:${setupId}`);

    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.TWO_FACTOR_ENABLED,
      {
        userId,
        method: 'TOTP',
        status: 'activated'
      }
    );

    return {
      activated: true,
      recoveryCodes
    };
  } catch (error) {
    logger.error(`验证TOTP设置错误: ${error.message}`, { error, userId });
    throw error;
  }
};

/**
 * 验证TOTP令牌
 * @param {string} userId 用户ID
 * @param {string} token 令牌
 * @returns {Promise<boolean>} 是否验证成功
 */
const verifyTOTP = async (userId, token) => {
  try {
    // 从数据库获取用户的密钥
    const { db } = require('../config/database');
    const user = await db('users')
      .where('id', userId)
      .select('two_factor_secret', 'two_factor_enabled', 'two_factor_method')
      .first();

    if (!user || !user.two_factor_enabled || user.two_factor_method !== 'TOTP') {
      return false;
    }

    // 验证令牌
    const verified = speakeasy.totp.verify({
      secret: user.two_factor_secret,
      encoding: 'base32',
      token,
      window: 1 // 允许前后1个时间窗口的验证码
    });

    // 检查是否使用了恢复码
    let recoveryUsed = false;
    if (!verified) {
      recoveryUsed = await verifyRecoveryCode(userId, token);
      if (!recoveryUsed) {
        return false;
      }
    }

    // 记录成功验证
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.LOGIN_SUCCESS,
      {
        userId,
        twoFactorUsed: true,
        twoFactorMethod: recoveryUsed ? 'recovery_code' : 'TOTP'
      }
    );

    return true;
  } catch (error) {
    logger.error(`验证TOTP错误: ${error.message}`, { error, userId });
    return false;
  }
};

/**
 * 生成恢复码
 * @param {string} userId 用户ID
 * @param {number} count 生成数量，默认10个
 * @param {boolean} replaceExisting 是否替换现有的恢复码
 * @returns {Promise<string[]>} 生成的恢复码列表
 */
const generateRecoveryCodes = async (userId, count = 10, replaceExisting = false) => {
  try {
    const { db } = require('../config/database');
    const crypto = require('crypto');
    const bcrypt = require('bcrypt');
    const SALT_ROUNDS = 10;
    
    // 检查用户是否存在并启用了2FA
    const user = await db('users')
      .where({ id: userId })
      .select('two_factor_enabled')
      .first();
      
    if (!user) {
      throw new Error('用户不存在');
    }
    
    if (!user.two_factor_enabled) {
      throw new Error('用户未启用二因素认证');
    }
    
    // 如果需要替换现有的恢复码，则先删除
    if (replaceExisting) {
      await db('two_factor_recovery_codes')
        .where('user_id', userId)
        .delete();
    }
    
    // 生成新的恢复码
    const recoveryCodes = [];
    const recoveryCodesForDB = [];
    
    for (let i = 0; i < count; i++) {
      // 生成安全随机字符串作为恢复码 (格式: XXXX-XXXX-XXXX-XXXX)
      const buffer = crypto.randomBytes(16);
      const segments = [];
      
      for (let j = 0; j < 4; j++) {
        const segment = buffer.slice(j * 4, (j + 1) * 4).toString('hex').toUpperCase();
        segments.push(segment);
      }
      
      const recoveryCode = segments.join('-');
      recoveryCodes.push(recoveryCode);
      
      // 对恢复码进行哈希后存储
      const codeHash = await bcrypt.hash(recoveryCode, SALT_ROUNDS);
      
      recoveryCodesForDB.push({
        user_id: userId,
        code_hash: codeHash,
        used: false,
        created_at: new Date()
      });
    }
    
    // 批量插入恢复码记录到数据库
    await db('two_factor_recovery_codes').insert(recoveryCodesForDB);
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.TWO_FACTOR_RECOVERY_CODES_GENERATED,
      {
        userId,
        count,
        replaceExisting
      }
    );
    
    return recoveryCodes;
  } catch (error) {
    logger.error(`生成恢复码错误: ${error.message}`, { error, userId });
    throw error;
  }
};

/**
 * 验证恢复码
 * @param {string} userId 用户ID
 * @param {string} recoveryCode 恢复码明文
 * @returns {Promise<boolean>} 验证是否成功
 */
const verifyRecoveryCode = async (userId, recoveryCode) => {
  try {
    const { db } = require('../config/database');
    const bcrypt = require('bcrypt');
    
    // 获取用户的所有未使用恢复码
    const recoveryCodeRecords = await db('two_factor_recovery_codes')
      .where({
        user_id: userId,
        used: false
      })
      .select('id', 'code_hash');
    
    if (!recoveryCodeRecords || recoveryCodeRecords.length === 0) {
      logger.warn(`用户 ${userId} 没有可用的恢复码`);
      return false;
    }
    
    // 依次验证每个恢复码
    for (const record of recoveryCodeRecords) {
      const isValid = await bcrypt.compare(recoveryCode, record.code_hash);
      
      if (isValid) {
        // 标记恢复码为已使用
        await db('two_factor_recovery_codes')
          .where('id', record.id)
          .update({
            used: true,
            used_at: new Date()
          });
        
        // 记录安全日志
        await securityLogService.logSecurityEvent(
          securityLogService.EVENT_TYPES.TWO_FACTOR_RECOVERY_CODE_USED,
          {
            userId,
            recoveryCodeId: record.id
          }
        );
        
        return true;
      }
    }
    
    // 所有恢复码都不匹配
    logger.warn(`用户 ${userId} 提供的恢复码无效`);
    return false;
  } catch (error) {
    logger.error(`验证恢复码错误: ${error.message}`, { error, userId });
    throw error;
  }
};

/**
 * 禁用二因素认证
 * @param {string} userId 用户ID
 * @param {string} password 当前密码(用于验证)
 * @returns {Promise<boolean>} 是否成功禁用
 */
const disableTwoFactor = async (userId, password) => {
  try {
    // 验证密码
    const { db } = require('../config/database');
    const user = await db('users')
      .where('id', userId)
      .select('password', 'two_factor_enabled')
      .first();
    
    if (!user) {
      throw new Error('用户不存在');
    }
    
    if (!user.two_factor_enabled) {
      throw new Error('用户未启用二因素认证');
    }
    
    // 验证密码
    const bcrypt = require('bcrypt');
    const isPasswordValid = await bcrypt.compare(password, user.password);
    
    if (!isPasswordValid) {
      throw new Error('密码错误');
    }
    
    // 禁用二因素认证
    await db('users')
      .where('id', userId)
      .update({
        two_factor_enabled: false,
        two_factor_secret: null,
        two_factor_method: null,
        updated_at: new Date()
      });
    
    // 删除恢复码
    await db('two_factor_recovery_codes')
      .where('user_id', userId)
      .delete();
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.TWO_FACTOR_DISABLED,
      {
        userId,
        verificationMethod: 'password'
      }
    );
    
    return true;
  } catch (error) {
    logger.error(`禁用二因素认证错误: ${error.message}`, { error, userId });
    throw error;
  }
};

module.exports = {
  generateTOTPSecret,
  verifyAndActivateTOTP,
  verifyTOTP,
  generateRecoveryCodes,
  verifyRecoveryCode,
  disableTwoFactor
}; 