import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import activityService, { ActivityService } from '../services/activity/activity.service';
import { AuthenticatedRequest } from '../core/middleware/auth.middleware';
import { httpRequestsTotal } from '../core/metrics';

/**
 * 活动控制器
 * 处理与农事活动相关的HTTP请求
 */
export class ActivityController {
  private activityService: ActivityService;

  constructor(activityService: ActivityService) {
    this.activityService = activityService;
  }

  /**
   * 获取活动列表
   */
  getActivities = async (req: Request, res: Response): Promise<void> => {
    try {
      const { 
        category, 
        query, 
        location, 
        startDate, 
        endDate, 
        sort = 'startDate_asc',
        limit = 20, 
        skip = 0 
      } = req.query;

      const result = await this.activityService.getActivities({
        category: category as string,
        query: query as string,
        location: location as string,
        startDate: startDate as string,
        endDate: endDate as string,
        sort: sort as string,
        limit: Number(limit),
        skip: Number(skip)
      });

      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities',
        status: '200'
      });

      res.status(200).json(result);
    } catch (error) {
      logger.error('获取活动列表失败', error);
      
      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities',
        status: '500'
      });
      
      res.status(500).json({ 
        error: '获取活动列表失败', 
        message: (error as Error).message 
      });
    }
  };

  /**
   * 获取活动详情
   */
  getActivityById = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params;
      const activity = await this.activityService.getActivityById(id);

      if (!activity) {
        // 记录指标
        httpRequestsTotal.inc({
          method: req.method,
          path: '/api/v1/activities/:id',
          status: '404'
        });
        
        res.status(404).json({ error: '活动不存在' });
        return;
      }

      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities/:id',
        status: '200'
      });
      
      res.status(200).json(activity);
    } catch (error) {
      logger.error(`获取活动详情失败: ${req.params.id}`, error);
      
      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities/:id',
        status: '500'
      });
      
      res.status(500).json({ 
        error: '获取活动详情失败', 
        message: (error as Error).message 
      });
    }
  };

  /**
   * 预约活动
   */
  registerForActivity = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
    try {
      const { id } = req.params;
      const { participants } = req.body;
      const userId = req.user?.id;

      if (!userId) {
        // 记录指标
        httpRequestsTotal.inc({
          method: req.method,
          path: '/api/v1/activities/:id/register',
          status: '401'
        });
        
        res.status(401).json({ error: '用户未认证' });
        return;
      }

      if (!participants || participants < 1) {
        // 记录指标
        httpRequestsTotal.inc({
          method: req.method,
          path: '/api/v1/activities/:id/register',
          status: '400'
        });
        
        res.status(400).json({ error: '参与人数必须大于0' });
        return;
      }

      const result = await this.activityService.registerForActivity(id, userId, participants);

      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities/:id/register',
        status: '200'
      });
      
      res.status(200).json({ success: true, message: '活动预约成功' });
    } catch (error) {
      logger.error(`预约活动失败: ${req.params.id}`, error);
      
      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities/:id/register',
        status: '500'
      });
      
      const errorMessage = (error as Error).message;
      
      if (errorMessage.includes('已经预约过')) {
        res.status(400).json({ error: errorMessage });
      } else if (errorMessage.includes('名额不足')) {
        res.status(400).json({ error: errorMessage });
      } else if (errorMessage.includes('不存在')) {
        res.status(404).json({ error: errorMessage });
      } else {
        res.status(500).json({ 
          error: '预约活动失败', 
          message: errorMessage 
        });
      }
    }
  };

  /**
   * 添加活动评价
   */
  addActivityReview = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
    try {
      const { id } = req.params;
      const { rating, comment, photoUrls } = req.body;
      const userId = req.user?.id;

      if (!userId) {
        // 记录指标
        httpRequestsTotal.inc({
          method: req.method,
          path: '/api/v1/activities/:id/review',
          status: '401'
        });
        
        res.status(401).json({ error: '用户未认证' });
        return;
      }

      if (!rating || rating < 1 || rating > 5) {
        // 记录指标
        httpRequestsTotal.inc({
          method: req.method,
          path: '/api/v1/activities/:id/review',
          status: '400'
        });
        
        res.status(400).json({ error: '评分必须在1-5之间' });
        return;
      }

      if (!comment || comment.trim().length === 0) {
        // 记录指标
        httpRequestsTotal.inc({
          method: req.method,
          path: '/api/v1/activities/:id/review',
          status: '400'
        });
        
        res.status(400).json({ error: '评论内容不能为空' });
        return;
      }

      const activity = await this.activityService.addActivityReview(id, {
        userId,
        rating,
        comment,
        photoUrls
      });

      if (!activity) {
        // 记录指标
        httpRequestsTotal.inc({
          method: req.method,
          path: '/api/v1/activities/:id/review',
          status: '404'
        });
        
        res.status(404).json({ error: '活动不存在' });
        return;
      }

      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities/:id/review',
        status: '200'
      });
      
      res.status(200).json({ 
        success: true, 
        message: '评价提交成功', 
        activity 
      });
    } catch (error) {
      logger.error(`添加活动评价失败: ${req.params.id}`, error);
      
      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities/:id/review',
        status: '500'
      });
      
      res.status(500).json({ 
        error: '添加活动评价失败', 
        message: (error as Error).message 
      });
    }
  };

  /**
   * 获取热门活动
   */
  getPopularActivities = async (req: Request, res: Response): Promise<void> => {
    try {
      const { limit = 5 } = req.query;
      const activities = await this.activityService.getPopularActivities(Number(limit));

      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities/popular',
        status: '200'
      });
      
      res.status(200).json(activities);
    } catch (error) {
      logger.error('获取热门活动失败', error);
      
      // 记录指标
      httpRequestsTotal.inc({
        method: req.method,
        path: '/api/v1/activities/popular',
        status: '500'
      });
      
      res.status(500).json({ 
        error: '获取热门活动失败', 
        message: (error as Error).message 
      });
    }
  };
}

export default new ActivityController(activityService); 