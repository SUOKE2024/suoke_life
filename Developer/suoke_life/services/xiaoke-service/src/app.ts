import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { logger } from './utils/logger';

// 导入路由
import supplyChainRoutes from './routes/supply-chain.routes';
import consumerRoutes from './routes/consumer.routes';
import iotRoutes from './routes/iot.routes';
import predictionRoutes from './routes/prediction.routes';
import blockchainRoutes from './routes/blockchain.routes';

// 初始化区块链连接
import { initializeBlockchain } from './services/blockchain/supply-chain-blockchain';

class App {
  public app: express.Application;

  constructor() {
    this.app = express();
    this.configureMiddleware();
    this.configureRoutes();
    this.initializeServices();
  }

  private configureMiddleware(): void {
    // 基础中间件
    this.app.use(cors());
    this.app.use(helmet());
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
    this.app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));
  }

  private configureRoutes(): void {
    // 健康检查
    this.app.get('/health', (req, res) => {
      res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    // API 路由
    this.app.use('/api/supply-chain', supplyChainRoutes());
    this.app.use('/api/consumer', consumerRoutes());
    this.app.use('/api/iot', iotRoutes());
    this.app.use('/api/prediction', predictionRoutes());
    this.app.use('/api/blockchain', blockchainRoutes());

    // 捕获 404 错误并转发到错误处理器
    this.app.use((req, res, next) => {
      const err: any = new Error('Not Found');
      err.status = 404;
      next(err);
    });

    // 错误处理器
    this.app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
      logger.error(`Error: ${err.message}`, { error: err });
      res.status(err.status || 500).json({
        success: false,
        message: err.message || '服务器内部错误',
        error: process.env.NODE_ENV === 'development' ? err : {}
      });
    });
  }

  private async initializeServices(): Promise<void> {
    try {
      // 初始化区块链连接
      await initializeBlockchain();
      logger.info('服务初始化完成');
    } catch (error) {
      logger.error('服务初始化失败:', error);
    }
  }
}

export default new App().app;