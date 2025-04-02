/**
 * 玉米迷宫服务主入口文件
 */
require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const bodyParser = require('body-parser');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

// 导入工具和中间件
const logger = require('./src/utils/logger');
const { errorMiddleware } = require('./src/middlewares/errorHandler');

// 导入路由
const mazeRoutes = require('./src/routes/maze.routes');
const treasureRoutes = require('./src/routes/treasure.routes');
const plantRoutes = require('./src/routes/plant.routes');
const teamRoutes = require('./src/routes/team.routes');
const arEnhancedRoutes = require('./src/routes/ar-enhanced.routes');

// 创建Express应用
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// 配置中间件
app.use(helmet()); // 安全头
app.use(cors()); // 跨域支持
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } })); // 请求日志
app.use(bodyParser.json()); // JSON解析
app.use(bodyParser.urlencoded({ extended: true })); // URL编码解析

// 静态文件目录
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/public', express.static(path.join(__dirname, 'public')));

// 健康检查接口
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'corn-maze-service', timestamp: new Date() });
});

// API路由
app.use('/api/mazes', mazeRoutes);
app.use('/api/treasures', treasureRoutes);
app.use('/api/plants', plantRoutes);
app.use('/api/teams', teamRoutes);
app.use('/api/ar', arEnhancedRoutes);

// 默认路由
app.get('/', (req, res) => {
  res.status(200).json({
    name: '玉米迷宫寻宝服务',
    version: process.env.npm_package_version || '1.0.0',
    description: '提供玉米迷宫探索、AR宝藏收集和团队协作功能',
    endpoints: [
      '/api/mazes',
      '/api/treasures',
      '/api/plants',
      '/api/teams',
      '/api/ar'
    ]
  });
});

// 错误处理
app.use(errorMiddleware);

// 配置WebSocket
require('./src/config/socket')(io);

// 连接数据库
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/corn-maze', {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => {
  logger.info('成功连接到MongoDB数据库');
})
.catch(err => {
  logger.error('数据库连接失败:', err);
  process.exit(1);
});

// 启动服务器
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  logger.info(`玉米迷宫服务已启动，监听端口: ${PORT}`);
  logger.info(`API文档: http://localhost:${PORT}/public/docs`);
  
  // 检查环境
  if (process.env.NODE_ENV === 'development') {
    logger.info('开发模式: 已启用调试功能');
  } else {
    logger.info('生产模式: 已优化性能和安全性');
  }
});

// 处理未捕获的异常
process.on('uncaughtException', (err) => {
  logger.error('未捕获的异常:', err);
});

// 处理未处理的Promise拒绝
process.on('unhandledRejection', (reason, promise) => {
  logger.error('未处理的Promise拒绝:', reason);
});

// 处理关闭信号
process.on('SIGTERM', () => {
  logger.info('收到SIGTERM信号，正在优雅关闭服务...');
  server.close(() => {
    mongoose.connection.close(false, () => {
      logger.info('MongoDB连接已关闭');
      process.exit(0);
    });
  });
});

module.exports = { app, server };
