/**
 * 指标中间件
 * 用于收集请求和响应的指标数据
 */
const metricsService = require('../services/metrics.service');
const logger = require('../utils/logger');

// 排除的路径列表 - 这些路径不会被收集指标
const EXCLUDED_PATHS = [
  '/metrics',
  '/health',
  '/health/ready',
  '/health/startup',
  '/favicon.ico'
];

/**
 * 检查是否应该排除该路径的指标收集
 * @param {string} path - 请求路径
 * @returns {boolean} 是否应该排除
 */
const shouldExcludePath = (path) => {
  return EXCLUDED_PATHS.some(excluded => path.startsWith(excluded));
};

/**
 * 异步收集指标
 * 通过将指标收集处理放在异步函数中，避免影响请求处理性能
 * 
 * @param {Object} req - Express请求对象
 * @param {Object} res - Express响应对象
 * @param {number} startTime - 请求开始时间
 * @param {number} statusCode - HTTP状态码
 */
const collectMetricsAsync = async (req, res, startTime, statusCode) => {
  try {
    const duration = Date.now() - startTime;
    const method = req.method;
    const path = req.originalUrl || req.url;
    const contentLength = res.getHeader('content-length') || 0;
    const userAgent = req.headers['user-agent'] || 'unknown';
    const ip = req.ip || req.socket.remoteAddress || 'unknown';
    const browser = getBrowserInfo(userAgent);
    
    // 递增请求计数器
    metricsService.increment('http_requests_total', {
      method,
      status: statusCode,
      path: path.split('?')[0] // 移除查询参数
    });
    
    // 记录请求持续时间
    metricsService.timing('http_request_duration_ms', duration, {
      method,
      status: statusCode,
      path: path.split('?')[0]
    });
    
    // 记录响应大小
    metricsService.observe('http_response_size_bytes', parseInt(contentLength, 10), {
      method,
      status: statusCode
    });
    
    // 用户代理信息
    metricsService.increment('client_requests', {
      browser: browser.name,
      browser_version: browser.version,
      device_type: browser.mobile ? 'mobile' : 'desktop'
    });
    
    // 请求IP信息
    metricsService.increment('client_ip_requests', { ip });
    
    // 如果是4xx或5xx状态码，记录错误
    if (statusCode >= 400) {
      metricsService.increment('http_errors_total', {
        method,
        status: statusCode,
        path: path.split('?')[0]
      });
    }
    
    logger.debug(`指标已收集: ${method} ${path} ${statusCode} ${duration}ms`);
  } catch (error) {
    logger.error('指标收集失败', error);
  }
};

/**
 * 从User-Agent提取浏览器信息
 * @param {string} userAgent - User-Agent字符串
 * @returns {Object} 浏览器信息对象
 */
const getBrowserInfo = (userAgent) => {
  const result = {
    name: 'unknown',
    version: 'unknown',
    mobile: false
  };
  
  try {
    if (!userAgent) return result;
    
    // 检测是否是移动设备
    if (/mobile|android|iphone|ipad|ipod/i.test(userAgent)) {
      result.mobile = true;
    }
    
    // 检测浏览器类型
    if (/chrome/i.test(userAgent)) {
      result.name = 'chrome';
      const match = userAgent.match(/chrome\/(\d+)/i);
      if (match) result.version = match[1];
    } else if (/firefox/i.test(userAgent)) {
      result.name = 'firefox';
      const match = userAgent.match(/firefox\/(\d+)/i);
      if (match) result.version = match[1];
    } else if (/safari/i.test(userAgent) && !/chrome/i.test(userAgent)) {
      result.name = 'safari';
      const match = userAgent.match(/safari\/(\d+)/i);
      if (match) result.version = match[1];
    } else if (/msie|trident/i.test(userAgent)) {
      result.name = 'ie';
      const match = userAgent.match(/(msie |rv:)(\d+)/i);
      if (match) result.version = match[2];
    } else if (/edge/i.test(userAgent)) {
      result.name = 'edge';
      const match = userAgent.match(/edge\/(\d+)/i);
      if (match) result.version = match[1];
    }
  } catch (error) {
    logger.error('解析User-Agent失败', error);
  }
  
  return result;
};

/**
 * 指标中间件
 * 用于收集HTTP请求和响应指标
 * 
 * @param {Object} req - Express请求对象
 * @param {Object} res - Express响应对象
 * @param {Function} next - 下一个中间件函数
 */
const metricsMiddleware = (req, res, next) => {
  // 如果是被排除的路径，直接跳过
  if (shouldExcludePath(req.path)) {
    return next();
  }

  // 记录开始时间
  const startTime = Date.now();
  
  // 增加活跃连接数
  metricsService.gauge('http_active_connections', 
    (metricsService.getMetrics().gauges['http_active_connections'] || 0) + 1
  );
  
  // 原始end方法
  const originalEnd = res.end;
  
  // 重写end方法以收集响应指标
  res.end = function(...args) {
    // 恢复原始end方法并应用
    res.end = originalEnd;
    const result = res.end.apply(this, args);
    
    // 减少活跃连接数
    metricsService.gauge('http_active_connections', 
      Math.max(0, (metricsService.getMetrics().gauges['http_active_connections'] || 1) - 1)
    );
    
    // 异步收集指标，不阻塞响应
    collectMetricsAsync(req, res, startTime, res.statusCode);
    
    return result;
  };
  
  next();
};

/**
 * 获取认证方法
 * @param {Object} req - 请求对象
 * @returns {string} 认证方法
 */
function getAuthMethod(req) {
  const path = req.path.toLowerCase();
  
  if (path.includes('/oauth/')) {
    return 'oauth';
  } else if (path.includes('/sms/')) {
    return 'sms';
  } else if (path.includes('/phone/')) {
    return 'phone';
  } else if (path.includes('/refresh-token')) {
    return 'refresh_token';
  } else if (path.includes('/login')) {
    return 'login';
  } else if (path.includes('/register')) {
    return 'register';
  } else {
    return 'other';
  }
}

/**
 * 获取认证提供商
 * @param {Object} req - 请求对象
 * @returns {string} 认证提供商
 */
function getAuthProvider(req) {
  const path = req.path.toLowerCase();
  
  if (path.includes('/oauth/wechat')) {
    return 'wechat';
  } else if (path.includes('/oauth/alipay')) {
    return 'alipay';
  } else if (path.includes('/oauth/google')) {
    return 'google';
  } else if (path.includes('/oauth/apple')) {
    return 'apple';
  } else if (path.includes('/oauth/facebook')) {
    return 'facebook';
  } else if (path.includes('/oauth/douyin')) {
    return 'douyin';
  } else if (path.includes('/oauth/xiaohongshu')) {
    return 'xiaohongshu';
  } else if (path.includes('/oauth/youtube')) {
    return 'youtube';
  } else if (path.includes('/oauth/tiktok')) {
    return 'tiktok';
  } else {
    return 'local';
  }
}

/**
 * 创建指标端点中间件
 * 用于提供Prometheus指标端点
 * @returns {Function} Express中间件函数
 */
function createMetricsEndpoint() {
  return async (req, res) => {
    try {
      // 获取注册表并输出指标
      const register = metricsService.getRegistry();
      const metrics = await register.metrics();
      
      res.set('Content-Type', register.contentType);
      res.end(metrics);
    } catch (error) {
      res.status(500).send(`指标收集失败: ${error.message}`);
    }
  };
}

/**
 * 认证指标装饰器
 * 用于记录认证相关指标
 * @param {string} method - 认证方法
 * @param {string} provider - 认证提供商
 */
function recordAuthMetrics(method, provider = 'internal') {
  return (target, propertyKey, descriptor) => {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function(...args) {
      const startTime = Date.now();
      
      try {
        // 执行原始方法
        const result = await originalMethod.apply(this, args);
        
        // 记录成功指标
        if (result && result.success) {
          metricsService.recordAuthSuccess(method, provider);
          
          // 记录令牌生成时间（如果适用）
          if (result.accessToken) {
            const tokenDuration = Date.now() - startTime;
            metricsService.recordTokenGeneration('access', tokenDuration);
          }
        } else {
          // 记录失败指标
          const reason = (result && result.message) ? 
            result.message.substring(0, 30) : 'unknown';
          metricsService.recordAuthFailure(method, reason, provider);
        }
        
        return result;
      } catch (error) {
        // 记录错误指标
        metricsService.recordAuthFailure(
          method, 
          error.name || 'exception', 
          provider
        );
        throw error;
      }
    };
    
    return descriptor;
  };
}

/**
 * 数据库操作指标装饰器
 * 用于记录数据库操作相关指标
 * @param {string} operation - 操作类型
 * @param {string} table - 表名
 */
function recordDbMetrics(operation, table) {
  return (target, propertyKey, descriptor) => {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function(...args) {
      const startTime = Date.now();
      
      try {
        // 执行原始方法
        const result = await originalMethod.apply(this, args);
        
        // 记录成功指标
        const duration = Date.now() - startTime;
        metricsService.recordDbOperation(operation, table, 'success', duration);
        
        return result;
      } catch (error) {
        // 记录错误指标
        const duration = Date.now() - startTime;
        metricsService.recordDbOperation(operation, table, 'error', duration);
        throw error;
      }
    };
    
    return descriptor;
  };
}

/**
 * Redis操作指标装饰器
 * 用于记录Redis操作相关指标
 * @param {string} operation - 操作类型
 */
function recordRedisMetrics(operation) {
  return (target, propertyKey, descriptor) => {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function(...args) {
      const startTime = Date.now();
      
      try {
        // 执行原始方法
        const result = await originalMethod.apply(this, args);
        
        // 记录成功指标
        const duration = Date.now() - startTime;
        metricsService.recordRedisOperation(operation, 'success', duration);
        
        return result;
      } catch (error) {
        // 记录错误指标
        const duration = Date.now() - startTime;
        metricsService.recordRedisOperation(operation, 'error', duration);
        throw error;
      }
    };
    
    return descriptor;
  };
}

/**
 * 跨区域同步指标装饰器
 * 用于记录跨区域同步操作相关指标
 * @param {string} operation - 操作类型
 * @param {string} region - 区域
 */
function recordSyncMetrics(operation, region) {
  return (target, propertyKey, descriptor) => {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function(...args) {
      const startTime = Date.now();
      
      try {
        // 执行原始方法
        const result = await originalMethod.apply(this, args);
        
        // 记录成功指标
        const duration = Date.now() - startTime;
        metricsService.recordCrossRegionSync(operation, region, 'success', duration);
        
        return result;
      } catch (error) {
        // 记录错误指标
        const duration = Date.now() - startTime;
        metricsService.recordCrossRegionSync(operation, region, 'error', duration);
        throw error;
      }
    };
    
    return descriptor;
  };
}

module.exports = {
  metricsMiddleware,
  createMetricsEndpoint,
  recordAuthMetrics,
  recordDbMetrics,
  recordRedisMetrics,
  recordSyncMetrics
}; 