/**
 * 加密工具模块
 * 提供数据加密和解密功能
 */
const crypto = require('crypto');
const config = require('../config');
const { logger } = require('./logger');

// 加密密钥和初始化向量
const ENCRYPTION_KEY = config.security.encryptionKey;
const IV_LENGTH = 16;

/**
 * 加密数据
 * @param {string} text - 要加密的文本
 * @returns {string} - 加密后的文本
 */
const encrypt = async (text) => {
  if (!text) return text;
  
  try {
    // 生成随机初始化向量
    const iv = crypto.randomBytes(IV_LENGTH);
    
    // 创建加密器
    const cipher = crypto.createCipheriv(
      'aes-256-cbc', 
      Buffer.from(ENCRYPTION_KEY), 
      iv
    );
    
    // 加密数据
    let encrypted = cipher.update(text.toString(), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    // 返回IV和加密数据的组合
    return `${iv.toString('hex')}:${encrypted}`;
  } catch (error) {
    logger.error('加密数据失败', { error: error.message });
    throw new Error('加密失败');
  }
};

/**
 * 解密数据
 * @param {string} text - 要解密的文本
 * @returns {string} - 解密后的文本
 */
const decrypt = async (text) => {
  if (!text) return text;
  
  try {
    // 分离IV和加密数据
    const parts = text.split(':');
    if (parts.length !== 2) {
      throw new Error('无效的加密格式');
    }
    
    const iv = Buffer.from(parts[0], 'hex');
    const encryptedText = parts[1];
    
    // 创建解密器
    const decipher = crypto.createDecipheriv(
      'aes-256-cbc', 
      Buffer.from(ENCRYPTION_KEY), 
      iv
    );
    
    // 解密数据
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  } catch (error) {
    logger.error('解密数据失败', { error: error.message });
    throw new Error('解密失败');
  }
};

/**
 * 批量加密对象中的指定字段
 * @param {Object} data - 要处理的数据对象
 * @param {Array<string>} fields - 要加密的字段数组
 * @returns {Object} - 处理后的数据对象
 */
const encryptFields = async (data, fields) => {
  if (!data || !fields || !Array.isArray(fields)) {
    return data;
  }
  
  const result = { ...data };
  
  for (const field of fields) {
    if (result[field]) {
      result[field] = await encrypt(result[field]);
    }
  }
  
  return result;
};

/**
 * 批量解密对象中的指定字段
 * @param {Object} data - 要处理的数据对象
 * @param {Array<string>} fields - 要解密的字段数组
 * @returns {Object} - 处理后的数据对象
 */
const decryptFields = async (data, fields) => {
  if (!data || !fields || !Array.isArray(fields)) {
    return data;
  }
  
  const result = { ...data };
  
  for (const field of fields) {
    if (result[field]) {
      result[field] = await decrypt(result[field]);
    }
  }
  
  return result;
};

/**
 * 批量加密数组中每个对象的指定字段
 * @param {Array<Object>} items - 要处理的数据对象数组
 * @param {Array<string>} fields - 要加密的字段数组
 * @returns {Array<Object>} - 处理后的数据对象数组
 */
const encryptFieldsInArray = async (items, fields) => {
  if (!items || !Array.isArray(items) || !fields || !Array.isArray(fields)) {
    return items;
  }
  
  const result = [];
  
  for (const item of items) {
    result.push(await encryptFields(item, fields));
  }
  
  return result;
};

/**
 * 批量解密数组中每个对象的指定字段
 * @param {Array<Object>} items - 要处理的数据对象数组
 * @param {Array<string>} fields - 要解密的字段数组
 * @returns {Array<Object>} - 处理后的数据对象数组
 */
const decryptFieldsInArray = async (items, fields) => {
  if (!items || !Array.isArray(items) || !fields || !Array.isArray(fields)) {
    return items;
  }
  
  const result = [];
  
  for (const item of items) {
    result.push(await decryptFields(item, fields));
  }
  
  return result;
};

/**
 * 生成哈希值
 * @param {string} text - 要哈希的文本
 * @param {string} salt - 盐值，默认使用配置中的值
 * @returns {string} - 哈希后的文本
 */
const hash = (text, salt = config.security.hashSalt) => {
  if (!text) return text;
  
  try {
    return crypto
      .createHmac('sha256', salt)
      .update(text)
      .digest('hex');
  } catch (error) {
    logger.error('生成哈希值失败', { error: error.message });
    throw new Error('哈希生成失败');
  }
};

/**
 * 生成安全的随机令牌
 * @param {number} length - 令牌长度，默认32
 * @returns {string} - 生成的令牌
 */
const generateToken = (length = 32) => {
  return crypto.randomBytes(length).toString('hex');
};

/**
 * 生成密码哈希
 * @param {string} password - 原始密码
 * @returns {string} - 哈希后的密码
 */
const hashPassword = async (password) => {
  if (!password) {
    throw new Error('密码不能为空');
  }
  
  // 生成随机盐
  const salt = crypto.randomBytes(16).toString('hex');
  
  // 使用PBKDF2算法生成哈希
  return new Promise((resolve, reject) => {
    crypto.pbkdf2(
      password, 
      salt, 
      10000, // 迭代次数
      64,    // 密钥长度
      'sha512', 
      (err, derivedKey) => {
        if (err) {
          logger.error('密码哈希生成失败', { error: err.message });
          reject(new Error('密码哈希生成失败'));
        } else {
          // 格式: 算法:迭代次数:盐:哈希
          resolve(`pbkdf2:10000:${salt}:${derivedKey.toString('hex')}`);
        }
      }
    );
  });
};

/**
 * 验证密码
 * @param {string} password - 要验证的密码
 * @param {string} hashedPassword - 存储的哈希密码
 * @returns {Promise<boolean>} - 密码是否匹配
 */
const verifyPassword = async (password, hashedPassword) => {
  if (!password || !hashedPassword) {
    return false;
  }
  
  try {
    // 解析存储的哈希密码
    const [algorithm, iterations, salt, hash] = hashedPassword.split(':');
    
    if (algorithm !== 'pbkdf2' || !iterations || !salt || !hash) {
      throw new Error('无效的哈希密码格式');
    }
    
    // 使用相同参数重新计算哈希
    return new Promise((resolve, reject) => {
      crypto.pbkdf2(
        password, 
        salt, 
        parseInt(iterations, 10), 
        64, 
        'sha512', 
        (err, derivedKey) => {
          if (err) {
            logger.error('密码验证失败', { error: err.message });
            reject(new Error('密码验证失败'));
          } else {
            // 比较哈希值
            resolve(derivedKey.toString('hex') === hash);
          }
        }
      );
    });
  } catch (error) {
    logger.error('密码验证失败', { error: error.message });
    return false;
  }
};

module.exports = {
  encrypt,
  decrypt,
  encryptFields,
  decryptFields,
  encryptFieldsInArray,
  decryptFieldsInArray,
  hash,
  generateToken,
  hashPassword,
  verifyPassword
}; 