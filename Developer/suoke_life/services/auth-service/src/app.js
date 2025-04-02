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
const { csrfProtection } = require('./middlewares/csrf.middleware');
const { verifyToken } = require('./middlewares/auth.middleware');
const { verifySession, checkSuspiciousSession } = require('./middlewares/session.middleware');
const { v4: uuidv4 } = require('uuid');

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
  origin: config.security.cors.allowedOrigins,
  methods: config.security.cors.allowedMethods,
  allowedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token', 'X-XSRF-Token'],
  exposedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token', 'X-XSRF-Token'],
  credentials: config.security.cors.allowCredentials
}));

// 请求解析
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// 添加请求ID
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || uuidv4();
  res.setHeader('X-Request-ID', req.id);
  next();
});

// 日志记录
if (config.app.environment !== 'test') {
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

// 导入路由
const authRoutes = require('./routes/auth.routes');
const oauthRoutes = require('./routes/oauth.routes');
const smsAuthRoutes = require('./routes/sms-auth.routes');
const phoneAuthRoutes = require('./routes/phone-auth.routes');
const biometricRoutes = require('./routes/biometric.routes');
const twoFactorRoutes = require('./routes/two-factor.routes');
const securityLogsRoutes = require('./routes/security-logs.routes');
const sessionsRoutes = require('./routes/sessions.routes');
const healthRoutes = require('./routes/health.routes');
const metricsRoutes = require('./routes/metrics.routes');

// 基本路由和未受保护的路由
app.use('/health', healthRoutes);
app.use('/api/health', healthRoutes);
app.use('/metrics', metricsRoutes);
app.use('/api/metrics', metricsRoutes);

// 简单健康检查
app.get(['/'], (req, res) => {
  res.status(200).json({ 
    status: 'ok', 
    service: 'auth-service', 
    version: process.env.npm_package_version || '1.0.0' 
  });
});

// 不需要CSRF保护的路由（登录、注册等）
app.use('/api/auth/login', authRoutes);
app.use('/api/auth/register', authRoutes);
app.use('/api/auth/refresh', authRoutes);
app.use('/api/auth/forgot-password', authRoutes);
app.use('/api/auth/reset-password', authRoutes);
app.use('/api/auth/2fa/verify', twoFactorRoutes);

// 应用CSRF保护 - 仅对需要保护的路由
const secureRoutes = express.Router();
// 应用CSRF保护中间件（已在中间件中配置排除路径）
secureRoutes.use(csrfProtection);

// 注册需要CSRF保护的路由
secureRoutes.use('/api/auth', authRoutes);
secureRoutes.use('/api/auth/oauth', oauthRoutes);
secureRoutes.use('/api/auth/sms', smsAuthRoutes);
secureRoutes.use('/api/auth/phone', phoneAuthRoutes);
secureRoutes.use('/api/auth/biometric', biometricRoutes);
secureRoutes.use('/api/auth/2fa', twoFactorRoutes);
secureRoutes.use('/api/auth/security-logs', securityLogsRoutes);

// 添加会话管理路由 - 需要令牌验证和会话验证
const sessionProtectedRoutes = express.Router();
sessionProtectedRoutes.use(verifyToken);
sessionProtectedRoutes.use(verifySession);
sessionProtectedRoutes.use(checkSuspiciousSession);
sessionProtectedRoutes.use('/api/auth/sessions', sessionsRoutes);

// 将安全路由添加到应用
app.use(secureRoutes);
app.use(sessionProtectedRoutes);

// 404处理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: `找不到路径: ${req.path}`,
    code: 'server/not-found',
    requestId: req.id
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
    } else if (err.message.includes('黑名单') || err.message.includes('blacklist')) {
      errorCode = 'auth/token-revoked';
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
  } else if (err.message.includes('CSRF') || err.message.includes('csrf')) {
    errorCode = 'security/csrf-failed';
  } else if (err.message.includes('账户锁定') || err.message.includes('locked')) {
    errorCode = 'auth/account-locked';
  } else if (err.message.includes('密码策略') || err.message.includes('password policy')) {
    errorCode = 'auth/password-policy-violation';
  } else if (err.message.includes('二因素') || err.message.includes('2fa')) {
    errorCode = 'auth/2fa-failed';
  }
  
  // 记录服务器错误
  if (statusCode >= 500) {
    logger.error(`服务器错误: ${err.message}`, {
      error: err,
      stack: err.stack,
      path: req.path,
      method: req.method,
      requestId: req.id
    });
  } else {
    logger.warn(`客户端错误: ${err.message}`, {
      error: err,
      path: req.path,
      method: req.method,
      requestId: req.id
    });
  }
  
  // 返回标准错误响应格式
  return res.status(statusCode).json({
    success: false,
    message: err.message || '服务器内部错误',
    code: err.code || errorCode,
    errors: err.errors || null,
    requestId: req.id
  });
});

module.exports = app; 