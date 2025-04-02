/**
 * 会话管理控制器
 */
import { Request, Response } from 'express';
import { SessionService } from '../services/session-service';
import logger from '../utils/logger';

export class SessionController {
  private sessionService: SessionService;

  constructor() {
    this.sessionService = new SessionService();
  }

  /**
   * 创建新的用户会话
   */
  createSession = async (req: Request, res: Response): Promise<void> => {
    try {
      const { userId, preferredAgentId, initialContext } = req.body;
      
      logger.info(`创建用户会话`, { userId, preferredAgentId });
      
      const session = await this.sessionService.createSession(userId, preferredAgentId, initialContext);
      
      res.status(201).json({
        success: true,
        data: session,
      });
    } catch (error) {
      logger.error(`创建会话失败`, { error });
      res.status(500).json({
        success: false,
        message: '创建会话时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 获取会话信息
   */
  getSession = async (req: Request, res: Response): Promise<void> => {
    try {
      const { sessionId } = req.params;
      
      logger.info(`获取会话信息`, { sessionId });
      
      const session = await this.sessionService.getSession(sessionId);
      
      if (!session) {
        res.status(404).json({
          success: false,
          message: '未找到会话',
        });
        return;
      }
      
      res.status(200).json({
        success: true,
        data: session,
      });
    } catch (error) {
      logger.error(`获取会话失败`, { error });
      res.status(500).json({
        success: false,
        message: '获取会话时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 更新会话信息
   */
  updateSession = async (req: Request, res: Response): Promise<void> => {
    try {
      const { sessionId } = req.params;
      const { context, status } = req.body;
      
      logger.info(`更新会话信息`, { sessionId, status });
      
      const updated = await this.sessionService.updateSession(sessionId, { context, status });
      
      if (!updated) {
        res.status(404).json({
          success: false,
          message: '未找到会话',
        });
        return;
      }
      
      res.status(200).json({
        success: true,
        data: updated,
      });
    } catch (error) {
      logger.error(`更新会话失败`, { error });
      res.status(500).json({
        success: false,
        message: '更新会话时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 结束会话
   */
  endSession = async (req: Request, res: Response): Promise<void> => {
    try {
      const { sessionId } = req.params;
      
      logger.info(`结束会话`, { sessionId });
      
      const success = await this.sessionService.endSession(sessionId);
      
      if (!success) {
        res.status(404).json({
          success: false,
          message: '未找到会话',
        });
        return;
      }
      
      res.status(204).send();
    } catch (error) {
      logger.error(`结束会话失败`, { error });
      res.status(500).json({
        success: false,
        message: '结束会话时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };

  /**
   * 获取会话消息历史
   */
  getSessionMessages = async (req: Request, res: Response): Promise<void> => {
    try {
      const { sessionId } = req.params;
      const limit = parseInt(req.query.limit as string) || 50;
      const offset = parseInt(req.query.offset as string) || 0;
      
      logger.info(`获取会话消息历史`, { sessionId, limit, offset });
      
      const messages = await this.sessionService.getSessionMessages(sessionId, limit, offset);
      
      res.status(200).json({
        success: true,
        data: messages,
      });
    } catch (error) {
      logger.error(`获取会话消息历史失败`, { error });
      res.status(500).json({
        success: false,
        message: '获取会话消息历史时发生错误',
        error: error instanceof Error ? error.message : String(error),
      });
    }
  };
}