import { Router } from 'express';
import seasonalController from '../controllers/seasonal.controller';
import { validateRequest } from '../middleware/validation.middleware';
import { authenticateJwt } from '../middleware/auth.middleware';
import { Server } from 'socket.io';
import { logger } from '../utils/logger';
import { rateLimit } from '../middleware/rate-limit.middleware';

/**
 * 节气路由配置
 * @param io Socket.IO 服务器实例
 * @returns 配置好的路由
 */
export default function seasonalRoutes(io: Server): Router {
  const router = Router();
  
  logger.info('初始化节气路由...');

  // 公共访问路由 - 基础节气信息
  
  // 获取当前节气信息
  router.get(
    '/current',
    rateLimit(10, 60), // 每分钟最多10次请求
    seasonalController.getCurrentSolarTerm.bind(seasonalController)
  );
  
  // 获取指定日期的节气信息
  router.get(
    '/by-date',
    rateLimit(20, 60), // 每分钟最多20次请求
    validateRequest({
      query: {
        date: { type: 'string', optional: false }
      }
    }),
    seasonalController.getSolarTermByDate.bind(seasonalController)
  );
  
  // 获取所有节气列表
  router.get(
    '/all',
    rateLimit(5, 60), // 每分钟最多5次请求
    seasonalController.getAllSolarTerms.bind(seasonalController)
  );
  
  // 获取下一个节气信息
  router.get(
    '/next',
    rateLimit(10, 60), // 每分钟最多10次请求
    seasonalController.getNextSolarTerm.bind(seasonalController)
  );
  
  // 获取指定ID的节气信息
  router.get(
    '/:id',
    rateLimit(15, 60), // 每分钟最多15次请求
    seasonalController.getSolarTermById.bind(seasonalController)
  );
  
  // 需要认证的路由 - 特定节气功能
  
  // 获取当前节气饮食推荐
  router.get(
    '/dietary-recommendations',
    authenticateJwt,
    rateLimit(15, 60), // 每分钟最多15次请求
    seasonalController.getCurrentDietaryRecommendations.bind(seasonalController)
  );
  
  // 获取当前节气健康建议
  router.get(
    '/health-tips',
    authenticateJwt,
    rateLimit(15, 60), // 每分钟最多15次请求
    seasonalController.getCurrentHealthTips.bind(seasonalController)
  );

  // 设置实时节气通知功能
  io.of('/seasonal').on('connection', (socket) => {
    logger.info(`Socket connected for seasonal updates: ${socket.id}`);
    
    // 当有用户连接时，发送当前节气信息
    seasonalController.seasonalService.getCurrentSolarTerm()
      .then((solarTerm) => {
        if (solarTerm) {
          socket.emit('current-solar-term', solarTerm);
        }
      })
      .catch((error) => {
        logger.error('获取当前节气信息失败:', error);
      });
    
    // 处理断开连接
    socket.on('disconnect', () => {
      logger.info(`Socket disconnected from seasonal updates: ${socket.id}`);
    });
  });

  return router;
} 