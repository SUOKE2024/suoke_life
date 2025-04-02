import express, { Application } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import { Container } from 'typedi';
import config from './config';
import { setupSwagger } from './config/swagger';
import { requestLoggerMiddleware } from './middlewares/request-logger.middleware';
import { errorMiddleware } from './middlewares/error.middleware';
import routes from './routes';
import { logger } from './utils/logger';

/**
 * 应用类
 * 负责初始化Express应用
 */
export class App {
  public app: Application;
  public port: number;

  constructor(port: number) {
    this.app = express();
    this.port = port;

    this.initializeMiddlewares();
    this.initializeRoutes();
    this.initializeSwagger();
    this.initializeErrorHandling();
  }

  private initializeMiddlewares(): void {
    // 安全中间件
    this.app.use(helmet({
      contentSecurityPolicy: process.env.NODE_ENV === 'production' ? undefined : false,
    }));
    
    // CORS设置
    this.app.use(cors({
      origin: config.cors.origin,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-API-KEY']
    }));
    
    // 响应压缩
    this.app.use(compression());
    
    // 请求解析
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    
    // 请求日志记录
    this.app.use(requestLoggerMiddleware);
  }

  private initializeRoutes(): void {
    this.app.use('/api', routes);
  }
  
  private initializeSwagger(): void {
    // 设置API文档
    setupSwagger(this.app);
  }

  private initializeErrorHandling(): void {
    this.app.use(errorMiddleware);
  }

  public listen(): void {
    this.app.listen(this.port, () => {
      logger.info(`🚀 应用已启动：http://localhost:${this.port}`);
      
      if (config.apiDocs.enabled) {
        logger.info(`📚 API文档可通过 http://localhost:${this.port}/api-docs 访问`);
      }
      
      logger.info(`🔍 健康检查地址：http://localhost:${this.port}/api/health`);
      logger.info(`🌐 当前环境：${process.env.NODE_ENV || 'development'}`);
    });
  }
}

export default App;