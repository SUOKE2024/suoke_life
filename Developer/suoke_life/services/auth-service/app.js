/**
 * 索克生活认证服务
 * 应用程序入口文件
 */
const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const session = require('express-session');
const RedisStore = require('connect-redis').default;

// 引入工具和服务
const logger = require('./src/utils/logger');
const redisClient = require('./src/utils/redis');
const config = require('./src/config');

// 引入中间件
const { csrfProtection, csrfTokenGenerator } = require('./src/middlewares/csrf.middleware');
const { metricsMiddleware } = require('./src/middlewares/metrics.middleware');
const errorHandler = require('./src/middlewares/error.middleware');
const rateLimiter = require('./src/middlewares/rate-limiter.middleware');

// 引入路由
const authRouter = require('./src/controllers/auth.controller');
const sessionRouter = require('./src/controllers/session.controller');
const twoFactorRouter = require('./src/controllers/two-factor.controller');
const smsAuthRouter = require('./src/controllers/sms-auth.controller');
const knowledgeAuthRouter = require('./src/controllers/knowledge-auth.controller');
const deviceRouter = require('./src/controllers/device.controller');
const deviceVerificationRouter = require('./src/controllers/device-verification.controller');
const biometricRouter = require('./src/controllers/biometric.controller');
const securityDashboardRouter = require('./src/controllers/security-dashboard.controller');
const metricsRouter = require('./src/controllers/metrics.controller');

// 创建Express应用
const app = express();

// 配置会话存储
const sessionStore = new RedisStore({
  client: redisClient,
  prefix: 'session:',
  ttl: config.session.ttl || 86400 // 默认1天
});

// 基础中间件
app.use(helmet()); // 安全头
app.use(compression()); // 响应压缩
app.use(cors(config.cors)); // CORS策略
app.use(bodyParser.json({ limit: '1mb' })); // JSON解析
app.use(bodyParser.urlencoded({ extended: true, limit: '1mb' })); // URL编码解析
app.use(cookieParser(config.cookies.secret)); // Cookie解析

// 会话中间件
app.use(session({
  store: sessionStore,
  secret: config.session.secret,
  name: config.session.name || 'suoke.sid',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: (config.session.ttl || 86400) * 1000
  }
}));

// 日志中间件
if (process.env.NODE_ENV !== 'test') {
  app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));
}

// 指标中间件
app.use(metricsMiddleware);

// CSRF令牌生成和验证
app.use(csrfTokenGenerator);

// 健康检查接口
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'UP', timestamp: new Date().toISOString() });
});

app.get('/health/ready', (req, res) => {
  res.status(200).json({ status: 'READY', timestamp: new Date().toISOString() });
});

app.get('/health/startup', (req, res) => {
  res.status(200).json({ status: 'STARTED', timestamp: new Date().toISOString() });
});

// 公共路由（无需认证）
app.use('/auth', authRouter);
app.use('/auth/sms', smsAuthRouter);

// 需要CSRF保护的路由
app.use(csrfProtection);

// API路由
app.use('/api/sessions', sessionRouter);
app.use('/api/two-factor', twoFactorRouter);
app.use('/api/devices', deviceRouter);
app.use('/api/device-verification', deviceVerificationRouter);
app.use('/api/biometric', biometricRouter);
app.use('/api/knowledge-auth', knowledgeAuthRouter);
app.use('/api/security', securityDashboardRouter);
app.use('/api/metrics', metricsRouter);

// 404错误处理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: '请求的资源不存在',
    code: 'resource_not_found'
  });
});

// 全局错误处理
app.use(errorHandler);

module.exports = app;
