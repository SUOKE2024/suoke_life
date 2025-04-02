/**
 * 密码策略中间件
 * 增强密码安全性检查
 */
const axios = require('axios');
const crypto = require('crypto');
const config = require('../config');
const logger = require('../utils/logger');
const { ValidationError } = require('../utils/errors');

/**
 * 密码策略检查器
 */
class PasswordPolicyChecker {
  constructor() {
    // 读取配置
    this.passwordPolicy = config.security?.passwordPolicy || {};
    
    // 密码策略参数
    this.minLength = this.passwordPolicy.minLength || 10;
    this.requireLowercase = this.passwordPolicy.requireLowercase !== false;
    this.requireUppercase = this.passwordPolicy.requireUppercase !== false;
    this.requireNumbers = this.passwordPolicy.requireNumbers !== false;
    this.requireSpecialChars = this.passwordPolicy.requireSpecialChars !== false;
    this.maxRepeatingChars = this.passwordPolicy.maxRepeatingChars || 3;
    this.preventCommonPasswords = this.passwordPolicy.preventCommonPasswords !== false;
    
    // 泄露密码检查配置
    this.breachedPasswordCheck = config.security?.advancedProtection?.breachedPasswordCheck || {};
    this.checkBreachedPasswords = this.breachedPasswordCheck.enabled !== false;
    this.apiEndpoint = this.breachedPasswordCheck.apiEndpoint || 'https://api.pwnedpasswords.com/range/';
    this.cacheResults = this.breachedPasswordCheck.cacheResults !== false;
    this.cacheTTL = this.breachedPasswordCheck.cacheTTL || 86400; // 24小时
    
    // 高风险密码缓存
    this.breachedCache = new Map();
    
    // 常见密码检查
    this.commonPasswords = new Set([
      'password', 'password123', '123456', 'qwerty', 'admin', 
      'welcome', 'login', 'abc123', 'letmein', '111111', 
      '12345678', 'iloveyou', '1234567', 'monkey', 'dragon'
    ]);
    
    logger.info('密码策略已初始化');
  }
  
  /**
   * 验证密码是否符合策略
   * @param {string} password - 密码
   * @param {string} username - 用户名，用于检查密码中是否包含用户名
   * @param {string} email - 电子邮件，用于检查密码中是否包含邮件地址
   * @returns {Promise<Object>} 验证结果
   */
  async validatePassword(password, username = '', email = '') {
    try {
      // 基本密码策略检查
      const basicCheck = this._checkBasicPolicy(password, username, email);
      
      if (!basicCheck.valid) {
        return basicCheck;
      }
      
      // 检查常见密码
      if (this.preventCommonPasswords && this._isCommonPassword(password)) {
        return {
          valid: false,
          message: '密码过于常见，请使用更复杂的密码'
        };
      }
      
      // 检查泄露密码
      if (this.checkBreachedPasswords) {
        const breachCheck = await this._checkBreachedPassword(password);
        if (!breachCheck.valid) {
          return breachCheck;
        }
      }
      
      return {
        valid: true,
        message: '密码符合安全策略'
      };
    } catch (error) {
      logger.error(`密码验证失败: ${error.message}`, { error });
      
      // 默认允许密码通过，以防安全检查工具临时不可用
      return {
        valid: true,
        skippedChecks: true,
        message: '部分密码安全检查被跳过'
      };
    }
  }
  
  /**
   * 检查基本密码策略
   * @private
   * @param {string} password - 密码
   * @param {string} username - 用户名
   * @param {string} email - 电子邮件
   * @returns {Object} 验证结果
   */
  _checkBasicPolicy(password, username, email) {
    // 检查密码长度
    if (password.length < this.minLength) {
      return {
        valid: false,
        message: `密码长度不能少于${this.minLength}个字符`
      };
    }
    
    // 检查是否包含小写字母
    if (this.requireLowercase && !/[a-z]/.test(password)) {
      return {
        valid: false,
        message: '密码必须包含小写字母'
      };
    }
    
    // 检查是否包含大写字母
    if (this.requireUppercase && !/[A-Z]/.test(password)) {
      return {
        valid: false,
        message: '密码必须包含大写字母'
      };
    }
    
    // 检查是否包含数字
    if (this.requireNumbers && !/\d/.test(password)) {
      return {
        valid: false,
        message: '密码必须包含数字'
      };
    }
    
    // 检查是否包含特殊字符
    if (this.requireSpecialChars && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/.test(password)) {
      return {
        valid: false,
        message: '密码必须包含特殊字符'
      };
    }
    
    // 检查重复字符
    if (this._hasRepeatingCharacters(password, this.maxRepeatingChars)) {
      return {
        valid: false,
        message: `密码不能包含${this.maxRepeatingChars}个以上连续重复的字符`
      };
    }
    
    // 检查密码中是否包含用户名
    if (username && password.toLowerCase().includes(username.toLowerCase())) {
      return {
        valid: false,
        message: '密码不能包含用户名'
      };
    }
    
    // 检查密码中是否包含电子邮件
    if (email) {
      const emailName = email.split('@')[0];
      if (password.toLowerCase().includes(emailName.toLowerCase())) {
        return {
          valid: false,
          message: '密码不能包含电子邮件地址的用户名部分'
        };
      }
    }
    
    return {
      valid: true
    };
  }
  
  /**
   * 检查是否有连续重复字符
   * @private
   * @param {string} password - 密码
   * @param {number} maxRepeats - 最大重复次数
   * @returns {boolean} 是否有连续重复字符
   */
  _hasRepeatingCharacters(password, maxRepeats) {
    let count = 1;
    let prevChar = '';
    
    for (let i = 0; i < password.length; i++) {
      const char = password[i];
      
      if (char === prevChar) {
        count++;
        if (count > maxRepeats) {
          return true;
        }
      } else {
        count = 1;
        prevChar = char;
      }
    }
    
    return false;
  }
  
  /**
   * 检查是否是常见密码
   * @private
   * @param {string} password - 密码
   * @returns {boolean} 是否是常见密码
   */
  _isCommonPassword(password) {
    const normalizedPassword = password.toLowerCase();
    
    // 检查常见密码列表
    if (this.commonPasswords.has(normalizedPassword)) {
      return true;
    }
    
    // 检查键盘序列密码
    const keyboardSequences = [
      'qwertyuiop', 'asdfghjkl', 'zxcvbnm', // 横向
      'qazwsx', 'wsxedc', 'edcrfv', 'rfvtgb', 'tgbyhn', 'yhnujm', // 纵向
      '1qaz', '2wsx', '3edc', '4rfv', '5tgb', '6yhn', '7ujm', '8ik,', '9ol.', '0p;/' // 斜向
    ];
    
    for (const seq of keyboardSequences) {
      if (normalizedPassword.includes(seq) || normalizedPassword.includes([...seq].reverse().join(''))) {
        return true;
      }
    }
    
    // 检查数字序列
    const numSequences = ['123456', '654321', '123123', '456456', '789789', '987654321'];
    for (const seq of numSequences) {
      if (normalizedPassword.includes(seq)) {
        return true;
      }
    }
    
    return false;
  }
  
  /**
   * 检查是否是泄露密码
   * @private
   * @param {string} password - 密码
   * @returns {Promise<Object>} 验证结果
   */
  async _checkBreachedPassword(password) {
    try {
      // 计算密码的SHA-1哈希
      const hash = crypto.createHash('sha1').update(password).digest('hex').toUpperCase();
      const prefix = hash.substring(0, 5);
      const suffix = hash.substring(5);
      
      // 检查缓存
      if (this.cacheResults) {
        const cacheKey = `pwned:${prefix}`;
        const cachedResult = this.breachedCache.get(cacheKey);
        
        if (cachedResult && cachedResult.expires > Date.now()) {
          // 如果缓存中包含该密码后缀，则表示密码已泄露
          return {
            valid: !cachedResult.hashes.includes(suffix),
            message: '此密码已在数据泄露中出现，请使用其他密码',
            occurrences: cachedResult.occurrences[suffix] || 0
          };
        }
      }
      
      // 调用API检查
      const response = await axios.get(`${this.apiEndpoint}${prefix}`);
      const data = response.data;
      
      // 解析响应
      const hashes = [];
      const occurrences = {};
      
      if (data) {
        const lines = data.split('\n');
        for (const line of lines) {
          if (line.includes(':')) {
            const [hashSuffix, count] = line.split(':');
            hashes.push(hashSuffix);
            occurrences[hashSuffix] = parseInt(count.trim());
          }
        }
      }
      
      // 更新缓存
      if (this.cacheResults) {
        const cacheKey = `pwned:${prefix}`;
        this.breachedCache.set(cacheKey, {
          expires: Date.now() + this.cacheTTL * 1000,
          hashes,
          occurrences
        });
      }
      
      // 检查密码是否出现在泄露数据中
      const isPwned = hashes.includes(suffix);
      
      return {
        valid: !isPwned,
        message: isPwned ? '此密码已在数据泄露中出现，请使用其他密码' : '密码未在已知泄露中出现',
        occurrences: isPwned ? occurrences[suffix] : 0
      };
    } catch (error) {
      logger.debug(`密码泄露检查失败: ${error.message}`);
      
      // 如果API调用失败，我们默认密码是有效的，但记录跳过了检查
      return {
        valid: true,
        skippedChecks: true,
        message: '密码泄露检查已跳过'
      };
    }
  }
}

// 单例模式
const passwordPolicyChecker = new PasswordPolicyChecker();

/**
 * 创建密码验证中间件
 * @param {Object} options - 选项
 * @param {string} options.field - 密码字段名
 * @param {string} [options.usernameField] - 用户名字段名
 * @param {string} [options.emailField] - 电子邮件字段名
 * @returns {Function} Express中间件函数
 */
function validatePasswordMiddleware(options = {}) {
  const field = options.field || 'password';
  const usernameField = options.usernameField || 'username';
  const emailField = options.emailField || 'email';
  
  return async (req, res, next) => {
    try {
      const password = req.body[field];
      
      if (!password) {
        return next();
      }
      
      const username = req.body[usernameField] || '';
      const email = req.body[emailField] || '';
      
      const result = await passwordPolicyChecker.validatePassword(password, username, email);
      
      if (!result.valid) {
        return next(new ValidationError(result.message));
      }
      
      next();
    } catch (error) {
      next(error);
    }
  };
}

module.exports = {
  passwordPolicyChecker,
  validatePasswordMiddleware
}; 