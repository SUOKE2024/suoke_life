/**
 * 认证服务应用入口
 */
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const morgan = require('morgan');
const swaggerUi = require('swagger-ui-express');
const swaggerSpecs = require('./config/swagger');
const config = require('./config');
const { logger, errorHandler } = require('@suoke/shared').utils;
const { createMetricsMiddleware } = require('./middlewares/metrics.middleware');
const { globalLimiter } = require('./middlewares/rate-limit.middleware');
const { generateCsrfToken } = require('./middlewares/csrf.middleware');

// 创建Express应用
const app = express();

// 安全中间件
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"], // 允许Swagger UI正常工作
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:']
    }
  },
  crossOriginResourcePolicy: { policy: 'cross-origin' }, // 允许跨源资源访问
  crossOriginEmbedderPolicy: false, // 允许跨源嵌入
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  xssFilter: true
}));

// CORS配置
app.use(cors({
  origin: config.cors.origins,
  methods: config.cors.methods,
  allowedHeaders: config.cors.allowedHeaders,
  exposedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token', 'X-CSRF-Signature'],
  credentials: true
}));

// 请求解析
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// 日志记录
if (config.env !== 'test') {
  app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));
}

// 全局速率限制
app.use(globalLimiter);

// 指标收集中间件
app.use(createMetricsMiddleware());

// API文档
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpecs, {
  explorer: true,
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: "索克生活认证服务API文档"
}));

// 为所有GET响应生成CSRF令牌
app.use((req, res, next) => {
  if (req.method === 'GET') {
    generateCsrfToken(req, res, next);
  } else {
    next();
  }
});

// 导入路由
const authRoutes = require('./routes/auth.routes');
const oauthRoutes = require('./routes/oauth.routes');
const smsAuthRoutes = require('./routes/sms-auth.routes');
const phoneAuthRoutes = require('./routes/phone-auth.routes');
const biometricRoutes = require('./routes/biometric.routes');
const healthRoutes = require('./routes/health.routes');
const metricsRoutes = require('./routes/metrics.routes');

// 路由注册
app.use('/api/auth', authRoutes);
app.use('/api/auth/oauth', oauthRoutes);
app.use('/api/auth/sms', smsAuthRoutes);
app.use('/api/auth/phone', phoneAuthRoutes);
app.use('/api/auth/biometric', biometricRoutes);
app.use('/health', healthRoutes);
app.use('/api/health', healthRoutes);
app.use('/metrics', metricsRoutes);
app.use('/api/metrics', metricsRoutes);

// 简单健康检查 (弃用，使用完整的健康检查路由)
app.get(['/'], (req, res) => {
  res.status(200).json({ 
    status: 'ok', 
    service: 'auth-service', 
    version: process.env.npm_package_version || '1.0.0' 
  });
});

// 404处理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: `找不到路径: ${req.path}`
  });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  
  // 转换错误格式，添加code字段
  let errorCode = 'server/unknown-error';
  
  if (err.name === 'ValidationError') {
    errorCode = 'validation/invalid-input';
  } else if (err.message.includes('令牌') || err.message.includes('token')) {
    if (err.message.includes('过期') || err.message.includes('expired')) {
      errorCode = 'auth/token-expired';
    } else {
      errorCode = 'auth/invalid-token';
    }
  } else if (err.message.includes('未授权') || err.message.includes('unauthorized')) {
    errorCode = 'auth/unauthorized';
  } else if (err.message.includes('无效凭证') || err.message.includes('invalid credentials')) {
    errorCode = 'auth/invalid-credentials';
  } else if (err.message.includes('用户不存在') || err.message.includes('user not found')) {
    errorCode = 'auth/user-not-found';
  } else if (err.message.includes('用户已存在') || err.message.includes('user already exists')) {
    errorCode = 'auth/user-already-exists';
  } else if (err.message.includes('生物识别')) {
    errorCode = 'auth/biometric-failed';
  }
  
  // 记录服务器错误
  if (statusCode >= 500) {
    logger.error(`服务器错误: ${err.message}`, {
      error: err,
      stack: err.stack,
      path: req.path,
      method: req.method
    });
  } else {
    logger.warn(`客户端错误: ${err.message}`, {
      error: err,
      path: req.path,
      method: req.method
    });
  }
  
  // 返回标准错误响应格式
  return res.status(statusCode).json({
    success: false,
    message: err.message || '服务器内部错误',
    code: err.code || errorCode,
    errors: err.errors || null
  });
});

module.exports = app; 