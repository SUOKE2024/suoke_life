/**
 * API Gateway 服务
 * 索克生活APP API网关入口
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const bodyParser = require('body-parser');
const morgan = require('morgan');
const compression = require('compression');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
const expressWinston = require('express-winston');
const fs = require('fs');
const path = require('path');
const LoadBalancer = require('./utils/load-balancer');
const routes = require('./routes');
const knowledgeRouter = require('./middlewares/knowledge-router');
const responseCache = require('./utils/response-cache');
const { circuitBreakerMiddleware } = require('./middlewares/circuit-breaker');
const { createCanaryRouter } = require('./middlewares/canary-router');
const metricsRoutes = require('./routes/metrics');

// 加载环境变量
require('dotenv').config();

// 应用配置
let config;
try {
  const configPath = path.join(__dirname, '../config/api-gateway.json');
  config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  // 替换环境变量占位符
  const configStr = JSON.stringify(config);
  const parsedConfig = JSON.parse(configStr.replace(/\${([^}]+)}/g, (_, varName) => {
    return process.env[varName] || '';
  }));
  
  config = parsedConfig;
} catch (err) {
  console.error('无法加载配置文件:', err);
  config = {
    service: {
      name: 'api-gateway',
      version: '1.0.0',
      port: process.env.PORT || 3000,
      log_level: process.env.LOG_LEVEL || 'info',
      environment: process.env.NODE_ENV || 'development'
    },
    cors: {
      origin: '*',
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    },
    rate_limit: {
      window: 60000,
      max: 100
    },
    services: []
  };
}

// 创建Express应用
const app = express();
const PORT = process.env.PORT || config.service.port || 3000;

// 设置日志
const logger = winston.createLogger({
  level: config.service.log_level,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console()
  ]
});

// 请求日志中间件
app.use(expressWinston.logger({
  winstonInstance: logger,
  expressFormat: true,
  colorize: process.env.NODE_ENV !== 'production',
  meta: true
}));

// 基础中间件
app.use(helmet()); // 安全头
app.use(cors(config.cors)); // CORS配置
app.use(bodyParser.json()); // JSON解析
app.use(bodyParser.urlencoded({ extended: true })); // URL编码
app.use(compression()); // 响应压缩
app.use(morgan(process.env.NODE_ENV !== 'production' ? 'dev' : 'combined')); // HTTP请求日志

// 速率限制
const limiter = rateLimit({
  windowMs: config.rate_limit.window,
  max: config.rate_limit.max,
  message: config.rate_limit.message || '请求过于频繁，请稍后再试',
  standardHeaders: true,
  legacyHeaders: false
});
app.use(limiter);

// 初始化请求统计信息
app.set('requestStats', {
  total: 0,
  byMethod: {},
  byPath: {},
  byStatus: {},
  errors: 0,
  startTime: Date.now()
});

// 请求统计中间件
app.use((req, res, next) => {
  const stats = app.get('requestStats');
  stats.total++;
  
  // 按方法统计
  stats.byMethod[req.method] = (stats.byMethod[req.method] || 0) + 1;
  
  // 提取基本路径，去除参数和ID
  const basePath = req.path.split('/').slice(0, 3).join('/');
  stats.byPath[basePath] = (stats.byPath[basePath] || 0) + 1;
  
  // 拦截响应完成事件以记录状态
  res.on('finish', () => {
    // 按状态码统计
    const statusGroup = Math.floor(res.statusCode / 100) + 'xx';
    stats.byStatus[statusGroup] = (stats.byStatus[statusGroup] || 0) + 1;
    
    // 记录错误
    if (res.statusCode >= 500) {
      stats.errors++;
    }
  });
  
  next();
});

// 健康检查
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    service: config.service.name,
    version: config.service.version,
    timestamp: new Date().toISOString()
  });
});

// 就绪检查，检查服务连接状态
app.get('/health/ready', (req, res) => {
  // 获取服务负载均衡器
  const serviceLBMap = app.get('serviceLBMap') || new Map();
  const services = {};
  
  for (const [serviceName, lb] of serviceLBMap.entries()) {
    services[serviceName] = {
      available: lb.urls.length > 0,
      urls: lb.urls.length
    };
  }
  
  res.status(200).json({
    status: 'ready',
    uptime: process.uptime(),
    services
  });
});

// 添加响应缓存中间件
const cacheOptions = {
  ttl: process.env.CACHE_TTL || 300000, // 5分钟
  exclude: (req) => {
    // 排除特定路径
    return req.path.includes('/auth/') || 
           req.path.includes('/metrics') || 
           req.originalUrl.includes('_nocache=true');
  }
};
app.use(responseCache.createCacheMiddleware(cacheOptions));

// 服务代理
if (config.services && Array.isArray(config.services)) {
  config.services.forEach(service => {
    if (service.name && service.url && service.prefix) {
      logger.info(`设置代理: ${service.prefix} -> ${service.url}`);
      
      // 为协调器服务创建特定路径映射
      let pathRewrite = service.pathRewrite || { [`^${service.prefix}`]: '' };
      
      // 添加协调器服务的特殊路径映射
      if (service.name === 'agent-coordinator-service') {
        pathRewrite = {
          [`^${service.prefix}/sessions`]: '/sessions',
          [`^${service.prefix}/agents`]: '/agents',
          [`^${service.prefix}/coordination`]: '/coordination',
          [`^${service.prefix}/knowledge`]: '/knowledge',
          [`^${service.prefix}`]: '/api' // 默认映射到协调器的/api路径
        };
      }
      
      // 检查是否配置了灰度发布
      if (service.canary && service.canary.enabled) {
        logger.info(`为服务 ${service.name} 启用灰度发布`);
        
        // 创建灰度发布路由中间件
        const canaryRouter = createCanaryRouter(service.name, {
          enabled: service.canary.enabled,
          versions: service.canary.versions || [],
          defaultVersion: service.canary.defaultVersion || 'stable',
          rules: service.canary.rules || [],
          onProxyReq: (proxyReq, req, res, version) => {
            // 可在此添加自定义请求头
            proxyReq.setHeader('X-API-Gateway', config.service.name);
            
            // 传递认证信息和追踪ID
            if (req.headers.authorization) {
              proxyReq.setHeader('Authorization', req.headers.authorization);
            }
            if (req.id || req.headers['x-request-id']) {
              proxyReq.setHeader('X-Request-ID', req.id || req.headers['x-request-id']);
            }
          }
        });
        
        // 为每个服务的灰度版本添加断路器
        const breakerOptions = {
          failureThreshold: service.circuit_breaker?.failure_threshold || 5,
          resetTimeout: service.circuit_breaker?.reset_timeout || 30000,
          timeout: service.timeout || 30000
        };
        
        app.use(service.prefix, circuitBreakerMiddleware(service.name, breakerOptions));
        app.use(service.prefix, canaryRouter);
      } else {
        // 为每个服务添加断路器
        const breakerOptions = {
          failureThreshold: service.circuit_breaker?.failure_threshold || 5,
          resetTimeout: service.circuit_breaker?.reset_timeout || 30000,
          timeout: service.timeout || 30000
        };
        
        app.use(service.prefix, circuitBreakerMiddleware(service.name, breakerOptions));
        
        // 使用常规代理
        app.use(service.prefix, createProxyMiddleware({
          target: service.url,
          changeOrigin: true,
          pathRewrite: pathRewrite,
          logLevel: 'warn',
          onProxyReq: (proxyReq, req, res) => {
            // 可在此添加自定义请求头
            proxyReq.setHeader('X-API-Gateway', config.service.name);
            
            // 协调器服务的特殊处理
            if (service.name === 'agent-coordinator-service') {
              // 传递原始认证信息
              if (req.headers.authorization) {
                proxyReq.setHeader('Authorization', req.headers.authorization);
              }
              
              // 传递追踪ID
              if (req.id || req.headers['x-request-id']) {
                proxyReq.setHeader('X-Request-ID', req.id || req.headers['x-request-id']);
              }
            }
          },
          onError: (err, req, res) => {
            logger.error(`代理错误: ${service.name}`, err);
            res.status(500).json({
              status: 'error',
              message: `服务 ${service.name} 暂时不可用`,
              error: process.env.NODE_ENV === 'production' ? undefined : err.message
            });
          }
        }));
      }
    }
  });
}

// 注册监控指标路由
app.use('/metrics', metricsRoutes);

// 使用知识路由中间件
app.use(knowledgeRouter);

// 使用路由
app.use('/', routes);

// 错误处理中间件
app.use((err, req, res, next) => {
  logger.error('服务器错误:', err);
  res.status(500).json({
    status: 'error',
    message: '服务器内部错误',
    error: process.env.NODE_ENV === 'production' ? undefined : err.message
  });
});

// 未找到路由处理
app.use((req, res) => {
  res.status(404).json({
    status: 'error',
    message: '未找到请求的资源'
  });
});

// 初始化服务负载均衡器
const serviceLBMap = new Map();

// 将服务负载均衡器映射给应用上下文
app.set('serviceLBMap', serviceLBMap);

// 启动服务器
app.listen(PORT, () => {
  logger.info(`API网关服务已启动，端口: ${PORT}`);
  logger.info(`环境: ${config.service.environment}`);
  logger.info(`服务名称: ${config.service.name}`);
  logger.info(`版本: ${config.service.version}`);
});

// 捕获未处理的异常
process.on('uncaughtException', (err) => {
  logger.error('未捕获的异常:', err);
  // 给进程一些时间来处理当前请求然后退出
  setTimeout(() => {
    process.exit(1);
  }, 1000);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('未处理的Promise拒绝:', reason);
});

module.exports = app; // 为测试导出 