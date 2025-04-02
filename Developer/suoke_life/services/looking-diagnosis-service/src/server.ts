import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { errorHandler } from './middlewares/error.middleware';
import lookingDiagnosisRoutes from './routes/looking-diagnosis.routes';
import logger from './utils/logger';
import { db } from './config/database';

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 3001;

// 中间件
app.use(cors());
app.use(helmet());
app.use(morgan('combined'));
app.use(express.json({ limit: '50mb' })); // 增加限制以处理大型图像
app.use(express.urlencoded({ extended: true }));

// 路由
app.use('/api/looking-diagnosis', lookingDiagnosisRoutes);

// 健康检查
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'looking-diagnosis-service' });
});

// 错误处理
app.use(errorHandler);

// 启动数据库连接并启动服务器
const startServer = async () => {
  try {
    // 连接到MongoDB
    await db.connect();
    
    // 启动服务器
    app.listen(PORT, () => {
      logger.info(`望诊服务运行在端口 ${PORT}`);
    });
  } catch (error) {
    logger.error(`服务启动失败: ${error.message}`);
    process.exit(1);
  }
};

// 启动服务
startServer();

export default app;
