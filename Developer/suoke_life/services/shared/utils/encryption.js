/**
 * 加密工具模块
 * 提供密码哈希、加密和解密功能
 */
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const config = require('../config');

/**
 * 密码哈希处理
 */
const password = {
  /**
   * 生成密码哈希
   * @param {string} password - 原始密码
   * @returns {Promise<string>} 哈希后的密码
   */
  async hash(password) {
    const saltRounds = 10;
    return bcrypt.hash(password, saltRounds);
  },

  /**
   * 验证密码
   * @param {string} password - 原始密码
   * @param {string} hash - 存储的哈希密码
   * @returns {Promise<boolean>} 验证结果
   */
  async verify(password, hash) {
    return bcrypt.compare(password, hash);
  }
};

/**
 * AES加密解密
 */
const aes = {
  /**
   * AES加密
   * @param {string} text - 要加密的文本
   * @param {string} secretKey - 密钥 (默认使用配置中的密钥)
   * @returns {string} 加密后的文本
   */
  encrypt(text, secretKey = config.security.encryptionKey) {
    const iv = crypto.randomBytes(16);
    const key = crypto.createHash('sha256').update(secretKey).digest('base64').substr(0, 32);
    const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(key), iv);
    
    let encrypted = cipher.update(text);
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    
    return iv.toString('hex') + ':' + encrypted.toString('hex');
  },

  /**
   * AES解密
   * @param {string} text - 加密后的文本
   * @param {string} secretKey - 密钥 (默认使用配置中的密钥)
   * @returns {string} 解密后的文本
   */
  decrypt(text, secretKey = config.security.encryptionKey) {
    const textParts = text.split(':');
    const iv = Buffer.from(textParts.shift(), 'hex');
    const encryptedText = Buffer.from(textParts.join(':'), 'hex');
    const key = crypto.createHash('sha256').update(secretKey).digest('base64').substr(0, 32);
    const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(key), iv);
    
    let decrypted = decipher.update(encryptedText);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    
    return decrypted.toString();
  }
};

/**
 * JWT令牌处理
 */
const token = {
  /**
   * 生成JWT令牌
   * @param {Object} payload - 令牌负载
   * @param {Object} options - 令牌选项
   * @returns {string} JWT令牌
   */
  generate(payload, options = {}) {
    const defaultOptions = {
      expiresIn: config.jwt.expiresIn || '1d'
    };
    
    return jwt.sign(
      payload, 
      config.jwt.secret,
      { ...defaultOptions, ...options }
    );
  },

  /**
   * 验证JWT令牌
   * @param {string} token - JWT令牌
   * @returns {Object|null} 验证结果
   */
  verify(token) {
    try {
      return jwt.verify(token, config.jwt.secret);
    } catch (error) {
      return null;
    }
  },

  /**
   * 解码JWT令牌(不验证签名)
   * @param {string} token - JWT令牌
   * @returns {Object|null} 解码结果
   */
  decode(token) {
    try {
      return jwt.decode(token);
    } catch (error) {
      return null;
    }
  }
};

/**
 * 生成随机字符串
 * @param {number} length - 字符串长度
 * @returns {string} 随机字符串
 */
const generateRandomString = (length = 32) => {
  return crypto.randomBytes(length).toString('hex');
};

/**
 * 计算字符串的MD5哈希
 * @param {string} str - 输入字符串
 * @returns {string} MD5哈希
 */
const md5 = (str) => {
  return crypto.createHash('md5').update(str).digest('hex');
};

/**
 * 计算字符串的SHA256哈希
 * @param {string} str - 输入字符串
 * @returns {string} SHA256哈希
 */
const sha256 = (str) => {
  return crypto.createHash('sha256').update(str).digest('hex');
};

module.exports = {
  password,
  aes,
  token,
  generateRandomString,
  md5,
  sha256
}; 