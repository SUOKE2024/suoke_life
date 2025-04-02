/**
 * 灰度发布(金丝雀)路由中间件
 * 
 * 提供流量分割和A/B测试功能
 */

const { createProxyMiddleware } = require('http-proxy-middleware');
const logger = require('../utils/logger');

/**
 * 灰度发布配置类
 */
class CanaryConfig {
  /**
   * 创建灰度发布配置
   * @param {string} serviceName 服务名称
   * @param {Object} options 配置选项
   */
  constructor(serviceName, options = {}) {
    this.serviceName = serviceName;
    this.enabled = options.enabled || false;
    this.versions = options.versions || [];
    this.defaultVersion = options.defaultVersion || 'stable';
    this.rules = options.rules || [];
    this.metrics = {
      requests: {},
      errors: {},
      latency: {}
    };
    
    // 初始化指标计数
    this.versions.forEach(version => {
      this.metrics.requests[version.name] = 0;
      this.metrics.errors[version.name] = 0;
      this.metrics.latency[version.name] = [];
    });
  }
  
  /**
   * 记录请求指标
   * @param {string} version 版本名称
   * @param {number} statusCode HTTP状态码 
   * @param {number} latency 请求延迟时间(毫秒)
   */
  recordMetrics(version, statusCode, latency) {
    if (!this.metrics.requests[version]) {
      this.metrics.requests[version] = 0;
      this.metrics.errors[version] = 0;
      this.metrics.latency[version] = [];
    }
    
    this.metrics.requests[version]++;
    
    if (statusCode >= 400) {
      this.metrics.errors[version]++;
    }
    
    // 记录延迟时间，最多保留最近100个请求的延迟
    this.metrics.latency[version].push(latency);
    if (this.metrics.latency[version].length > 100) {
      this.metrics.latency[version].shift();
    }
  }
  
  /**
   * 获取指标统计
   * @returns {Object} 指标统计
   */
  getMetrics() {
    const result = {
      requests: { ...this.metrics.requests },
      errors: { ...this.metrics.errors },
      latency: {}
    };
    
    // 计算每个版本的平均延迟和错误率
    Object.keys(this.metrics.requests).forEach(version => {
      const requests = this.metrics.requests[version];
      const errors = this.metrics.errors[version];
      const latencyArr = this.metrics.latency[version];
      
      result.latency[version] = {
        avg: latencyArr.length > 0 
          ? latencyArr.reduce((sum, val) => sum + val, 0) / latencyArr.length 
          : 0,
        min: latencyArr.length > 0 ? Math.min(...latencyArr) : 0,
        max: latencyArr.length > 0 ? Math.max(...latencyArr) : 0
      };
      
      result.errorRate = requests > 0 ? (errors / requests) : 0;
    });
    
    return result;
  }
  
  /**
   * 重置指标计数
   */
  resetMetrics() {
    this.versions.forEach(version => {
      this.metrics.requests[version.name] = 0;
      this.metrics.errors[version.name] = 0;
      this.metrics.latency[version.name] = [];
    });
  }
}

// 存储灰度发布配置
const canaryConfigs = new Map();

/**
 * 获取灰度发布配置
 * @param {string} serviceName 服务名称
 * @returns {CanaryConfig} 灰度发布配置
 */
function getCanaryConfig(serviceName) {
  if (!canaryConfigs.has(serviceName)) {
    canaryConfigs.set(serviceName, new CanaryConfig(serviceName));
  }
  return canaryConfigs.get(serviceName);
}

/**
 * 设置灰度发布配置
 * @param {string} serviceName 服务名称
 * @param {Object} options 配置选项
 * @returns {CanaryConfig} 灰度发布配置
 */
function setCanaryConfig(serviceName, options) {
  const config = new CanaryConfig(serviceName, options);
  canaryConfigs.set(serviceName, config);
  return config;
}

/**
 * 根据请求确定应该使用的版本
 * @param {CanaryConfig} config 灰度发布配置
 * @param {Object} req Express请求对象
 * @returns {string} 目标版本
 */
function determineTargetVersion(config, req) {
  if (!config.enabled || config.versions.length === 0) {
    return config.defaultVersion;
  }
  
  // 检查是否有强制指定版本的头部或查询参数
  const forcedVersion = req.headers['x-canary-version'] || req.query.canary_version;
  if (forcedVersion && config.versions.some(v => v.name === forcedVersion)) {
    logger.debug(`请求强制使用版本: ${forcedVersion}`);
    return forcedVersion;
  }
  
  // 应用路由规则
  for (const rule of config.rules) {
    let matches = false;
    
    // 规则类型：用户ID
    if (rule.type === 'userId' && req.user && req.user.id) {
      matches = rule.values.includes(req.user.id);
    }
    
    // 规则类型：用户组
    else if (rule.type === 'userGroup' && req.user && req.user.groups) {
      matches = rule.values.some(group => req.user.groups.includes(group));
    }
    
    // 规则类型：请求头
    else if (rule.type === 'header' && rule.name) {
      const headerValue = req.headers[rule.name.toLowerCase()];
      matches = headerValue && rule.values.includes(headerValue);
    }
    
    // 规则类型：查询参数
    else if (rule.type === 'query' && rule.name) {
      const queryValue = req.query[rule.name];
      matches = queryValue && rule.values.includes(queryValue);
    }
    
    // 规则类型：设备类型
    else if (rule.type === 'device') {
      const userAgent = req.headers['user-agent'] || '';
      matches = rule.values.some(device => {
        if (device === 'mobile') {
          return /mobile|android|iphone|ipad|ipod/i.test(userAgent);
        } else if (device === 'desktop') {
          return !/mobile|android|iphone|ipad|ipod/i.test(userAgent);
        }
        return false;
      });
    }
    
    // 规则类型：随机比例
    else if (rule.type === 'random' && rule.percentage) {
      matches = Math.random() < (rule.percentage / 100);
    }
    
    // 规则类型：IP地址
    else if (rule.type === 'ip') {
      const clientIp = req.ip || req.connection.remoteAddress;
      matches = rule.values.includes(clientIp);
    }
    
    // 如果规则匹配，返回指定的版本
    if (matches && rule.targetVersion) {
      return rule.targetVersion;
    }
  }
  
  // 没有匹配规则，使用权重分配
  const totalWeight = config.versions.reduce((sum, v) => sum + (v.weight || 0), 0);
  if (totalWeight > 0) {
    const random = Math.random() * totalWeight;
    let cumulativeWeight = 0;
    
    for (const version of config.versions) {
      cumulativeWeight += (version.weight || 0);
      if (random <= cumulativeWeight) {
        return version.name;
      }
    }
  }
  
  // 默认返回稳定版本
  return config.defaultVersion;
}

/**
 * 创建灰度发布路由中间件
 * @param {string} serviceName 服务名称
 * @param {Object} options 配置选项
 * @returns {Function} Express中间件
 */
function createCanaryRouter(serviceName, options = {}) {
  const config = setCanaryConfig(serviceName, options);
  
  return (req, res, next) => {
    if (!config.enabled || config.versions.length === 0) {
      return next();
    }
    
    const targetVersion = determineTargetVersion(config, req);
    const versionConfig = config.versions.find(v => v.name === targetVersion);
    
    if (!versionConfig) {
      logger.warn(`灰度发布: 未找到版本配置 ${targetVersion} 对于服务 ${serviceName}`);
      return next();
    }
    
    // 开始请求时间
    const startTime = Date.now();
    
    // 添加版本标记到请求头
    req.headers['x-canary-version'] = targetVersion;
    
    logger.debug(`灰度发布: 服务 ${serviceName} 请求路由到版本 ${targetVersion} - ${versionConfig.url}`);
    
    // 创建代理中间件
    const proxy = createProxyMiddleware({
      target: versionConfig.url,
      changeOrigin: true,
      pathRewrite: versionConfig.pathRewrite || {},
      logLevel: 'warn',
      onProxyReq: (proxyReq, req, res) => {
        // 设置灰度发布版本头
        proxyReq.setHeader('X-Canary-Version', targetVersion);
        
        // 如果提供了自定义的onProxyReq回调，则执行
        if (options.onProxyReq) {
          options.onProxyReq(proxyReq, req, res, targetVersion);
        }
      },
      onProxyRes: (proxyRes, req, res) => {
        // 添加版本响应头
        proxyRes.headers['x-served-by'] = `${serviceName}:${targetVersion}`;
        
        // 计算请求处理时间并记录指标
        const endTime = Date.now();
        const latency = endTime - startTime;
        config.recordMetrics(targetVersion, proxyRes.statusCode, latency);
        
        // 如果提供了自定义的onProxyRes回调，则执行
        if (options.onProxyRes) {
          options.onProxyRes(proxyRes, req, res, targetVersion);
        }
      },
      onError: (err, req, res) => {
        logger.error(`灰度发布代理错误: ${serviceName}:${targetVersion}`, err);
        
        // 记录错误指标
        const endTime = Date.now();
        const latency = endTime - startTime;
        config.recordMetrics(targetVersion, 500, latency);
        
        res.status(500).json({
          status: 'error',
          message: `服务 ${serviceName} (${targetVersion}) 暂时不可用`,
          error: process.env.NODE_ENV === 'production' ? undefined : err.message
        });
      }
    });
    
    // 执行代理
    proxy(req, res, next);
  };
}

/**
 * 获取所有灰度发布配置
 * @returns {Object} 所有灰度发布配置
 */
function getAllCanaryConfigs() {
  const result = {};
  
  for (const [serviceName, config] of canaryConfigs.entries()) {
    result[serviceName] = {
      enabled: config.enabled,
      versions: config.versions.map(v => ({
        name: v.name,
        weight: v.weight
      })),
      metrics: config.getMetrics()
    };
  }
  
  return result;
}

module.exports = {
  createCanaryRouter,
  getCanaryConfig,
  setCanaryConfig,
  getAllCanaryConfigs
}; 