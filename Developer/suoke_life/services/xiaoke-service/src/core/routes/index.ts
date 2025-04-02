import express, { Express, Request, Response, NextFunction } from 'express';
import { Server } from 'socket.io';
import userRoutes from '../../routes/user.routes';
import authRoutes from '../../routes/auth.routes';
import productRoutes from '../../routes/product.routes';
import traceabilityRoutes from '../../routes/traceability.routes';
import visualizationRoutes from '../../routes/visualization.routes';
import blockchainRoutes from '../../routes/blockchain.routes';
import seasonalRoutes from '../../routes/seasonal.routes';
import recommendationRoutes from '../../routes/recommendation.routes';
import knowledgeRoutes from '../../routes/knowledge.routes';
import supplyChainRoutes from '../../routes/supply-chain.routes';
import { logger } from '../../utils/logger';
import { httpRequestsTotal } from '../metrics';

/**
 * 设置所有路由
 * @param app Express 应用实例
 * @param io Socket.IO 服务器实例
 */
export const setupRoutes = (app: Express, io: Server): void => {
  // API 前缀
  const apiPrefix = '/api/v1';
  
  // 基础健康检查路由
  app.get('/health', (req: Request, res: Response) => {
    httpRequestsTotal.inc({ method: req.method, path: '/health', status: '200' });
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });
  
  app.get('/', (req: Request, res: Response) => {
    httpRequestsTotal.inc({ method: req.method, path: '/', status: '200' });
    res.json({ 
      name: 'Xiaoke API Service',
      version: process.env.APP_VERSION || '1.0.0',
      environment: process.env.NODE_ENV || 'development'
    });
  });

  // 使用路由模块
  logger.info(`设置API路由，前缀: ${apiPrefix}`);
  
  app.use(`${apiPrefix}/users`, userRoutes(io));
  app.use(`${apiPrefix}/auth`, authRoutes(io));
  app.use(`${apiPrefix}/products`, productRoutes(io));
  app.use(`${apiPrefix}/traceability`, traceabilityRoutes(io));
  app.use(`${apiPrefix}/visualization`, visualizationRoutes(io));
  app.use(`${apiPrefix}/blockchain`, blockchainRoutes(io));
  app.use(`${apiPrefix}/seasonal`, seasonalRoutes(io));
  app.use(`${apiPrefix}/recommendations`, recommendationRoutes(io));
  app.use(`${apiPrefix}/knowledge`, knowledgeRoutes(io));
  app.use(`${apiPrefix}/supply-chain`, supplyChainRoutes(io));

  // 404 处理
  app.use((req: Request, res: Response) => {
    httpRequestsTotal.inc({ method: req.method, path: 'not_found', status: '404' });
    res.status(404).json({
      success: false,
      error: '请求的路径不存在',
      code: 'ROUTE_NOT_FOUND'
    });
  });

  // 全局错误处理
  app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    logger.error('全局错误处理器捕获到错误:', err);
    httpRequestsTotal.inc({ method: req.method, path: req.path, status: '500' });
    
    res.status(500).json({
      success: false,
      error: '服务器内部错误',
      message: process.env.NODE_ENV === 'production' ? '请稍后再试' : err.message,
      code: 'SERVER_ERROR'
    });
  });
};

export default setupRoutes; 