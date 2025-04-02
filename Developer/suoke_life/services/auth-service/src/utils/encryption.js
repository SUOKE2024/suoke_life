/**
 * 数据加密工具模块
 * 用于敏感数据的加密和解密
 */
const crypto = require('crypto');
const { logger } = require('@suoke/shared').utils;
const config = require('../config');

// 加密配置
const ALGORITHM = process.env.SENSITIVE_DATA_ENCRYPTION_ALGORITHM || 'AES-256-GCM';
let encryptionKey = null;
let previousEncryptionKey = null;
let iv = null;

/**
 * 初始化加密组件
 * @returns {Promise<boolean>} 初始化是否成功
 */
const initialize = async () => {
  try {
    // 检查是否启用了加密
    if (process.env.APP_ENCRYPTION_ENABLED !== 'true') {
      logger.info('数据加密功能未启用');
      return false;
    }
    
    // 从环境变量或KMS加载密钥
    await loadEncryptionKeys();
    
    // 生成随机初始化向量
    iv = crypto.randomBytes(16);
    
    logger.info(`数据加密组件已初始化，算法: ${ALGORITHM}`);
    return true;
  } catch (error) {
    logger.error(`数据加密组件初始化失败: ${error.message}`);
    throw error;
  }
};

/**
 * 加载加密密钥
 * 从环境变量或KMS加载主密钥和前一个密钥
 * @returns {Promise<void>}
 */
const loadEncryptionKeys = async () => {
  try {
    // 尝试从环境变量加载
    if (process.env.ENCRYPTION_KEY) {
      // 将Base64编码的密钥转换为Buffer
      encryptionKey = Buffer.from(process.env.ENCRYPTION_KEY, 'base64');
      logger.info('从环境变量加载了加密密钥');
    } else {
      // 生成随机密钥
      encryptionKey = crypto.randomBytes(32); // 256位密钥
      logger.info('生成了随机加密密钥');
    }
    
    // 尝试加载前一个密钥（用于轮换）
    if (process.env.ENCRYPTION_KEY_PREVIOUS) {
      previousEncryptionKey = Buffer.from(process.env.ENCRYPTION_KEY_PREVIOUS, 'base64');
      logger.info('从环境变量加载了前一个加密密钥');
    }
  } catch (error) {
    logger.error(`加载加密密钥失败: ${error.message}`);
    throw error;
  }
};

/**
 * 加密敏感数据
 * @param {string} text 要加密的文本
 * @returns {string} 加密后的Base64字符串，格式为 iv:authTag:encryptedData
 */
const encrypt = (text) => {
  if (!encryptionKey || !iv || process.env.APP_ENCRYPTION_ENABLED !== 'true') {
    return text;
  }
  
  try {
    // 创建加密器
    const cipher = crypto.createCipheriv(ALGORITHM, encryptionKey, iv);
    
    // 加密数据
    let encrypted = cipher.update(text, 'utf8', 'base64');
    encrypted += cipher.final('base64');
    
    // 获取认证标签 (GCM模式)
    const authTag = cipher.getAuthTag().toString('base64');
    
    // 组合IV、认证标签和加密数据
    return `${iv.toString('base64')}:${authTag}:${encrypted}`;
  } catch (error) {
    logger.error(`加密数据失败: ${error.message}`);
    return text; // 失败时返回原文，避免数据丢失
  }
};

/**
 * 解密敏感数据
 * @param {string} encryptedText 格式为 iv:authTag:encryptedData 的加密文本
 * @returns {string} 解密后的文本
 */
const decrypt = (encryptedText) => {
  if (!encryptedText || !encryptionKey || process.env.APP_ENCRYPTION_ENABLED !== 'true') {
    return encryptedText;
  }
  
  try {
    // 分解加密文本
    const parts = encryptedText.split(':');
    if (parts.length !== 3) {
      return encryptedText; // 格式不正确，返回原文
    }
    
    const ivString = parts[0];
    const authTagString = parts[1];
    const encryptedData = parts[2];
    
    // 转换为Buffer
    const ivBuffer = Buffer.from(ivString, 'base64');
    const authTagBuffer = Buffer.from(authTagString, 'base64');
    
    // 创建解密器
    const decipher = crypto.createDecipheriv(ALGORITHM, encryptionKey, ivBuffer);
    decipher.setAuthTag(authTagBuffer);
    
    // 解密数据
    let decrypted = decipher.update(encryptedData, 'base64', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  } catch (error) {
    // 尝试使用前一个密钥解密（密钥轮换场景）
    if (previousEncryptionKey) {
      try {
        const parts = encryptedText.split(':');
        const ivBuffer = Buffer.from(parts[0], 'base64');
        const authTagBuffer = Buffer.from(parts[1], 'base64');
        const encryptedData = parts[2];
        
        const decipher = crypto.createDecipheriv(ALGORITHM, previousEncryptionKey, ivBuffer);
        decipher.setAuthTag(authTagBuffer);
        
        let decrypted = decipher.update(encryptedData, 'base64', 'utf8');
        decrypted += decipher.final('utf8');
        
        // 成功解密，记录密钥轮换使用情况
        logger.info('使用前一个密钥成功解密数据');
        
        // 使用新密钥重新加密（透明重加密）
        return decrypted;
      } catch (innerError) {
        logger.error(`使用当前密钥和前一个密钥都无法解密: ${innerError.message}`);
      }
    }
    
    logger.error(`解密数据失败: ${error.message}`);
    return encryptedText; // 解密失败，返回原文
  }
};

/**
 * 加密对象中的敏感字段
 * @param {Object} data 要处理的数据对象
 * @param {Array<string>} sensitiveFields 需要加密的敏感字段列表
 * @returns {Object} 处理后的对象
 */
const encryptSensitiveData = (data, sensitiveFields) => {
  if (!data || typeof data !== 'object' || !sensitiveFields || !Array.isArray(sensitiveFields)) {
    return data;
  }
  
  const result = { ...data };
  
  for (const field of sensitiveFields) {
    if (result[field] && typeof result[field] === 'string') {
      result[field] = encrypt(result[field]);
    }
  }
  
  return result;
};

/**
 * 解密对象中的敏感字段
 * @param {Object} data 要处理的数据对象
 * @param {Array<string>} sensitiveFields 需要解密的敏感字段列表
 * @returns {Object} 处理后的对象
 */
const decryptSensitiveData = (data, sensitiveFields) => {
  if (!data || typeof data !== 'object' || !sensitiveFields || !Array.isArray(sensitiveFields)) {
    return data;
  }
  
  const result = { ...data };
  
  for (const field of sensitiveFields) {
    if (result[field] && typeof result[field] === 'string') {
      result[field] = decrypt(result[field]);
    }
  }
  
  return result;
};

/**
 * 获取基于当前密钥的哈希值
 * 用于数据完整性校验
 * @param {string} data 要哈希的数据
 * @returns {string} 哈希值
 */
const getIntegrityHash = (data) => {
  if (!encryptionKey || !data) {
    return null;
  }
  
  const hmac = crypto.createHmac('sha256', encryptionKey);
  hmac.update(data);
  return hmac.digest('hex');
};

/**
 * 验证数据完整性
 * @param {string} data 数据
 * @param {string} hash 原始哈希值
 * @returns {boolean} 是否一致
 */
const verifyIntegrity = (data, hash) => {
  const calculatedHash = getIntegrityHash(data);
  return calculatedHash === hash;
};

/**
 * 创建自定义加密中间件
 * 用于自动加密/解密请求和响应中的敏感字段
 * @param {Array<string>} requestFields 请求中需要处理的字段
 * @param {Array<string>} responseFields 响应中需要处理的字段
 * @returns {Function} Express中间件
 */
const createEncryptionMiddleware = (requestFields = [], responseFields = []) => {
  return (req, res, next) => {
    if (process.env.APP_ENCRYPTION_ENABLED !== 'true') {
      return next();
    }
    
    // 拦截原始的json方法
    const originalJson = res.json;
    
    // 处理请求体中的敏感数据
    if (req.body && requestFields.length > 0) {
      req.body = decryptSensitiveData(req.body, requestFields);
    }
    
    // 重写json方法以处理响应数据
    res.json = function(data) {
      let processedData = data;
      
      // 处理响应中的敏感数据
      if (data && responseFields.length > 0) {
        processedData = encryptSensitiveData(data, responseFields);
      }
      
      return originalJson.call(this, processedData);
    };
    
    next();
  };
};

module.exports = {
  initialize,
  encrypt,
  decrypt,
  encryptSensitiveData,
  decryptSensitiveData,
  getIntegrityHash,
  verifyIntegrity,
  createEncryptionMiddleware
}; 