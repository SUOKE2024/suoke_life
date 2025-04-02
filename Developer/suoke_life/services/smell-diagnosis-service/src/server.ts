import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import promClient from 'prom-client';
import { errorHandler, requestIdMiddleware, requestLoggerMiddleware } from './middlewares/error.middleware';
import smellDiagnosisRoutes from './routes/smell-diagnosis.routes';
import { Logger } from './utils/logger';
import { setupOpenTelemetry } from './utils/telemetry';
import { db } from './database/connection';

// 初始化OpenTelemetry
setupOpenTelemetry();

// 初始化Prometheus
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// 创建指标
const httpRequestDurationMicroseconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

register.registerMetric(httpRequestDurationMicroseconds);
register.registerMetric(httpRequestsTotal);

const logger = new Logger('Server');
const app = express();
const PORT = process.env.PORT || 3002;
const METRICS_PORT = process.env.METRICS_PORT || 9464;

// 中间件
app.use(cors());
app.use(helmet());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(requestIdMiddleware);
app.use(requestLoggerMiddleware);

// 指标中间件
app.use((req, res, next) => {
  const end = httpRequestDurationMicroseconds.startTimer();
  res.on('finish', () => {
    const route = req.route ? req.route.path : req.path;
    const method = req.method;
    const statusCode = res.statusCode.toString();
    
    end({ method, route, status_code: statusCode });
    httpRequestsTotal.inc({ method, route, status_code: statusCode });
  });
  next();
});

// 路由
app.use('/api/smell-diagnosis', smellDiagnosisRoutes);

// 健康检查
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'smell-diagnosis-service' });
});

// 就绪检查
app.get('/ready', async (req, res) => {
  // 检查数据库连接
  if (db.isConnectedToDatabase()) {
    res.status(200).json({ status: 'ready', service: 'smell-diagnosis-service' });
  } else {
    res.status(503).json({ status: 'not ready', service: 'smell-diagnosis-service', message: '数据库未连接' });
  }
});

// 存活检查
app.get('/live', (req, res) => {
  res.status(200).json({ status: 'alive', service: 'smell-diagnosis-service' });
});

// 错误处理
app.use(errorHandler);

// 初始化数据库连接
db.connect().then(() => {
  // 启动主服务
  app.listen(PORT, () => {
    logger.info(`闻诊服务API运行在端口 ${PORT}`);
  });
  
  // 创建指标服务器
  const metricsApp = express();
  metricsApp.get('/metrics', async (req, res) => {
    try {
      res.set('Content-Type', register.contentType);
      res.end(await register.metrics());
    } catch (err) {
      logger.error('指标导出错误', { error: err });
      res.status(500).end();
    }
  });
  
  // 启动指标服务器
  metricsApp.listen(METRICS_PORT, () => {
    logger.info(`指标服务运行在端口 ${METRICS_PORT}`);
  });
}).catch(err => {
  logger.error('启动服务失败', { error: err.message });
  process.exit(1);
});

export default app; 