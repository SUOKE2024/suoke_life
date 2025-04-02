/**
 * 协调操作控制器
 */
import { Request, Response } from 'express';
import { CoordinationService } from '../services/coordination-service';
import logger from '../utils/logger';

export class CoordinationController {
  private coordinationService: CoordinationService;

  constructor() {
    this.coordinationService = new CoordinationService();
  }

  /**
   * 智能路由请求
   */
  routeRequest = async (req: Request, res: Response): Promise<void> => {
    try {
      const { sessionId, query, context } = req.body;
      
      logger.info(`智能路由请求`, { sessionId });
      
      const response = await this.coordinationService.routeRequest(sessionId, query, context);
      
      res.status(200).json({
        success: true,
        data: response,
      });
    } catch (error) {
      logger.error(`智能路由请求失败`, { error });
      res.status(500).json({
        success: false,
        message: '路由请求时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 代理服务交接
   */
  handoffSession = async (req: Request, res: Response): Promise<void> => {
    try {
      const { sessionId, fromAgentId, toAgentId, reason, context } = req.body;
      
      logger.info(`代理交接会话`, { sessionId, fromAgentId, toAgentId, reason });
      
      const result = await this.coordinationService.handoffSession(
        sessionId, 
        fromAgentId, 
        toAgentId, 
        reason, 
        context
      );
      
      res.status(200).json({
        success: true,
        data: result,
      });
    } catch (error) {
      logger.error(`代理交接会话失败`, { error });
      res.status(500).json({
        success: false,
        message: '交接会话时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 分析用户查询
   */
  analyzeQuery = async (req: Request, res: Response): Promise<void> => {
    try {
      const { query, context } = req.body;
      
      logger.info(`分析用户查询`, { queryLength: query.length });
      
      const analysis = await this.coordinationService.analyzeQuery(query, context);
      
      res.status(200).json({
        success: true,
        data: analysis,
      });
    } catch (error) {
      logger.error(`分析用户查询失败`, { error });
      res.status(500).json({
        success: false,
        message: '分析查询时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 获取系统总体能力
   */
  getSystemCapabilities = async (req: Request, res: Response): Promise<void> => {
    try {
      logger.info(`获取系统总体能力`);
      
      const capabilities = await this.coordinationService.getSystemCapabilities();
      
      res.status(200).json({
        success: true,
        data: capabilities,
      });
    } catch (error) {
      logger.error(`获取系统总体能力失败`, { error });
      res.status(500).json({
        success: false,
        message: '获取系统能力时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };
}