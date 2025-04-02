/**
 * 知识库服务主应用程序
 */

import express, { Express, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import { v4 as uuidv4 } from 'uuid';
import swaggerUi from 'swagger-ui-express';
import swaggerJsDoc from 'swagger-jsdoc';
import routes from './routes';
import logger from './utils/logger';
import { connectToDatabase } from './utils/database';
import { connectToRedis } from './utils/redis';

// 创建Express应用
const app: Express = express();

// 连接数据库
connectToDatabase().catch((err) => {
  logger.error('数据库连接失败', { error: err });
  process.exit(1);
});

// 连接Redis
connectToRedis().catch((err) => {
  logger.error('Redis连接失败', { error: err });
  // 继续运行，Redis不是强制依赖
});

// 配置Swagger
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: '知识库服务API文档',
      version: '1.0.0',
      description: '索克生活知识库服务API接口文档',
    },
    servers: [
      {
        url: process.env.API_BASE_URL || 'http://localhost:3002',
        description: '开发服务器',
      },
    ],
  },
  apis: ['./src/routes/*.ts'], // API路由文件的路径
};

const swaggerSpec = swaggerJsDoc(swaggerOptions);

// 添加请求ID中间件
app.use((req: Request, res: Response, next: NextFunction) => {
  req.headers['x-request-id'] = req.headers['x-request-id'] || uuidv4();
  next();
});

// 配置日志中间件
app.use(morgan('combined', {
  stream: {
    write: (message: string) => {
      logger.info(message.trim());
    },
  },
}));

// 安全相关中间件
app.use(helmet());
app.use(cors());

// 请求解析中间件
app.use(express.json({ limit: process.env.MAX_CONTENT_SIZE || '10mb' }));
app.use(express.urlencoded({ extended: true, limit: process.env.MAX_CONTENT_SIZE || '10mb' }));

// 压缩响应
app.use(compression());

// API文档路由
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// 健康检查路由
app.get('/health', (req: Request, res: Response) => {
  res.status(200).json({
    status: 'UP',
    timestamp: new Date().toISOString(),
    service: 'knowledge-base-service',
  });
});

// API路由
app.use('/api', routes);

// 错误处理中间件
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  const requestId = req.headers['x-request-id'] as string;
  
  logger.error(`服务器错误: ${err.message}`, {
    requestId,
    error: err.stack,
  });
  
  res.status(500).json({
    success: false,
    message: '服务器内部错误',
    requestId,
  });
});

// 404处理
app.use((req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    message: '未找到请求的资源',
  });
});

export default app;