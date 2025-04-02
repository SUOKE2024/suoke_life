import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import traceabilityService, { TraceabilityService } from '../services/traceability/traceability.service';
import { httpRequestsTotal } from '../core/metrics';

/**
 * 溯源控制器
 * 处理与产品溯源相关的HTTP请求
 */
export class TraceabilityController {
  private traceabilityService: TraceabilityService;

  constructor(traceabilityService: TraceabilityService) {
    this.traceabilityService = traceabilityService;
  }

  /**
   * 根据溯源ID获取溯源信息
   */
  async getTraceabilityById(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/traceability/:id', 
        status: '200' 
      });

      const { id } = req.params;
      
      const traceability = await this.traceabilityService.getTraceabilityById(id);
      
      if (!traceability) {
        res.status(404).json({
          success: false,
          error: '溯源信息不存在',
          code: 'TRACEABILITY_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: traceability
      });
    } catch (error) {
      logger.error('获取溯源信息失败:', error);
      res.status(500).json({
        success: false,
        error: '获取溯源信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 根据产品ID获取溯源信息
   */
  async getTraceabilityByProductId(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/traceability/product/:productId', 
        status: '200' 
      });

      const { productId } = req.params;
      
      const traceability = await this.traceabilityService.getTraceabilityByProductId(productId);
      
      if (!traceability) {
        res.status(404).json({
          success: false,
          error: '产品溯源信息不存在',
          code: 'PRODUCT_TRACEABILITY_NOT_FOUND'
        });
        return;
      }
      
      res.json({
        success: true,
        data: traceability
      });
    } catch (error) {
      logger.error('获取产品溯源信息失败:', error);
      res.status(500).json({
        success: false,
        error: '获取产品溯源信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 创建新的溯源信息
   */
  async createTraceability(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/traceability', 
        status: '201' 
      });

      const traceabilityData = req.body;
      
      const traceability = await this.traceabilityService.createTraceability(traceabilityData);
      
      res.status(201).json({
        success: true,
        data: traceability
      });
    } catch (error) {
      logger.error('创建溯源信息失败:', error);
      
      // 特定错误处理
      if (error instanceof Error && error.message.includes('产品不存在')) {
        res.status(400).json({
          success: false,
          error: '产品不存在',
          message: error.message,
          code: 'PRODUCT_NOT_FOUND'
        });
        return;
      }
      
      res.status(500).json({
        success: false,
        error: '创建溯源信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 验证区块链溯源信息
   */
  async verifyBlockchainRecord(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/traceability/verify/:txId', 
        status: '200' 
      });

      const { txId } = req.params;
      
      const result = await this.traceabilityService.verifyBlockchainRecord(txId);
      
      res.json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('验证溯源信息失败:', error);
      res.status(500).json({
        success: false,
        error: '验证溯源信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }

  /**
   * 获取溯源统计信息
   */
  async getTraceabilityStats(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/traceability/stats', 
        status: '200' 
      });

      const stats = await this.traceabilityService.getTraceabilityStats();
      
      res.json({
        success: true,
        data: stats
      });
    } catch (error) {
      logger.error('获取溯源统计信息失败:', error);
      res.status(500).json({
        success: false,
        error: '获取溯源统计信息失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }
}

export default new TraceabilityController(traceabilityService); 