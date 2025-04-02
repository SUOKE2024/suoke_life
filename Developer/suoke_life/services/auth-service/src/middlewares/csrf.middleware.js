/**
 * CSRF保护中间件
 * 提供跨站请求伪造防护功能
 */
const csrfService = require('../services/csrf.service');
const logger = require('../utils/logger');
const crypto = require('crypto');

/**
 * CSRF保护中间件配置
 */
const csrfOptions = {
  // 排除的路径
  excludedPaths: [
    '/health',
    '/metrics',
    '/auth/login',
    '/auth/register',
    '/auth/refresh',
    '/auth/logout'
  ],
  // 排除的HTTP方法
  excludedMethods: ['GET', 'HEAD', 'OPTIONS'],
  // 令牌来源
  tokenSources: ['header', 'cookie', 'body'],
  headerName: 'X-CSRF-Token',
  cookieName: 'csrf_token',
  bodyName: '_csrf'
};

// CSRF令牌密钥
const CSRF_SECRET = process.env.CSRF_SECRET || 'suoke-csrf-secret-key';

// 令牌过期时间（1小时）
const TOKEN_EXPIRY = 60 * 60 * 1000;

// 不需要CSRF保护的HTTP方法
const SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS'];

/**
 * 从请求中提取CSRF令牌
 * @param {Object} req 请求对象
 * @returns {string|null} CSRF令牌
 */
function extractToken(req) {
  for (const source of csrfOptions.tokenSources) {
    switch (source) {
      case 'header':
        if (req.headers[csrfOptions.headerName.toLowerCase()]) {
          return req.headers[csrfOptions.headerName.toLowerCase()];
        }
        break;
      case 'cookie':
        if (req.cookies && req.cookies[csrfOptions.cookieName]) {
          return req.cookies[csrfOptions.cookieName];
        }
        break;
      case 'body':
        if (req.body && req.body[csrfOptions.bodyName]) {
          return req.body[csrfOptions.bodyName];
        }
        break;
    }
  }
  return null;
}

/**
 * 检查请求是否应该排除CSRF检查
 * @param {Object} req 请求对象
 * @returns {boolean} 是否排除
 */
function shouldExclude(req) {
  // 排除指定HTTP方法
  if (csrfOptions.excludedMethods.includes(req.method)) {
    return true;
  }
  
  // 排除指定路径
  for (const path of csrfOptions.excludedPaths) {
    if (req.path.startsWith(path)) {
      return true;
    }
  }
  
  return false;
}

/**
 * 检测浏览器类型
 * @param {Object} req 请求对象
 * @returns {string} 浏览器类型
 */
function detectBrowser(req) {
  const userAgent = req.headers['user-agent'] || '';
  
  if (userAgent.includes('Safari') && !userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
    return 'safari';
  } else if (userAgent.includes('Firefox')) {
    return 'firefox';
  } else if (userAgent.includes('Chrome')) {
    return 'chrome';
  } else if (userAgent.includes('Edg') || userAgent.includes('Edge')) {
    return 'edge';
  } else {
    return 'other';
  }
}

/**
 * CSRF保护中间件
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
async function csrfProtection(req, res, next) {
  try {
    // 检查请求是否应该排除CSRF检查
    if (shouldExclude(req)) {
      return next();
    }
    
    // 从会话中获取用户ID
    const sessionId = req.session?.id;
    
    // 如果请求不包含会话，则跳过CSRF检查
    if (!sessionId) {
      return next();
    }
    
    // 从请求中提取CSRF令牌
    const token = extractToken(req);
    
    // 如果请求不包含令牌，则返回403错误
    if (!token) {
      logger.warn(`CSRF验证失败: 请求不包含CSRF令牌 [${req.method} ${req.path}]`);
      return res.status(403).json({
        success: false,
        message: '缺少CSRF令牌',
        code: 'security/missing-csrf-token'
      });
    }
    
    // 浏览器检测
    const browser = detectBrowser(req);
    
    // 验证CSRF令牌，为Safari浏览器提供特殊处理
    const isValid = browser === 'safari' 
      ? await csrfService.validateTokenSafari(token, sessionId)
      : await csrfService.validateToken(token, sessionId);
    
    // 如果令牌无效，则返回403错误
    if (!isValid) {
      logger.warn(`CSRF验证失败: 无效的CSRF令牌 [${req.method} ${req.path}] (浏览器: ${browser})`);
      return res.status(403).json({
        success: false,
        message: '无效的CSRF令牌',
        code: 'security/invalid-csrf-token'
      });
    }
    
    // 继续处理请求
    next();
  } catch (error) {
    // 记录错误
    logger.error(`CSRF中间件错误: ${error.message}`);
    next(error);
  }
}

/**
 * 生成CSRF令牌并添加到响应对象的Cookie
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
async function csrfTokenGenerator(req, res, next) {
  try {
    // 如果请求中已包含CSRF令牌，则不生成新令牌
    if (extractToken(req)) {
      return next();
    }
    
    // 从会话中获取用户ID
    const sessionId = req.session?.id;
    
    // 如果请求不包含会话，则跳过生成令牌
    if (!sessionId) {
      return next();
    }
    
    // 浏览器检测
    const browser = detectBrowser(req);
    
    // 生成新的CSRF令牌
    const token = await csrfService.generateToken(sessionId);
    
    // 将令牌添加到响应的Cookie，为Safari提供特殊处理
    if (browser === 'safari') {
      csrfService.setCookieSafari(req, res, token);
    } else {
      csrfService.setCookie(req, res, token);
    }
    
    // 为客户端提供获取CSRF令牌的方法
    res.locals.csrfToken = token;
    
    // 继续处理请求
    next();
  } catch (error) {
    // 记录错误
    logger.error(`CSRF令牌生成错误: ${error.message}`);
    next(error);
  }
}

/**
 * 生成CSRF令牌
 * @param {string} sessionId - 会话ID
 * @returns {string} CSRF令牌
 */
const generateCsrfToken = (sessionId) => {
  // 创建当前时间戳
  const timestamp = Date.now().toString();
  
  // 创建HMAC
  const hmac = crypto.createHmac('sha256', CSRF_SECRET);
  hmac.update(`${sessionId}:${timestamp}`);
  const hash = hmac.digest('hex');
  
  // 返回时间戳与哈希的组合
  return `${timestamp}:${hash}`;
};

/**
 * 验证CSRF令牌
 * @param {string} token - CSRF令牌
 * @param {string} sessionId - 会话ID
 * @returns {boolean} 是否有效
 */
const validateCsrfToken = (token, sessionId) => {
  try {
    // 解析令牌
    const parts = token.split(':');
    if (parts.length !== 2) {
      return false;
    }
    
    const [timestamp, hash] = parts;
    
    // 检查令牌是否过期
    const tokenTime = parseInt(timestamp, 10);
    const now = Date.now();
    if (now - tokenTime > TOKEN_EXPIRY) {
      return false;
    }
    
    // 重新计算哈希并验证
    const hmac = crypto.createHmac('sha256', CSRF_SECRET);
    hmac.update(`${sessionId}:${timestamp}`);
    const expectedHash = hmac.digest('hex');
    
    return crypto.timingSafeEqual(
      Buffer.from(hash, 'hex'),
      Buffer.from(expectedHash, 'hex')
    );
  } catch (error) {
    logger.error('CSRF令牌验证失败', { error: error.message });
    return false;
  }
};

/**
 * CSRF令牌生成中间件
 * 为每个请求生成CSRF令牌并添加到响应头
 */
const csrfTokenGeneratorNew = (req, res, next) => {
  // 确保会话已初始化
  if (!req.session) {
    return next(new Error('会话中间件未正确配置'));
  }
  
  // 生成新的CSRF令牌
  const token = generateCsrfToken(req.session.id);
  
  // 将令牌存储在会话中
  req.session.csrfToken = token;
  
  // 添加令牌到响应头
  res.setHeader('X-CSRF-Token', token);
  
  // 添加生成令牌的便捷方法到请求对象
  req.csrfToken = () => token;
  
  next();
};

/**
 * CSRF保护中间件
 * 验证请求中的CSRF令牌
 */
const csrfProtectionNew = (req, res, next) => {
  // 对安全的HTTP方法不进行CSRF保护
  if (SAFE_METHODS.includes(req.method)) {
    return next();
  }
  
  // 确保会话已初始化
  if (!req.session) {
    return next(new Error('会话中间件未正确配置'));
  }
  
  // 从请求中获取令牌
  const token = 
    req.headers['x-csrf-token'] || 
    req.headers['x-xsrf-token'] || 
    req.body._csrf;
  
  // 如果没有令牌，拒绝请求
  if (!token) {
    logger.warn('CSRF验证失败: 缺少令牌', {
      method: req.method,
      url: req.originalUrl,
      ip: req.ip
    });
    
    return res.status(403).json({
      success: false,
      message: 'CSRF验证失败',
      code: 'csrf_validation_failed'
    });
  }
  
  // 从会话中获取存储的令牌
  const storedToken = req.session.csrfToken;
  
  // 如果没有存储的令牌，拒绝请求
  if (!storedToken) {
    logger.warn('CSRF验证失败: 会话中无令牌', {
      method: req.method,
      url: req.originalUrl,
      ip: req.ip
    });
    
    return res.status(403).json({
      success: false,
      message: 'CSRF会话无效',
      code: 'csrf_session_invalid'
    });
  }
  
  // 验证令牌
  if (!validateCsrfToken(token, req.session.id)) {
    logger.warn('CSRF验证失败: 令牌无效', {
      method: req.method,
      url: req.originalUrl,
      ip: req.ip
    });
    
    return res.status(403).json({
      success: false,
      message: 'CSRF令牌无效',
      code: 'csrf_token_invalid'
    });
  }
  
  // 令牌有效，继续
  next();
};

module.exports = {
  csrfProtection,
  csrfTokenGenerator,
  csrfTokenGeneratorNew,
  csrfProtectionNew,
  generateCsrfToken
}; 