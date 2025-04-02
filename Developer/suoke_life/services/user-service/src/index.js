/**
 * 索克生活APP用户服务入口文件
 */
const express = require('express');
const helmet = require('helmet');
const compression = require('compression');
const cors = require('cors');
const { loggerMiddleware, errorMiddleware } = require('@suoke/shared').middlewares;
const { logger } = require('@suoke/shared').utils;
const routes = require('./routes');
const config = require('./config');

// 创建Express应用
const app = express();

// 使用中间件
app.use(helmet());
app.use(compression());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(loggerMiddleware);

// 注册路由
app.use('/api/v1/users', routes.userRoutes);
app.use('/api/v1/profiles', routes.profileRoutes);
app.use('/api/v1/health-profiles', routes.healthProfileRoutes);

// 错误处理中间件
app.use(errorMiddleware);

// 健康检查
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'UP', service: 'user-service' });
});

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  logger.info(`用户服务已启动，监听端口: ${PORT}`);
}); 