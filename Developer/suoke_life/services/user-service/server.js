/**
 * 索克生活用户服务 - 主服务
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
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// 初始化Express应用
const app = express();
const PORT = process.env.PORT || 3002;

// 创建日志和上传目录
const dirs = [
  path.join(__dirname, 'logs'),
  path.join(__dirname, 'uploads'),
  path.join(__dirname, 'uploads/avatars'),
  path.join(__dirname, 'uploads/documents')
];

dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// 配置日志记录器
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.File({ filename: path.join(__dirname, 'logs/error.log'), level: 'error' }),
    new winston.transports.File({ filename: path.join(__dirname, 'logs/combined.log') })
  ]
});

// 在非生产环境下同时输出到控制台
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
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
  name: 'user_http_requests_total',
  help: '用户服务HTTP请求总数',
  labelNames: ['method', 'path', 'status'],
  registers: [register]
});

// 请求持续时间直方图
const httpRequestDurationSeconds = new promClient.Histogram({
  name: 'user_http_request_duration_seconds',
  help: '用户服务HTTP请求持续时间（秒）',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2.5, 5, 10],
  registers: [register]
});

// 文件上传计数器
const fileUploadsTotal = new promClient.Counter({
  name: 'user_file_uploads_total',
  help: '用户文件上传总数',
  labelNames: ['type', 'result'],
  registers: [register]
});

// 配置文件上传
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const type = req.params.type || 'documents';
    const dest = path.join(__dirname, `uploads/${type}`);
    cb(null, dest);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const ext = path.extname(file.originalname);
    cb(null, `${file.fieldname}-${uniqueSuffix}${ext}`);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB限制
  fileFilter: (req, file, cb) => {
    const allowedMimes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
    if (allowedMimes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('不支持的文件类型'), false);
    }
  }
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

// 引入路由
const apiRoutes = require('./src/routes');

// 注册API路由
app.use('/api', apiRoutes);

// 用户路由
app.get('/users', (req, res) => {
  // 简单模拟，实际应用中需从数据库获取
  res.status(200).json({
    users: [
      { id: 1, username: 'admin', email: 'admin@suoke.life', role: 'admin' },
      { id: 2, username: 'user1', email: 'user1@suoke.life', role: 'user' },
      { id: 3, username: 'user2', email: 'user2@suoke.life', role: 'user' }
    ]
  });
});

app.get('/users/:id', (req, res) => {
  const userId = parseInt(req.params.id, 10);
  
  // 简单模拟，实际应用中需从数据库获取
  if (userId === 1) {
    res.status(200).json({
      id: 1,
      username: 'admin',
      email: 'admin@suoke.life',
      role: 'admin',
      profile: {
        fullName: '管理员',
        avatar: '/uploads/avatars/default.png',
        phone: '13800138000',
        address: '北京市海淀区中关村',
        createdAt: '2023-01-01T00:00:00Z'
      }
    });
  } else if (userId > 0 && userId <= 10) {
    res.status(200).json({
      id: userId,
      username: `user${userId}`,
      email: `user${userId}@suoke.life`,
      role: 'user',
      profile: {
        fullName: `用户${userId}`,
        avatar: '/uploads/avatars/default.png',
        phone: '138xxxx' + String(userId).padStart(4, '0'),
        address: '北京市',
        createdAt: '2023-01-01T00:00:00Z'
      }
    });
  } else {
    res.status(404).json({ error: '用户不存在' });
  }
});

// 文件上传路由
app.post('/users/:id/avatar', upload.single('avatar'), (req, res) => {
  if (!req.file) {
    fileUploadsTotal.labels('avatar', 'failed').inc();
    return res.status(400).json({ error: '未提供有效的图片文件' });
  }
  
  const userId = parseInt(req.params.id, 10);
  const avatarUrl = `/uploads/avatars/${req.file.filename}`;
  
  fileUploadsTotal.labels('avatar', 'success').inc();
  res.status(200).json({
    success: true,
    message: '头像上传成功',
    data: {
      userId,
      avatarUrl
    }
  });
});

// 启动服务器
app.listen(PORT, () => {
  logger.info(`用户服务已启动，监听端口 ${PORT}`);
  logger.info(`环境: ${process.env.NODE_ENV || 'development'}`);
});

// 处理未捕获的异常
process.on('uncaughtException', (error) => {
  logger.error('未捕获的异常:', { error: error.message, stack: error.stack });
  // 在生产环境中，可能需要通知管理员或重启服务
});

// 处理未处理的Promise拒绝
process.on('unhandledRejection', (reason, promise) => {
  logger.error('未处理的Promise拒绝:', { reason });
  // 在生产环境中，可能需要通知管理员
});

// 优雅关闭
process.on('SIGTERM', () => {
  logger.info('收到SIGTERM信号，开始优雅关闭');
  // 等待一段时间允许当前请求完成
  setTimeout(() => {
    process.exit(0);
  }, 5000);
});

module.exports = app;