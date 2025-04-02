/**
 * 代理服务控制器
 */
import { Request, Response } from 'express';
import { AgentService } from '../services/agent-service';
import logger from '../utils/logger';
import { AgentNotFoundError } from '../utils/error-handler';

export class AgentController {
  private agentService: AgentService;

  constructor(agentService?: AgentService) {
    this.agentService = agentService || new AgentService();
  }

  /**
   * 获取可用代理列表
   */
  getAgents = async (req: Request, res: Response): Promise<void> => {
    try {
      logger.info('获取代理列表');
      
      const agents = await this.agentService.getAllAgents();
      
      res.status(200).json({
        success: true,
        data: agents,
      });
    } catch (error) {
      logger.error(`获取代理列表失败`, { error });
      res.status(500).json({
        success: false,
        message: '获取代理列表失败',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 获取代理详情
   */
  getAgentById = async (req: Request, res: Response): Promise<void> => {
    try {
      const { agentId } = req.params;
      
      logger.info(`获取代理详情`, { agentId });
      
      const agent = await this.agentService.getAgentById(agentId);
      
      if (!agent) {
        res.status(404).json({
          success: false,
          message: `代理 ${agentId} 未找到`,
        });
        return;
      }
      
      res.status(200).json({
        success: true,
        data: agent,
      });
    } catch (error) {
      if (error instanceof AgentNotFoundError) {
        res.status(404).json({
          success: false,
          message: `代理 ${req.params.agentId} 未找到`
        });
        return;
      }
      
      logger.error(`获取代理详情失败`, { error });
      res.status(500).json({
        success: false,
        message: '获取代理信息失败',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 检查代理能力
   */
  checkAgentCapability = async (req: Request, res: Response): Promise<void> => {
    try {
      const { agentId } = req.params;
      const capability = req.query.capability as string;
      
      if (!capability) {
        res.status(400).json({
          success: false,
          message: '缺少capability参数'
        });
        return;
      }
      
      logger.info(`检查代理能力`, { agentId, capability });
      
      const hasCapability = await this.agentService.checkAgentCapability(agentId, capability);
      
      res.status(200).json({
        success: true,
        data: {
          hasCapability
        },
      });
    } catch (error) {
      if (error instanceof AgentNotFoundError) {
        res.status(404).json({
          success: false,
          message: `代理 ${req.params.agentId} 未找到`
        });
        return;
      }
      
      logger.error(`检查代理能力失败`, { error });
      res.status(500).json({
        success: false,
        message: '检查代理能力失败',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 向特定代理发送请求
   */
  queryAgent = async (req: Request, res: Response): Promise<void> => {
    try {
      const { agentId } = req.params;
      const { sessionId, query, context } = req.body;
      
      logger.info(`向代理发送请求`, { agentId, sessionId });
      
      const response = await this.agentService.queryAgent(agentId, sessionId, query, context);
      
      res.status(200).json({
        success: true,
        data: response,
      });
    } catch (error) {
      logger.error(`向代理发送请求失败`, { error });
      res.status(500).json({
        success: false,
        message: '向代理发送请求时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 检查代理健康状态
   */
  checkAgentHealth = async (req: Request, res: Response): Promise<void> => {
    try {
      const { agentId } = req.params;
      
      logger.info(`检查代理健康状态`, { agentId });
      
      const isHealthy = await this.agentService.checkAgentHealth(agentId);
      
      res.status(200).json({
        success: true,
        data: {
          agentId,
          healthy: isHealthy,
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      logger.error(`检查代理健康状态失败`, { error });
      res.status(500).json({
        success: false,
        message: '检查代理健康状态时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };
}