/**
 * 索克生活认证服务 - 主服务
 */
const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const winston = require('winston');
const expressWinston = require('express-winston');
const passport = require('passport');
const promClient = require('prom-client');
const fs = require('fs');
const path = require('path');
const http = require('http');
const config = require('./src/config');
const logger = require('./src/utils/logger');

// 初始化Express应用
const app = express();
const PORT = config.server.port || 3000;

// 创建日志目录
if (!fs.existsSync(path.join(__dirname, 'logs'))) {
  fs.mkdirSync(path.join(__dirname, 'logs'), { recursive: true });
}

// 配置日志记录器
const loggerWinston = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'auth-service' },
  transports: [
    new winston.transports.File({ filename: path.join(__dirname, 'logs/error.log'), level: 'error' }),
    new winston.transports.File({ filename: path.join(__dirname, 'logs/combined.log') })
  ]
});

// 在非生产环境下同时输出到控制台
if (process.env.NODE_ENV !== 'production') {
  loggerWinston.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    )
  }));
}

// 设置Prometheus指标收集
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// HTTP请求计数器
const httpRequestsTotal = new promClient.Counter({
  name: 'auth_http_requests_total',
  help: '认证服务HTTP请求总数',
  labelNames: ['method', 'path', 'status'],
  registers: [register]
});

// 请求持续时间直方图
const httpRequestDurationSeconds = new promClient.Histogram({
  name: 'auth_http_request_duration_seconds',
  help: '认证服务HTTP请求持续时间（秒）',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2.5, 5, 10],
  registers: [register]
});

// 认证失败计数器
const authFailuresTotal = new promClient.Counter({
  name: 'auth_failures_total',
  help: '认证失败总数',
  labelNames: ['method', 'reason'],
  registers: [register]
});

// 中间件配置
app.use(cors({
  origin: process.env.CORS_ALLOWED_ORIGINS ? process.env.CORS_ALLOWED_ORIGINS.split(',') : '*',
  methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
  credentials: true,
  optionsSuccessStatus: 204
}));
app.use(helmet());
app.use(compression());
app.use(bodyParser.json({ limit: '1mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '1mb' }));
app.use(cookieParser());
app.use(passport.initialize());

// 请求日志中间件
app.use(expressWinston.logger({
  transports: [
    new winston.transports.File({ filename: path.join(__dirname, 'logs/requests.log') })
  ],
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  meta: true,
  expressFormat: true,
  colorize: false
}));

// 指标收集中间件
app.use((req, res, next) => {
  const start = Date.now();
  
  // 拦截响应结束事件以记录指标
  res.on('finish', () => {
    const duration = Date.now() - start;
    httpRequestsTotal.labels(req.method, req.path, res.statusCode).inc();
    httpRequestDurationSeconds.labels(req.method, req.path, res.statusCode).observe(duration / 1000);
  });
  
  next();
});

// 健康检查端点
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'UP', timestamp: new Date().toISOString() });
});

app.get('/health/ready', (req, res) => {
  // 此处可以添加数据库连接检查等
  res.status(200).json({ status: 'READY', timestamp: new Date().toISOString() });
});

app.get('/health/startup', (req, res) => {
  res.status(200).json({ status: 'STARTED', timestamp: new Date().toISOString() });
});

// 暴露Prometheus指标
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// 认证路由
app.post('/auth/login', (req, res) => {
  // 简单模拟，实际应用中需连接数据库验证
  const { username, password } = req.body;
  
  if (username === 'admin' && password === 'adminPass123') {
    res.status(200).json({ 
      success: true, 
      token: 'simulated-jwt-token',
      user: { id: 1, username: 'admin', role: 'admin' }
    });
  } else {
    authFailuresTotal.labels('password', 'invalid_credentials').inc();
    res.status(401).json({ success: false, message: '用户名或密码不正确' });
  }
});

// 用户API
app.get('/auth/user', (req, res) => {
  // 简单模拟，实际应用中需验证令牌并获取用户信息
  res.status(200).json({ 
    id: 1, 
    username: 'admin', 
    email: 'admin@suoke.life',
    role: 'admin',
    permissions: ['read', 'write', 'admin']
  });
});

// API文档路由
app.get('/api-docs', (req, res) => {
  res.json({
    service: 'auth-service',
    version: '1.0.0',
    description: '索克生活认证服务API',
    endpoints: [
      { path: '/health', method: 'GET', description: '健康检查' },
      { path: '/metrics', method: 'GET', description: 'Prometheus指标' },
      { path: '/auth/login', method: 'POST', description: '用户登录' },
      { path: '/auth/user', method: 'GET', description: '获取用户信息' }
    ]
  });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  loggerWinston.error('应用错误', { error: err.message, stack: err.stack });
  res.status(500).json({ error: '服务器内部错误', message: err.message });
});

// 未捕获异常处理
process.on('uncaughtException', (error) => {
  loggerWinston.error('未捕获的异常', { error: error.stack });
  // 给进程一些时间记录日志，然后退出
  setTimeout(() => {
    process.exit(1);
  }, 1000);
});

// 未处理的Promise拒绝处理
process.on('unhandledRejection', (reason, promise) => {
  loggerWinston.error('未处理的Promise拒绝', { 
    reason: reason instanceof Error ? reason.stack : reason,
    promise
  });
});

// 创建HTTP服务器
const server = http.createServer(app);

// 启动服务器
server.listen(PORT, () => {
  loggerWinston.info(`索克生活认证服务已启动`, {
    port: PORT,
    env: process.env.NODE_ENV || 'development',
    nodeVersion: process.version
  });
});

// 优雅关闭
const gracefulShutdown = () => {
  loggerWinston.info('收到关闭信号，正在优雅关闭...');
  
  server.close(() => {
    loggerWinston.info('HTTP服务器已关闭');
    // 关闭数据库连接等其他资源
    process.exit(0);
  });
  
  // 如果10秒后服务器仍未关闭，则强制退出
  setTimeout(() => {
    loggerWinston.error('服务器关闭超时，强制退出');
    process.exit(1);
  }, 10000);
};

// 监听终止信号
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

module.exports = server; 