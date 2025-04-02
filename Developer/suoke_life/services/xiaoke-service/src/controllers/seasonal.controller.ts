import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import seasonalService, { SeasonalService } from '../services/seasonal/seasonal.service';
import { httpRequestsTotal } from '../core/metrics';

/**
 * 节气控制器
 * 处理与二十四节气相关的HTTP请求
 */
export class SeasonalController {
  private seasonalService: SeasonalService;

  constructor(seasonalService: SeasonalService) {
    this.seasonalService = seasonalService;
  }

  /**
   * 获取当前节气信息
   */
  async getCurrentSolarTerm(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/seasonal/current', 
        status: '200' 
      });

      const solarTerm = await this.seasonalService.getCurrentSolarTerm();
      
      if (!solarTerm) {
        res.status(404).json({
          success: false,
          error: '节气信息不可用',
          code: 'SOLAR_TERM_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: solarTerm
      });
    } catch (error) {
      logger.error('获取当前节气信息失败:', error);
      res.status(500).json({
        success: false,
        error: '获取当前节气信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取指定日期的节气信息
   */
  async getSolarTermByDate(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/seasonal/by-date', 
        status: '200' 
      });

      const { date } = req.query;
      
      if (!date) {
        res.status(400).json({
          success: false,
          error: '日期参数缺失',
          code: 'MISSING_DATE_PARAMETER'
        });
        return;
      }
      
      const solarTerm = await this.seasonalService.getSolarTermByDate(date as string);
      
      if (!solarTerm) {
        res.status(404).json({
          success: false,
          error: '节气信息不可用',
          code: 'SOLAR_TERM_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: solarTerm
      });
    } catch (error) {
      logger.error('获取指定日期节气信息失败:', error);
      res.status(500).json({
        success: false,
        error: '获取指定日期节气信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取指定节气信息
   */
  async getSolarTermById(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/seasonal/:id', 
        status: '200' 
      });

      const { id } = req.params;
      
      const solarTerm = await this.seasonalService.getSolarTermById(id);
      
      if (!solarTerm) {
        res.status(404).json({
          success: false,
          error: '节气信息不存在',
          code: 'SOLAR_TERM_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: solarTerm
      });
    } catch (error) {
      logger.error('获取指定节气信息失败:', error);
      res.status(500).json({
        success: false,
        error: '获取指定节气信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取所有节气列表
   */
  async getAllSolarTerms(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/seasonal/all', 
        status: '200' 
      });

      const solarTerms = await this.seasonalService.getAllSolarTerms();
      
      res.json({
        success: true,
        data: solarTerms
      });
    } catch (error) {
      logger.error('获取所有节气列表失败:', error);
      res.status(500).json({
        success: false,
        error: '获取所有节气列表失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取当前节气饮食推荐
   */
  async getCurrentDietaryRecommendations(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/seasonal/dietary-recommendations', 
        status: '200' 
      });

      const recommendations = await this.seasonalService.getCurrentDietaryRecommendations();
      
      if (!recommendations) {
        res.status(404).json({
          success: false,
          error: '节气饮食推荐不可用',
          code: 'DIETARY_RECOMMENDATIONS_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: recommendations
      });
    } catch (error) {
      logger.error('获取当前节气饮食推荐失败:', error);
      res.status(500).json({
        success: false,
        error: '获取当前节气饮食推荐失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取当前节气健康建议
   */
  async getCurrentHealthTips(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/seasonal/health-tips', 
        status: '200' 
      });

      const healthTips = await this.seasonalService.getCurrentHealthTips();
      
      if (!healthTips) {
        res.status(404).json({
          success: false,
          error: '节气健康建议不可用',
          code: 'HEALTH_TIPS_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: healthTips
      });
    } catch (error) {
      logger.error('获取当前节气健康建议失败:', error);
      res.status(500).json({
        success: false,
        error: '获取当前节气健康建议失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取下一个节气信息
   */
  async getNextSolarTerm(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/seasonal/next', 
        status: '200' 
      });

      const solarTerm = await this.seasonalService.getNextSolarTerm();
      
      if (!solarTerm) {
        res.status(404).json({
          success: false,
          error: '下一节气信息不可用',
          code: 'NEXT_SOLAR_TERM_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: solarTerm
      });
    } catch (error) {
      logger.error('获取下一节气信息失败:', error);
      res.status(500).json({
        success: false,
        error: '获取下一节气信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }
}

export default new SeasonalController(seasonalService); 