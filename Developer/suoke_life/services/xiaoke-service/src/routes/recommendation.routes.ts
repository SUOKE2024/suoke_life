import { Router } from 'express';
import recommendationController from '../controllers/recommendation.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { Server } from 'socket.io';
import { logger } from '../utils/logger';
import { rateLimit } from '../middleware/rate-limit.middleware';
import { RecommendationService } from '../services/recommendation/recommendation.service';
import { requireAuth } from '../core/middleware/auth.middleware';

/**
 * 推荐路由配置
 * @param io Socket.IO 服务器实例
 * @returns 配置好的路由
 */
export default function recommendationRoutes(io: Server): Router {
  const router = Router();
  const recommendationService = new RecommendationService();
  
  logger.info('初始化推荐路由...');

  // 产品推荐路由
  
  // 获取个性化产品推荐 - 需要用户认证
  router.get(
    '/products/personalized',
    requireAuth,
    rateLimit(20, 60), // 每分钟最多20次请求
    async (req, res) => {
      try {
        const userId = req.user.id;
        const limit = parseInt(req.query.limit as string) || 10;
        
        const userProfile = await recommendationService.getUserProfile(userId);
        const recommendations = await recommendationService.getPersonalizedProductRecommendations(userProfile, limit);
        
        res.json({ success: true, recommendations });
      } catch (error) {
        logger.error('获取个性化产品推荐失败', error);
        res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
      }
    }
  );
  
  // 获取热门产品推荐 - 公开访问
  router.get(
    '/products/popular',
    rateLimit(30, 60), // 每分钟最多30次请求
    async (req, res) => {
      try {
        const limit = parseInt(req.query.limit as string) || 10;
        const recommendations = await recommendationService.getPopularProducts(limit);
        
        res.json({ success: true, recommendations });
      } catch (error) {
        logger.error('获取热门产品推荐失败', error);
        res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
      }
    }
  );
  
  // 获取节气产品推荐 - 公开访问
  router.get(
    '/products/seasonal',
    rateLimit(30, 60), // 每分钟最多30次请求
    async (req, res) => {
      try {
        const limit = parseInt(req.query.limit as string) || 10;
        const recommendations = await recommendationService.getSeasonalProductRecommendations(limit);
        
        res.json({ success: true, recommendations });
      } catch (error) {
        logger.error('获取季节性产品推荐失败', error);
        res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
      }
    }
  );
  
  // 获取节气相关产品推荐
  router.get('/products/solar-term/:solarTerm', requireAuth, async (req, res) => {
    try {
      const { solarTerm } = req.params;
      const userId = req.user.id;
      const limit = parseInt(req.query.limit as string) || 10;
      
      const userProfile = await recommendationService.getUserProfile(userId);
      const recommendations = await recommendationService.getSolarTermProductRecommendations(solarTerm, userProfile, limit);
      
      res.json({ success: true, recommendations });
    } catch (error) {
      logger.error(`获取节气产品推荐失败: ${req.params.solarTerm}`, error);
      res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
    }
  });
  
  // 获取健康导向产品推荐
  router.post('/products/health-oriented', requireAuth, async (req, res) => {
    try {
      const userId = req.user.id;
      const { healthConcepts } = req.body;
      const limit = parseInt(req.query.limit as string) || 10;
      
      if (!healthConcepts || !Array.isArray(healthConcepts) || healthConcepts.length === 0) {
        return res.status(400).json({ 
          success: false, 
          error: '请提供有效的健康概念列表' 
        });
      }
      
      const userProfile = await recommendationService.getUserProfile(userId);
      const recommendations = await recommendationService.getHealthOrientedProductRecommendations(
        userProfile,
        healthConcepts,
        limit
      );
      
      res.json({ success: true, recommendations });
    } catch (error) {
      logger.error('获取健康导向产品推荐失败', error);
      res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
    }
  });
  
  // 活动推荐路由
  
  // 获取个性化活动推荐 - 需要用户认证
  router.get(
    '/activities/personalized',
    authenticateJwt,
    rateLimit(20, 60), // 每分钟最多20次请求
    recommendationController.getPersonalizedActivityRecommendations.bind(recommendationController)
  );
  
  // 获取热门活动推荐 - 公开访问
  router.get(
    '/activities/popular',
    rateLimit(30, 60), // 每分钟最多30次请求
    recommendationController.getPopularActivities.bind(recommendationController)
  );
  
  // 获取节气活动推荐 - 公开访问
  router.get(
    '/activities/seasonal',
    rateLimit(30, 60), // 每分钟最多30次请求
    recommendationController.getSeasonalActivityRecommendations.bind(recommendationController)
  );

  // 设置实时推荐通知功能
  io.of('/recommendations').on('connection', (socket) => {
    logger.info(`Socket connected for recommendations: ${socket.id}`);
    
    // 当用户登录时，可发送个性化推荐
    socket.on('user-login', async (userData: { userId: string }) => {
      try {
        const { userId } = userData;
        
        // 获取个性化产品推荐
        const productRecommendations = await recommendationController.recommendationService.getPersonalizedProductRecommendations(userId, 5);
        socket.emit('personalized-product-recommendations', productRecommendations);
        
        // 获取个性化活动推荐
        const activityRecommendations = await recommendationController.recommendationService.getPersonalizedActivityRecommendations(userId, 3);
        socket.emit('personalized-activity-recommendations', activityRecommendations);
      } catch (error) {
        logger.error('发送个性化推荐失败:', error);
      }
    });
    
    // 处理断开连接
    socket.on('disconnect', () => {
      logger.info(`Socket disconnected from recommendations: ${socket.id}`);
    });
  });

  // WebSocket事件处理
  io.on('connection', (socket) => {
    socket.on('request_health_recommendations', async (data) => {
      try {
        const { userId, healthConcepts, limit } = data;
        
        if (!userId || !healthConcepts || !Array.isArray(healthConcepts)) {
          socket.emit('health_recommendations_error', { 
            error: '无效的请求参数'
          });
          return;
        }
        
        const userProfile = await recommendationService.getUserProfile(userId);
        const recommendations = await recommendationService.getHealthOrientedProductRecommendations(
          userProfile,
          healthConcepts,
          limit || 10
        );
        
        socket.emit('health_recommendations_result', { recommendations });
      } catch (error) {
        logger.error('WebSocket健康产品推荐请求失败', error);
        socket.emit('health_recommendations_error', { 
          error: '获取健康产品推荐失败',
          message: error.message
        });
      }
    });
  });

  return router;
} 