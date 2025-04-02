/**
 * 生物特征识别服务
 */
const crypto = require('crypto');
const db = require('../database');
const redis = require('../utils/redis');
const logger = require('../utils/logger');
const { ValidationError, AuthenticationError, NotFoundError } = require('../utils/errors');
const metricsService = require('./metrics.service');

/**
 * 生物特征识别服务类
 */
class BiometricService {
  /**
   * 构造函数
   * @param {Object} config - 配置对象
   */
  constructor(config) {
    this.config = config?.authentication?.biometric || {};
    this.enabled = this.config.enabled || false;
    this.validTypes = this.config.validTypes || ['face', 'fingerprint'];
    this.challengeExpiration = this.config.challengeExpiration || 300; // 默认5分钟
    this.maxAttempts = this.config.maxAttempts || 5;
  }

  /**
   * 注册生物特征凭证
   * @param {Object} params - 参数对象
   * @param {string} params.userId - 用户ID
   * @param {string} params.deviceId - 设备ID
   * @param {string} params.type - 生物特征类型
   * @param {string} params.publicKey - 公钥
   * @returns {Promise<Object>} 注册结果
   */
  async register({ userId, deviceId, type, publicKey }) {
    try {
      // 检查服务是否启用
      if (!this.enabled) {
        logger.warn('生物特征认证服务已禁用');
        metricsService.increment('biometric_register_error', { reason: 'disabled' });
        throw new ValidationError('生物特征认证服务已禁用');
      }

      // 验证生物特征类型
      if (!this.validTypes.includes(type)) {
        logger.warn(`不支持的生物特征类型: ${type}`);
        metricsService.increment('biometric_register_error', { reason: 'invalid_type' });
        throw new ValidationError('不支持的生物特征类型');
      }

      // 检查用户是否存在
      const users = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
      if (users.length === 0) {
        logger.warn(`用户不存在: ${userId}`);
        metricsService.increment('biometric_register_error', { reason: 'user_not_found' });
        throw new NotFoundError('用户不存在');
      }

      // 检查设备是否属于该用户
      const devices = await db.query(
        'SELECT * FROM devices WHERE id = ? AND user_id = ?',
        [deviceId, userId]
      );
      if (devices.length === 0) {
        logger.warn(`设备不属于该用户: ${deviceId}, ${userId}`);
        metricsService.increment('biometric_register_error', { reason: 'device_not_found' });
        throw new NotFoundError('设备不存在或不属于该用户');
      }

      // 查询是否已存在凭证
      const existingCredentials = await db.query(
        'SELECT * FROM biometric_credentials WHERE user_id = ? AND device_id = ? AND type = ?',
        [userId, deviceId, type]
      );

      let result;
      if (existingCredentials.length > 0) {
        // 更新现有凭证
        const credentialId = existingCredentials[0].id;
        await db.query(
          'UPDATE biometric_credentials SET public_key = ?, updated_at = NOW() WHERE id = ?',
          [publicKey, credentialId]
        );
        logger.info(`更新生物特征凭证: ${credentialId}`);
        result = { id: credentialId, updated: true };
      } else {
        // 创建新凭证
        const insertResult = await db.query(
          'INSERT INTO biometric_credentials (user_id, device_id, type, public_key, created_at, updated_at) VALUES (?, ?, ?, ?, NOW(), NOW())',
          [userId, deviceId, type, publicKey]
        );
        logger.info(`注册生物特征凭证: ${insertResult.insertId}`);
        result = { id: insertResult.insertId, updated: false };
      }

      metricsService.increment('biometric_register_success', { type });
      return result;
    } catch (error) {
      logger.error('注册生物特征凭证失败', error);
      throw error;
    }
  }

  /**
   * 验证生物特征认证
   * @param {Object} params - 参数对象
   * @param {string} params.userId - 用户ID
   * @param {string} params.deviceId - 设备ID
   * @param {string} params.type - 生物特征类型
   * @param {string} params.signedChallenge - 签名后的挑战值
   * @returns {Promise<boolean>} 验证结果
   */
  async verify({ userId, deviceId, type, signedChallenge }) {
    try {
      // 检查服务是否启用
      if (!this.enabled) {
        logger.warn('生物特征认证服务已禁用');
        metricsService.increment('biometric_verify_error', { reason: 'disabled' });
        throw new ValidationError('生物特征认证服务已禁用');
      }

      // 获取凭证
      const credentials = await db.query(
        'SELECT * FROM biometric_credentials WHERE user_id = ? AND device_id = ? AND type = ?',
        [userId, deviceId, type]
      );

      if (credentials.length === 0) {
        logger.warn(`未找到生物特征凭证: ${userId}, ${deviceId}, ${type}`);
        metricsService.increment('biometric_verify_error', { reason: 'credential_not_found' });
        throw new NotFoundError('未找到生物特征凭证');
      }

      const credential = credentials[0];
      const challengeKey = `biometric:challenge:${userId}:${deviceId}:${type}`;
      
      // 获取挑战值
      const storedChallengeData = await redis.get(challengeKey);
      if (!storedChallengeData) {
        logger.warn('挑战值不存在或已过期');
        metricsService.increment('biometric_verify_error', { reason: 'challenge_not_found' });
        throw new ValidationError('挑战值不存在或已过期');
      }

      const challengeData = JSON.parse(storedChallengeData);
      
      // 检查挑战值是否过期
      if (challengeData.expired) {
        await redis.del(challengeKey);
        logger.warn('挑战值已过期');
        metricsService.increment('biometric_verify_error', { reason: 'challenge_expired' });
        throw new ValidationError('挑战值已过期');
      }

      // 更新尝试次数
      challengeData.attempts += 1;
      
      // 检查尝试次数是否超过限制
      if (challengeData.attempts > this.maxAttempts) {
        await redis.del(challengeKey);
        logger.warn('尝试次数超过限制');
        metricsService.increment('biometric_verify_error', { reason: 'max_attempts_exceeded' });
        throw new ValidationError('尝试次数超过限制');
      }

      // TODO: 实际的签名验证逻辑，此处简化为模拟验证成功
      const isValid = true;
      
      if (isValid) {
        // 验证成功，删除挑战值
        await redis.del(challengeKey);
        
        // 更新凭证最后使用时间
        await db.query(
          'UPDATE biometric_credentials SET last_used_at = NOW() WHERE id = ?',
          [credential.id]
        );
        
        logger.info(`验证生物特征凭证成功: ${credential.id}`);
        metricsService.increment('biometric_verify_success', { type });
        return true;
      } else {
        // 验证失败，更新挑战数据
        await redis.set(challengeKey, JSON.stringify(challengeData));
        
        logger.warn(`验证生物特征凭证失败: ${credential.id}`);
        metricsService.increment('biometric_verify_error', { reason: 'signature_invalid' });
        return false;
      }
    } catch (error) {
      logger.error('验证生物特征凭证失败', error);
      throw error;
    }
  }

  /**
   * 生成挑战值
   * @param {Object} params - 参数对象
   * @param {string} params.userId - 用户ID
   * @param {string} params.deviceId - 设备ID
   * @param {string} params.type - 生物特征类型
   * @returns {Promise<string>} 挑战值
   */
  async generateChallenge({ userId, deviceId, type }) {
    try {
      // 检查服务是否启用
      if (!this.enabled) {
        logger.warn('生物特征认证服务已禁用');
        metricsService.increment('biometric_challenge_error', { reason: 'disabled' });
        throw new ValidationError('生物特征认证服务已禁用');
      }

      // 检查用户是否已注册生物特征凭证
      const credentials = await db.query(
        'SELECT * FROM biometric_credentials WHERE user_id = ? AND device_id = ? AND type = ?',
        [userId, deviceId, type]
      );

      if (credentials.length === 0) {
        logger.warn(`未找到生物特征凭证: ${userId}, ${deviceId}, ${type}`);
        metricsService.increment('biometric_challenge_error', { reason: 'no_credentials' });
        throw new NotFoundError('未找到生物特征凭证');
      }

      // 生成随机挑战值
      const challenge = crypto.randomBytes(32).toString('base64');
      const challengeKey = `biometric:challenge:${userId}:${deviceId}:${type}`;
      
      // 保存挑战值
      const challengeData = {
        challenge,
        attempts: 0,
        expired: false,
        createdAt: Date.now()
      };
      
      await redis.set(challengeKey, JSON.stringify(challengeData));
      await redis.expire(challengeKey, this.challengeExpiration);
      
      logger.info(`生成生物特征挑战值: ${userId}, ${deviceId}, ${type}`);
      metricsService.increment('biometric_challenge_generated', { type });
      
      return challenge;
    } catch (error) {
      logger.error('生成生物特征挑战值失败', error);
      throw error;
    }
  }
}

module.exports = BiometricService; 