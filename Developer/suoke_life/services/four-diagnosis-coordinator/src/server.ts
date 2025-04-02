import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { 
  errorHandler, 
  notFoundHandler, 
  requestIdMiddleware, 
  requestLoggerMiddleware 
} from './middlewares/error.middleware';
import fourDiagnosisRoutes from './routes/four-diagnosis-coordinator.routes';
import { Logger } from './utils/logger';

const logger = new Logger('Server');
const app = express();
const PORT = process.env.PORT || 3050;

// 中间件
app.use(cors());
app.use(helmet());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(requestIdMiddleware);
app.use(requestLoggerMiddleware);

// 路由
app.use('/api/four-diagnosis', fourDiagnosisRoutes);

// 健康检查
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'four-diagnosis-coordinator-service' });
});

// 404处理
app.use(notFoundHandler);

// 错误处理
app.use(errorHandler);

// 启动服务器
app.listen(PORT, () => {
  logger.info(`四诊协调服务运行在端口 ${PORT}`);
});

export default app;
