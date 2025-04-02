import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import visualizationService, { TraceabilityVisualizationService } from '../services/traceability/visualization.service';
import { httpRequestsTotal } from '../core/metrics';

/**
 * 溯源可视化控制器
 * 处理与溯源数据可视化和分析相关的HTTP请求
 */
export class VisualizationController {
  private visualizationService: TraceabilityVisualizationService;

  constructor(visualizationService: TraceabilityVisualizationService) {
    this.visualizationService = visualizationService;
  }

  /**
   * 获取溯源链数据（用于前端绘制流程图）
   */
  async getTraceabilityChain(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/visualization/chain/:id', 
        status: '200' 
      });

      const { id } = req.params;
      
      const chainData = await this.visualizationService.getTraceabilityChain(id);
      
      if (!chainData) {
        res.status(404).json({
          success: false,
          error: '溯源链数据不存在',
          code: 'TRACEABILITY_CHAIN_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: chainData
      });
    } catch (error) {
      logger.error('获取溯源链数据失败:', error);
      res.status(500).json({
        success: false,
        error: '获取溯源链数据失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取供应链地理分布数据（用于地图可视化）
   */
  async getSupplyChainGeoDistribution(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/visualization/geo-distribution', 
        status: '200' 
      });

      const { category } = req.query;
      
      const geoData = await this.visualizationService.getSupplyChainGeoDistribution(
        category as string
      );
      
      res.json({
        success: true,
        data: geoData
      });
    } catch (error) {
      logger.error('获取供应链地理分布数据失败:', error);
      res.status(500).json({
        success: false,
        error: '获取供应链地理分布数据失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取溯源数据分析和趋势
   */
  async getTraceabilityAnalytics(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/visualization/analytics', 
        status: '200' 
      });

      const { startDate, endDate } = req.query;
      
      const analyticsData = await this.visualizationService.getTraceabilityAnalytics(
        startDate as string,
        endDate as string
      );
      
      res.json({
        success: true,
        data: analyticsData
      });
    } catch (error) {
      logger.error('获取溯源数据分析失败:', error);
      res.status(500).json({
        success: false,
        error: '获取溯源数据分析失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取质量监控数据
   */
  async getQualityMonitoringData(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/visualization/quality-monitoring', 
        status: '200' 
      });

      const { productId } = req.query;
      
      const qualityData = await this.visualizationService.getQualityMonitoringData(
        productId as string
      );
      
      res.json({
        success: true,
        data: qualityData
      });
    } catch (error) {
      logger.error('获取质量监控数据失败:', error);
      res.status(500).json({
        success: false,
        error: '获取质量监控数据失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }
}

export default new VisualizationController(visualizationService); 