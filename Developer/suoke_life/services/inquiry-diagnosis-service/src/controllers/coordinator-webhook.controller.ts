import { Request, Response, NextFunction } from 'express';
import { Container } from 'typedi';
import { FourDiagnosisCoordinatorService } from '../integrations/four-diagnosis-coordinator.service';
import { logger } from '../utils/logger';

/**
 * 四诊协调Webhook控制器
 * 处理来自四诊协调服务的回调请求
 * @swagger
 * tags:
 *   name: 四诊协调
 *   description: 四诊协调服务集成API
 */
export class CoordinatorWebhookController {
  private coordinatorService: FourDiagnosisCoordinatorService;

  constructor() {
    this.coordinatorService = Container.get(FourDiagnosisCoordinatorService);
  }

  /**
   * 处理四诊结果通知
   * @swagger
   * /api/coordinator/webhook/diagnosis:
   *   post:
   *     summary: 接收四诊综合诊断结果
   *     tags: [四诊协调]
   *     security:
   *       - apiKeyAuth: []
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             required:
   *               - sessionId
   *               - diagnosisId
   *               - diagnosisType
   *               - diagnosisData
   *             properties:
   *               sessionId:
   *                 type: string
   *                 description: 关联的会话ID
   *               diagnosisId:
   *                 type: string
   *                 description: 综合诊断ID
   *               diagnosisType:
   *                 type: string
   *                 enum: [integrated, pulse, tongue, facial]
   *                 description: 诊断类型
   *               diagnosisData:
   *                 type: object
   *                 description: 诊断数据
   *     responses:
   *       200:
   *         description: 诊断结果接收成功
   *       400:
   *         description: 请求参数错误
   *       401:
   *         description: 未授权
   *       500:
   *         description: 服务器错误
   */
  public handleDiagnosisNotification = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      logger.info('收到四诊协调服务的诊断结果通知', { body: req.body });
      
      const { sessionId, diagnosisId, diagnosisType, diagnosisData } = req.body;
      
      await this.coordinatorService.processDiagnosisNotification(
        sessionId,
        diagnosisId,
        diagnosisType,
        diagnosisData
      );
      
      res.status(200).json({
        success: true,
        message: '诊断结果通知处理成功'
      });
    } catch (error) {
      logger.error('处理四诊协调通知失败', { error });
      next(error);
    }
  }

  /**
   * 处理舌诊结果通知
   * @swagger
   * /api/coordinator/webhook/tongue:
   *   post:
   *     summary: 接收舌诊结果
   *     tags: [四诊协调]
   *     security:
   *       - apiKeyAuth: []
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             required:
   *               - sessionId
   *               - tongueId
   *               - tongueData
   *             properties:
   *               sessionId:
   *                 type: string
   *                 description: 关联的会话ID
   *               tongueId:
   *                 type: string
   *                 description: 舌诊ID
   *               tongueData:
   *                 type: object
   *                 description: 舌诊数据
   *     responses:
   *       200:
   *         description: 舌诊结果接收成功
   *       400:
   *         description: 请求参数错误
   *       401:
   *         description: 未授权
   *       500:
   *         description: 服务器错误
   */
  public handleTongueNotification = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      logger.info('收到四诊协调服务的舌诊结果通知', { body: req.body });
      
      const { sessionId, tongueId, tongueData } = req.body;
      
      await this.coordinatorService.processTongueNotification(
        sessionId,
        tongueId,
        tongueData
      );
      
      res.status(200).json({
        success: true,
        message: '舌诊结果通知处理成功'
      });
    } catch (error) {
      logger.error('处理舌诊结果通知失败', { error });
      next(error);
    }
  }

  /**
   * 处理脉诊结果通知
   * @swagger
   * /api/coordinator/webhook/pulse:
   *   post:
   *     summary: 接收脉诊结果
   *     tags: [四诊协调]
   *     security:
   *       - apiKeyAuth: []
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             required:
   *               - sessionId
   *               - pulseId
   *               - pulseData
   *             properties:
   *               sessionId:
   *                 type: string
   *                 description: 关联的会话ID
   *               pulseId:
   *                 type: string
   *                 description: 脉诊ID
   *               pulseData:
   *                 type: object
   *                 description: 脉诊数据
   *     responses:
   *       200:
   *         description: 脉诊结果接收成功
   *       400:
   *         description: 请求参数错误
   *       401:
   *         description: 未授权
   *       500:
   *         description: 服务器错误
   */
  public handlePulseNotification = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      logger.info('收到四诊协调服务的脉诊结果通知', { body: req.body });
      
      const { sessionId, pulseId, pulseData } = req.body;
      
      await this.coordinatorService.processPulseNotification(
        sessionId,
        pulseId,
        pulseData
      );
      
      res.status(200).json({
        success: true,
        message: '脉诊结果通知处理成功'
      });
    } catch (error) {
      logger.error('处理脉诊结果通知失败', { error });
      next(error);
    }
  }

  /**
   * 健康检查
   * @swagger
   * /api/coordinator/health:
   *   get:
   *     summary: 服务健康检查
   *     tags: [四诊协调]
   *     responses:
   *       200:
   *         description: 服务正常运行
   */
  public healthCheck = async (req: Request, res: Response): Promise<void> => {
    res.status(200).json({
      success: true,
      message: '四诊协调服务集成正常运行',
      timestamp: new Date().toISOString()
    });
  }
}