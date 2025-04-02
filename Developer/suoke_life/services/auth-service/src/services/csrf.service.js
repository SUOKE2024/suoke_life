/**
 * CSRF保护服务
 * 提供跨站请求伪造防护功能
 */
const crypto = require('crypto');
const { HttpError } = require('@suoke/shared').errors;
const redisClient = require('../utils/redis');
const logger = require('../utils/logger');

/**
 * CSRF令牌过期时间（秒）
 */
const TOKEN_EXPIRY = 3600; // 1小时

/**
 * CSRF令牌Redis前缀
 */
const REDIS_PREFIX = 'csrf:';

/**
 * Safari浏览器CSRF令牌Redis前缀
 */
const SAFARI_REDIS_PREFIX = 'csrf:safari:';

/**
 * CSRF保护服务类
 */
class CSRFService {
  /**
   * 生成CSRF令牌
   * @param {string} sessionId 会话ID
   * @returns {Promise<string>} CSRF令牌
   */
  async generateToken(sessionId) {
    try {
      // 生成随机令牌
      const token = crypto.randomBytes(32).toString('hex');
      
      // 存储令牌与会话的关联
      const key = `${REDIS_PREFIX}${token}`;
      await redisClient.set(key, sessionId, 'EX', TOKEN_EXPIRY);
      
      return token;
    } catch (error) {
      logger.error(`生成CSRF令牌错误: ${error.message}`);
      throw new HttpError(500, '生成CSRF令牌失败');
    }
  }
  
  /**
   * 验证CSRF令牌
   * @param {string} token CSRF令牌
   * @param {string} sessionId 会话ID
   * @returns {Promise<boolean>} 是否有效
   */
  async validateToken(token, sessionId) {
    try {
      if (!token || !sessionId) {
        return false;
      }
      
      // 获取令牌关联的会话
      const key = `${REDIS_PREFIX}${token}`;
      const storedSessionId = await redisClient.get(key);
      
      // 验证令牌是否与当前会话匹配
      return storedSessionId === sessionId;
    } catch (error) {
      logger.error(`验证CSRF令牌错误: ${error.message}`);
      return false;
    }
  }

  /**
   * 验证Safari浏览器CSRF令牌
   * @param {string} token CSRF令牌
   * @param {string} sessionId 会话ID
   * @returns {Promise<boolean>} 是否有效
   */
  async validateTokenSafari(token, sessionId) {
    try {
      if (!token || !sessionId) {
        return false;
      }
      
      // 首先尝试标准验证
      const standardValidation = await this.validateToken(token, sessionId);
      if (standardValidation) {
        return true;
      }
      
      // 如果标准验证失败，尝试Safari特定验证
      const key = `${SAFARI_REDIS_PREFIX}${token}`;
      const storedSessionId = await redisClient.get(key);
      
      // 验证令牌是否与当前会话匹配
      const isValid = storedSessionId === sessionId;
      
      // 如果令牌有效，但存储在Safari专用命名空间下，则更新令牌以同步两种验证机制
      if (isValid) {
        const standardKey = `${REDIS_PREFIX}${token}`;
        await redisClient.set(standardKey, sessionId, 'EX', TOKEN_EXPIRY);
      }
      
      return isValid;
    } catch (error) {
      logger.error(`验证Safari CSRF令牌错误: ${error.message}`);
      return false;
    }
  }
  
  /**
   * 使令牌失效
   * @param {string} token CSRF令牌
   * @returns {Promise<void>}
   */
  async invalidateToken(token) {
    try {
      if (!token) return;
      
      // 删除令牌(同时删除标准和Safari命名空间下的令牌)
      const standardKey = `${REDIS_PREFIX}${token}`;
      const safariKey = `${SAFARI_REDIS_PREFIX}${token}`;
      
      await Promise.all([
        redisClient.del(standardKey),
        redisClient.del(safariKey)
      ]);
    } catch (error) {
      logger.error(`使CSRF令牌失效错误: ${error.message}`);
      // 不抛出异常，因为令牌失效是一种清理操作
    }
  }
  
  /**
   * 获取CSRF Cookie配置
   * @param {Object} req 请求对象
   * @returns {Object} Cookie配置
   */
  getCookieConfig(req) {
    // 检测是否是Safari浏览器
    const userAgent = req.headers['user-agent'] || '';
    const isSafari = userAgent.includes('Safari') && !userAgent.includes('Chrome');
    
    // 基本配置
    const config = {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: TOKEN_EXPIRY * 1000
    };
    
    // 为Safari浏览器调整SameSite策略
    if (isSafari) {
      // Safari对None值处理不一致，使用Lax策略能更好兼容
      config.sameSite = 'Lax';
    } else {
      // 对其他浏览器使用更严格的策略
      config.sameSite = process.env.NODE_ENV === 'production' ? 'None' : 'Lax';
    }
    
    // 开发环境下路径处理
    if (process.env.NODE_ENV !== 'production') {
      config.path = '/';
    }
    
    return config;
  }
  
  /**
   * 获取Safari专用的Cookie配置
   * @param {Object} req 请求对象
   * @returns {Object} Cookie配置
   */
  getSafariCookieConfig(req) {
    const config = {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: TOKEN_EXPIRY * 1000,
      // Safari浏览器最兼容的设置
      sameSite: 'Lax',
      path: '/'
    };
    
    return config;
  }
  
  /**
   * 设置CSRF Cookie
   * @param {Object} req 请求对象
   * @param {Object} res 响应对象
   * @param {string} token CSRF令牌
   */
  setCookie(req, res, token) {
    const cookieConfig = this.getCookieConfig(req);
    res.cookie('csrf_token', token, cookieConfig);
  }

  /**
   * 为Safari浏览器设置CSRF Cookie
   * @param {Object} req 请求对象
   * @param {Object} res 响应对象
   * @param {string} token CSRF令牌
   */
  async setCookieSafari(req, res, token) {
    try {
      // 存储令牌与会话的关联(在Safari专用命名空间)
      const sessionId = req.session?.id;
      if (sessionId) {
        const key = `${SAFARI_REDIS_PREFIX}${token}`;
        await redisClient.set(key, sessionId, 'EX', TOKEN_EXPIRY);
      }
      
      // 设置Safari专用Cookie配置
      const cookieConfig = this.getSafariCookieConfig(req);
      res.cookie('csrf_token', token, cookieConfig);
    } catch (error) {
      logger.error(`设置Safari CSRF Cookie错误: ${error.message}`);
      // 继续处理而不抛出异常，以便用户仍可使用系统
    }
  }
}

module.exports = new CSRFService(); 