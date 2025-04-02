/**
 * 手机验证码认证服务
 * 实现短信验证码登录、注册和验证功能
 */
const config = require('../config');
const redisClient = require('../utils/redis');
const smsService = require('./sms.service');
const userRepository = require('../models/repositories/user.repository');
const authService = require('./auth.service');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');
const { ValidationError } = require('../utils/errors');

class PhoneAuthService {
  constructor() {
    this.phoneLoginConfig = config.authentication?.phoneLogin || {};
    this.codeLength = parseInt(this.phoneLoginConfig.codeLength || 6);
    this.codeExpiration = parseInt(this.phoneLoginConfig.codeExpiration || 300); // 默认5分钟
    this.cooldownPeriod = parseInt(this.phoneLoginConfig.cooldownPeriod || 60); // 默认60秒
    this.redisKeyPrefix = 'phone:verification:';
    this.redisCooldownPrefix = 'phone:cooldown:';
  }
  
  /**
   * 生成随机验证码
   * @private
   * @returns {string} 随机验证码
   */
  _generateVerificationCode() {
    // 生成指定长度的随机数字验证码
    const digits = '0123456789';
    let code = '';
    for (let i = 0; i < this.codeLength; i++) {
      code += digits.charAt(Math.floor(Math.random() * digits.length));
    }
    return code;
  }
  
  /**
   * 发送验证码
   * @param {string} phoneNumber - 手机号码
   * @param {string} [purpose='login'] - 用途 (login|register|reset)
   * @returns {Promise<Object>} 发送结果
   */
  async sendVerificationCode(phoneNumber, purpose = 'login') {
    try {
      // 验证手机号格式
      if (!/^1[3-9]\d{9}$/.test(phoneNumber)) {
        return {
          success: false, 
          message: '手机号格式不正确'
        };
      }
      
      // 检查冷却期
      const cooldownKey = `${this.redisCooldownPrefix}${phoneNumber}`;
      const cooldownTime = await redisClient.get(cooldownKey);
      
      if (cooldownTime) {
        const remainingSeconds = parseInt(cooldownTime);
        return {
          success: false,
          message: `操作过于频繁，请在${remainingSeconds}秒后再试`,
          remainingSeconds
        };
      }
      
      // 检查用户是否存在（根据不同场景有不同逻辑）
      if (purpose === 'register') {
        const existingUser = await userRepository.findByPhone(phoneNumber);
        if (existingUser) {
          return {
            success: false,
            message: '该手机号已注册，请直接登录'
          };
        }
      } else if (purpose === 'login') {
        if (!this.phoneLoginConfig.autoCreateAccount) {
          // 如果不允许自动创建账号，需要验证用户是否存在
          const existingUser = await userRepository.findByPhone(phoneNumber);
          if (!existingUser) {
            return {
              success: false,
              message: '该手机号未注册，请先注册'
            };
          }
        }
      }
      
      // 生成验证码
      const code = this._generateVerificationCode();
      
      // 保存到Redis
      const key = `${this.redisKeyPrefix}${phoneNumber}:${purpose}`;
      const value = JSON.stringify({
        code,
        createdAt: Date.now(),
        attempts: 0,
        verified: false
      });
      
      await redisClient.set(key, value, 'EX', this.codeExpiration);
      
      // 设置冷却期
      await redisClient.set(cooldownKey, this.cooldownPeriod, 'EX', this.cooldownPeriod);
      
      // 发送短信
      const provider = this.phoneLoginConfig.defaultProvider || 'aliyun';
      const result = await smsService.sendVerificationCode(phoneNumber, code, provider);
      
      // 记录发送日志
      logger.info(`验证码发送: ${phoneNumber}, 用途: ${purpose}, 结果: ${result.success}`);
      
      return result;
    } catch (error) {
      logger.error(`验证码发送错误: ${error.message}`, { error });
      return {
        success: false,
        message: '系统错误，请稍后再试'
      };
    }
  }
  
  /**
   * 验证手机验证码
   * @param {string} phoneNumber - 手机号码
   * @param {string} code - 验证码
   * @param {string} [purpose='login'] - 用途
   * @returns {Promise<boolean>} 验证结果
   */
  async verifyCode(phoneNumber, code, purpose = 'login') {
    try {
      const key = `${this.redisKeyPrefix}${phoneNumber}:${purpose}`;
      const value = await redisClient.get(key);
      
      if (!value) {
        return {
          success: false,
          message: '验证码不存在或已过期，请重新获取'
        };
      }
      
      const verification = JSON.parse(value);
      
      // 检查验证码是否已被使用
      if (verification.verified) {
        return {
          success: false,
          message: '验证码已被使用，请重新获取'
        };
      }
      
      // 检查验证尝试次数
      const maxAttempts = 5;
      if (verification.attempts >= maxAttempts) {
        // 删除验证码，防止暴力破解
        await redisClient.del(key);
        return {
          success: false,
          message: '验证码尝试次数过多，请重新获取'
        };
      }
      
      // 验证码正确性
      if (verification.code !== code) {
        // 增加尝试次数
        verification.attempts += 1;
        await redisClient.set(key, JSON.stringify(verification), 'EX', this.codeExpiration);
        
        return {
          success: false,
          message: '验证码不正确',
          attemptsRemaining: maxAttempts - verification.attempts
        };
      }
      
      // 验证码正确
      verification.verified = true;
      await redisClient.set(key, JSON.stringify(verification), 'EX', 300); // 验证后保留5分钟，防止重放
      
      return {
        success: true,
        message: '验证成功'
      };
    } catch (error) {
      logger.error(`验证码验证错误: ${error.message}`, { error });
      return {
        success: false,
        message: '系统错误，请稍后再试'
      };
    }
  }
  
  /**
   * 手机号登录
   * @param {string} phoneNumber - 手机号码
   * @param {string} code - 验证码
   * @param {Object} clientInfo - 客户端信息
   * @returns {Promise<Object>} 登录结果
   */
  async login(phoneNumber, code, clientInfo = {}) {
    try {
      // 验证手机号格式
      if (!/^1[3-9]\d{9}$/.test(phoneNumber)) {
        throw new ValidationError('手机号格式不正确');
      }
      
      // 验证验证码
      const verifyResult = await this.verifyCode(phoneNumber, code, 'login');
      if (!verifyResult.success) {
        throw new ValidationError(verifyResult.message);
      }
      
      // 查找用户
      let user = await userRepository.findByPhone(phoneNumber);
      
      // 如果用户不存在且允许自动创建
      if (!user && this.phoneLoginConfig.autoCreateAccount) {
        const userInfo = {
          id: uuidv4(),
          username: `user_${phoneNumber.substring(phoneNumber.length - 4)}`,
          phone: phoneNumber,
          is_phone_verified: true,
          role: 'user',
          is_active: true,
          created_at: new Date(),
          updated_at: new Date(),
          last_login: new Date()
        };
        
        user = await userRepository.create(userInfo);
        logger.info(`通过手机登录自动创建用户: ${phoneNumber}`);
      } else if (!user) {
        throw new ValidationError('该手机号未注册，请先注册');
      }
      
      // 更新登录时间
      await userRepository.update(user.id, { 
        last_login: new Date(),
        login_count: (user.login_count || 0) + 1
      });
      
      // 生成JWT令牌
      const authData = await authService.generateTokens(user, clientInfo);
      
      return {
        success: true,
        message: '登录成功',
        user: {
          id: user.id,
          username: user.username,
          phone: user.phone,
          role: user.role,
          is_active: user.is_active
        },
        ...authData
      };
    } catch (error) {
      logger.error(`手机登录错误: ${error.message}`, { error });
      
      if (error instanceof ValidationError) {
        return {
          success: false,
          message: error.message
        };
      }
      
      return {
        success: false,
        message: '登录失败，请稍后再试'
      };
    }
  }
  
  /**
   * 绑定手机号
   * @param {string} userId - 用户ID
   * @param {string} phoneNumber - 手机号码
   * @param {string} code - 验证码
   * @returns {Promise<Object>} 绑定结果
   */
  async bindPhone(userId, phoneNumber, code) {
    try {
      // 验证验证码
      const verifyResult = await this.verifyCode(phoneNumber, code, 'bind');
      if (!verifyResult.success) {
        return verifyResult;
      }
      
      // 检查手机号是否已被其他用户绑定
      const existingUser = await userRepository.findByPhone(phoneNumber);
      if (existingUser && existingUser.id !== userId) {
        return {
          success: false,
          message: '该手机号已被其他账号绑定'
        };
      }
      
      // 更新用户信息
      await userRepository.update(userId, {
        phone: phoneNumber,
        is_phone_verified: true,
        updated_at: new Date()
      });
      
      return {
        success: true,
        message: '手机号绑定成功'
      };
    } catch (error) {
      logger.error(`手机号绑定错误: ${error.message}`, { error });
      return {
        success: false,
        message: '系统错误，请稍后再试'
      };
    }
  }
}

module.exports = new PhoneAuthService(); 