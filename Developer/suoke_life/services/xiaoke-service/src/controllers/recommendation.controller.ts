import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import recommendationService, { RecommendationService } from '../services/recommendation/recommendation.service';
import { httpRequestsTotal } from '../core/metrics';

/**
 * 推荐控制器
 * 处理与产品和活动推荐相关的HTTP请求
 */
export class RecommendationController {
  private recommendationService: RecommendationService;

  constructor(recommendationService: RecommendationService) {
    this.recommendationService = recommendationService;
  }

  /**
   * 获取个性化产品推荐
   */
  async getPersonalizedProductRecommendations(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/recommendations/products/personalized', 
        status: '200' 
      });

      // @ts-ignore - userId来自auth中间件
      const { userId } = req.user;
      const { limit } = req.query;
      
      const recommendations = await this.recommendationService.getPersonalizedProductRecommendations(
        userId,
        limit ? parseInt(limit as string, 10) : undefined
      );
      
      res.json({
        success: true,
        data: recommendations
      });
    } catch (error) {
      logger.error('获取个性化产品推荐失败:', error);
      res.status(500).json({
        success: false,
        error: '获取个性化产品推荐失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取热门产品推荐
   */
  async getPopularProducts(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/recommendations/products/popular', 
        status: '200' 
      });

      const { limit } = req.query;
      
      const popularProducts = await this.recommendationService.getPopularProducts(
        limit ? parseInt(limit as string, 10) : undefined
      );
      
      res.json({
        success: true,
        data: popularProducts
      });
    } catch (error) {
      logger.error('获取热门产品推荐失败:', error);
      res.status(500).json({
        success: false,
        error: '获取热门产品推荐失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取节气产品推荐
   */
  async getSeasonalProductRecommendations(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/recommendations/products/seasonal', 
        status: '200' 
      });

      const { limit } = req.query;
      
      const seasonalProducts = await this.recommendationService.getSeasonalProductRecommendations(
        limit ? parseInt(limit as string, 10) : undefined
      );
      
      res.json({
        success: true,
        data: seasonalProducts
      });
    } catch (error) {
      logger.error('获取节气产品推荐失败:', error);
      res.status(500).json({
        success: false,
        error: '获取节气产品推荐失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取个性化活动推荐
   */
  async getPersonalizedActivityRecommendations(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/recommendations/activities/personalized', 
        status: '200' 
      });

      // @ts-ignore - userId来自auth中间件
      const { userId } = req.user;
      const { limit } = req.query;
      
      const recommendations = await this.recommendationService.getPersonalizedActivityRecommendations(
        userId,
        limit ? parseInt(limit as string, 10) : undefined
      );
      
      res.json({
        success: true,
        data: recommendations
      });
    } catch (error) {
      logger.error('获取个性化活动推荐失败:', error);
      res.status(500).json({
        success: false,
        error: '获取个性化活动推荐失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取热门活动推荐
   */
  async getPopularActivities(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/recommendations/activities/popular', 
        status: '200' 
      });

      const { limit } = req.query;
      
      const popularActivities = await this.recommendationService.getPopularActivities(
        limit ? parseInt(limit as string, 10) : undefined
      );
      
      res.json({
        success: true,
        data: popularActivities
      });
    } catch (error) {
      logger.error('获取热门活动推荐失败:', error);
      res.status(500).json({
        success: false,
        error: '获取热门活动推荐失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取节气活动推荐
   */
  async getSeasonalActivityRecommendations(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/recommendations/activities/seasonal', 
        status: '200' 
      });

      const { limit } = req.query;
      
      const seasonalActivities = await this.recommendationService.getSeasonalActivityRecommendations(
        limit ? parseInt(limit as string, 10) : undefined
      );
      
      res.json({
        success: true,
        data: seasonalActivities
      });
    } catch (error) {
      logger.error('获取节气活动推荐失败:', error);
      res.status(500).json({
        success: false,
        error: '获取节气活动推荐失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }
}

export default new RecommendationController(recommendationService); 