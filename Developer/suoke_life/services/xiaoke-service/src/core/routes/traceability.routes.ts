import { Router } from 'express';
import { Server } from 'socket.io';
import traceabilityController from '../../controllers/traceability.controller';
import { auth } from '../middleware/auth.middleware';

/**
 * 溯源路由
 * 处理与产品溯源相关的HTTP路由
 */
export default function(io: Server): Router {
  const router = Router();

  // 为Websocket实时通知设置响应拦截器中间件
  const captureResponseData = (req: any, res: any, next: () => void) => {
    const originalJson = res.json;
    res.json = function(data: any) {
      res.locals.responseData = data;
      return originalJson.call(this, data);
    };
    next();
  };

  // 获取溯源信息 - 公共接口
  router.get('/:id', 
    captureResponseData,
    async (req, res) => {
      await traceabilityController.getTraceabilityById(req, res);
      
      // 记录溯源查询活动
      if (res.locals.responseData && res.locals.responseData.success) {
        io.emit('traceability:scan', {
          id: req.params.id,
          timestamp: new Date(),
          product: res.locals.responseData.data.productName,
          location: req.query.location || '未知位置'
        });
      }
    }
  );

  // 根据产品ID获取溯源信息 - 公共接口
  router.get('/product/:productId', 
    captureResponseData,
    async (req, res) => {
      await traceabilityController.getTraceabilityByProductId(req, res);
      
      // 记录产品溯源查询活动
      if (res.locals.responseData && res.locals.responseData.success) {
        io.emit('traceability:product-scan', {
          productId: req.params.productId,
          timestamp: new Date(),
          product: res.locals.responseData.data.productName,
          location: req.query.location || '未知位置'
        });
      }
    }
  );

  // 创建溯源信息 - 需要管理员权限
  router.post('/', 
    auth(['admin', 'producer']), 
    captureResponseData,
    async (req, res) => {
      await traceabilityController.createTraceability(req, res);
      
      // 通知管理员溯源信息创建成功
      if (res.locals.responseData && res.locals.responseData.success) {
        io.to('admin').emit('traceability:created', {
          id: res.locals.responseData.data.traceabilityId,
          product: res.locals.responseData.data.productName,
          timestamp: new Date(),
          creator: req.user?.name || req.user?.username || '未知用户'
        });
      }
    }
  );

  // 验证区块链记录 - 公共接口
  router.get('/verify/:txId', 
    captureResponseData,
    async (req, res) => {
      await traceabilityController.verifyBlockchainRecord(req, res);
      
      // 记录验证活动
      if (res.locals.responseData && res.locals.responseData.success) {
        io.emit('traceability:verification', {
          txId: req.params.txId,
          timestamp: new Date(),
          result: res.locals.responseData.data.verified ? '验证成功' : '验证失败',
          product: res.locals.responseData.data.productName || '未知产品'
        });
      }
    }
  );

  // 获取溯源统计信息 - 需要管理员权限
  router.get('/stats', auth(['admin']), async (req, res) => {
    await traceabilityController.getTraceabilityStats(req, res);
  });

  return router;
} 