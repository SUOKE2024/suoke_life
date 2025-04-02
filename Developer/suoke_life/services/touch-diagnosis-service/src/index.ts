import express from 'express';
import cors from 'cors';
import { json, urlencoded } from 'body-parser';
import helmet from 'helmet';
import dotenv from 'dotenv';
import compression from 'compression';

// 加载环境变量
dotenv.config();

// 导入路由
import touchDiagnosisRoutes from './routes/touch-diagnosis.route';

// 导入日志和数据库连接
import { Logger } from './utils/logger';
import { connectToDatabase } from './database/connection';

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 3004;
const API_PREFIX = process.env.API_PREFIX || '/api/touch-diagnosis';

// 中间件配置
app.use(cors());
app.use(helmet());
app.use(compression());
app.use(json({ limit: '10mb' }));
app.use(urlencoded({ extended: true, limit: '10mb' }));

// 健康检查端点
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'UP', service: 'touch-diagnosis-service' });
});

// 应用路由
app.use(`${API_PREFIX}`, touchDiagnosisRoutes);

// 全局错误处理
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  Logger.error(`Error: ${err.message}`, { stack: err.stack, path: req.path });
  res.status(err.status || 500).json({
    error: {
      message: err.message || '服务器内部错误',
      status: err.status || 500
    }
  });
});

// 启动服务器
const startServer = async () => {
  try {
    // 连接数据库
    await connectToDatabase();
    Logger.info('成功连接到MongoDB数据库');

    // 启动服务器
    app.listen(PORT, () => {
      Logger.info(`触诊服务已启动，正在监听端口 ${PORT}`);
      Logger.info(`API可通过 ${API_PREFIX} 访问`);
    });
  } catch (error) {
    Logger.error('服务启动失败', { error });
    process.exit(1);
  }
};

// 处理未捕获的异常
process.on('uncaughtException', (error) => {
  Logger.error('未捕获的异常', { error });
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  Logger.error('未处理的Promise拒绝', { reason, promise });
});

// 启动服务器
startServer(); 