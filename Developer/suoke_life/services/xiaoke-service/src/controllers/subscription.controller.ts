import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import subscriptionService, { SubscriptionService } from '../services/subscription/subscription.service';
import { AuthenticatedRequest } from '../core/middleware/auth.middleware';
import { httpRequestsTotal } from '../core/metrics';

/**
 * 订阅控制器
 * 处理与服务订阅相关的HTTP请求
 */
export class SubscriptionController {
  private subscriptionService: SubscriptionService;

  constructor(subscriptionService: SubscriptionService) {
    this.subscriptionService = subscriptionService;
  }

  /**
   * 创建订阅
   */
  async createSubscription(req: AuthenticatedRequest, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/subscriptions', 
        status: '200' 
      });

      const { userId } = req.user;
      const subscriptionData = {
        ...req.body,
        userId
      };
      
      const subscription = await this.subscriptionService.createSubscription(subscriptionData);
      
      res.status(201).json({
        success: true,
        data: subscription
      });
    } catch (error) {
      logger.error('创建订阅失败:', error);
      res.status(500).json({
        success: false,
        error: '创建订阅失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取订阅详情
   */
  async getSubscriptionById(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/subscriptions/:id', 
        status: '200' 
      });

      const { id } = req.params;
      
      const subscription = await this.subscriptionService.getSubscriptionById(id);
      
      if (!subscription) {
        res.status(404).json({
          success: false,
          error: '订阅不存在',
          code: 'SUBSCRIPTION_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: subscription
      });
    } catch (error) {
      logger.error('获取订阅详情失败:', error);
      res.status(500).json({
        success: false,
        error: '获取订阅详情失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取用户订阅列表
   */
  async getUserSubscriptions(req: AuthenticatedRequest, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/subscriptions/user', 
        status: '200' 
      });

      const { userId } = req.user;
      
      const subscriptions = await this.subscriptionService.getUserSubscriptions(userId);
      
      res.json({
        success: true,
        data: {
          subscriptions,
          total: subscriptions.length
        }
      });
    } catch (error) {
      logger.error('获取用户订阅列表失败:', error);
      res.status(500).json({
        success: false,
        error: '获取用户订阅列表失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 更新订阅状态
   */
  async updateSubscriptionStatus(req: AuthenticatedRequest, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/subscriptions/:id/status', 
        status: '200' 
      });

      const { id } = req.params;
      const { status } = req.body;
      
      const subscription = await this.subscriptionService.updateSubscriptionStatus(id, status);
      
      if (!subscription) {
        res.status(404).json({
          success: false,
          error: '订阅不存在',
          code: 'SUBSCRIPTION_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: subscription
      });
    } catch (error) {
      logger.error('更新订阅状态失败:', error);
      res.status(500).json({
        success: false,
        error: '更新订阅状态失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 续订服务
   */
  async renewSubscription(req: AuthenticatedRequest, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/subscriptions/:id/renew', 
        status: '200' 
      });

      const { id } = req.params;
      const { duration } = req.body;
      
      const subscription = await this.subscriptionService.renewSubscription(id, duration);
      
      if (!subscription) {
        res.status(404).json({
          success: false,
          error: '订阅不存在',
          code: 'SUBSCRIPTION_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: subscription
      });
    } catch (error) {
      logger.error('续订服务失败:', error);
      res.status(500).json({
        success: false,
        error: '续订服务失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }
}

export default new SubscriptionController(subscriptionService); 