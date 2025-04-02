/**
 * 知识相关路由
 */
import { Router } from 'express';
import { Server } from 'socket.io';
import { KnowledgeController } from '../controllers/knowledge';
import { createKnowledgeRoutes } from './knowledge';
import { logger } from '../utils/logger';
import { 
  createKnowledgeBaseService, 
  createKnowledgeGraphService,
  createKnowledgeIntegrationService
} from '../services/knowledge';

/**
 * 创建知识服务路由
 */
export default function knowledgeRoutes(io: Server): Router {
  const router = Router();
  logger.info('初始化知识服务路由');
  
  try {
    // 创建服务实例
    const knowledgeBaseService = createKnowledgeBaseService();
    const knowledgeGraphService = createKnowledgeGraphService();
    const knowledgeIntegrationService = createKnowledgeIntegrationService(
      knowledgeBaseService,
      knowledgeGraphService
    );
    
    // 初始化服务
    Promise.all([
      knowledgeBaseService.initialize(),
      knowledgeGraphService.initialize()
    ]).then(() => {
      return knowledgeIntegrationService.initialize();
    }).then(() => {
      logger.info('知识服务已成功初始化');
      
      // 通知客户端服务已就绪
      io.emit('knowledge:ready', { status: 'ready' });
    }).catch(error => {
      logger.error('知识服务初始化失败', error);
      io.emit('knowledge:error', { status: 'error', message: error.message });
    });
    
    // 创建控制器
    const knowledgeController = new KnowledgeController(
      knowledgeBaseService,
      knowledgeGraphService,
      knowledgeIntegrationService
    );
    
    // 获取知识路由
    const knowledgeApiRoutes = createKnowledgeRoutes(knowledgeController);
    
    // 挂载子路由
    router.use('/', knowledgeApiRoutes);
    
    // WebSocket事件处理
    io.on('connection', (socket) => {
      // 知识查询事件
      socket.on('knowledge:search', async (data) => {
        try {
          const result = await knowledgeBaseService.search(data.query, data.options);
          socket.emit('knowledge:search:result', { success: true, result });
        } catch (error) {
          logger.error('知识查询WebSocket错误', error);
          socket.emit('knowledge:search:result', { 
            success: false, 
            error: error.message 
          });
        }
      });
      
      // 产品知识增强事件
      socket.on('knowledge:product:enrich', async (data) => {
        try {
          const result = await knowledgeIntegrationService.enrichProductKnowledge(data.productId);
          socket.emit('knowledge:product:enrich:result', { success: true, result });
        } catch (error) {
          logger.error('产品知识增强WebSocket错误', error);
          socket.emit('knowledge:product:enrich:result', { 
            success: false, 
            error: error.message 
          });
        }
      });
    });
    
  } catch (error) {
    logger.error('知识服务路由初始化失败', error);
    router.use('/', (_req, res) => {
      res.status(500).json({
        success: false,
        error: '知识服务暂不可用',
        message: error.message,
        code: 'KNOWLEDGE_SERVICE_UNAVAILABLE'
      });
    });
  }
  
  return router;
}