import { Request, Response, NextFunction } from 'express';
import { Container } from 'typedi';
import { DiagnosisService } from '../services/diagnosis.service';
import { Logger } from '../utils/logger';
import { formatSuccess, formatError } from '../utils/response-formatter';
import { DiagnosisRequest } from '../models/diagnosis.model';
import { NotFoundError, BusinessError } from '../utils/error-handler';

/**
 * 诊断控制器
 * 处理与中医诊断相关的HTTP请求
 * @swagger
 * tags:
 *   name: 诊断
 *   description: 中医辨证分析和诊断结果API
 */
export class DiagnosisController {
  private diagnosisService: DiagnosisService;
  private logger: Logger;
  
  constructor() {
    this.diagnosisService = Container.get(DiagnosisService);
    this.logger = new Logger('DiagnosisController');
  }
  
  /**
   * 生成中医辨证诊断
   * @swagger
   * /api/diagnosis/tcm-pattern:
   *   post:
   *     summary: 生成中医辨证诊断
   *     tags: [诊断]
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             required:
   *               - sessionId
   *               - symptoms
   *             properties:
   *               sessionId:
   *                 type: string
   *                 description: 问诊会话ID
   *               userId:
   *                 type: string
   *                 description: 用户ID
   *               symptoms:
   *                 type: array
   *                 items:
   *                   type: string
   *                 description: 症状列表
   *               pulseData:
   *                 type: object
   *                 description: 脉诊数据
   *               tongueData:
   *                 type: object
   *                 description: 舌诊数据
   *     responses:
   *       200:
   *         description: 诊断成功
   *       400:
   *         description: 请求参数错误
   *       500:
   *         description: 服务器错误
   */
  async generateTCMPattern(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { sessionId, userId, symptoms, pulseData, tongueData } = req.body;
      
      const diagnosis = await this.diagnosisService.generateTCMPattern(
        sessionId,
        userId,
        symptoms,
        pulseData,
        tongueData
      );
      
      res.status(200).json({
        success: true,
        message: '诊断成功',
        data: diagnosis
      });
    } catch (error) {
      this.logger.error('生成中医辨证诊断失败', { error });
      next(error);
    }
  }
  
  /**
   * 获取诊断历史
   * @swagger
   * /api/diagnosis/history/{userId}:
   *   get:
   *     summary: 获取用户诊断历史
   *     tags: [诊断]
   *     parameters:
   *       - in: path
   *         name: userId
   *         schema:
   *           type: string
   *         required: true
   *         description: 用户ID
   *       - in: query
   *         name: limit
   *         schema:
   *           type: integer
   *           default: 10
   *         description: 返回结果数量限制
   *       - in: query
   *         name: offset
   *         schema:
   *           type: integer
   *           default: 0
   *         description: 分页偏移量
   *     responses:
   *       200:
   *         description: 成功获取诊断历史
   *       404:
   *         description: 用户不存在
   *       500:
   *         description: 服务器错误
   */
  async getDiagnosisHistory(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { userId } = req.params;
      const limit = parseInt(req.query.limit as string) || 10;
      const offset = parseInt(req.query.offset as string) || 0;
      
      const history = await this.diagnosisService.getDiagnosisHistory(userId, limit, offset);
      
      res.status(200).json({
        success: true,
        message: '成功获取诊断历史',
        data: history
      });
    } catch (error) {
      this.logger.error('获取诊断历史失败', { error, userId: req.params.userId });
      next(error);
    }
  }
  
  /**
   * 获取单个诊断详情
   * @swagger
   * /api/diagnosis/{id}:
   *   get:
   *     summary: 获取诊断详情
   *     tags: [诊断]
   *     parameters:
   *       - in: path
   *         name: id
   *         schema:
   *           type: string
   *         required: true
   *         description: 诊断ID
   *     responses:
   *       200:
   *         description: 成功获取诊断详情
   *       404:
   *         description: 诊断不存在
   *       500:
   *         description: 服务器错误
   */
  async getDiagnosisById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { id } = req.params;
      
      const diagnosis = await this.diagnosisService.getDiagnosisById(id);
      
      if (!diagnosis) {
        return res.status(404).json({
          success: false,
          message: '诊断不存在',
          data: null
        });
      }
      
      res.status(200).json({
        success: true,
        message: '成功获取诊断详情',
        data: diagnosis
      });
    } catch (error) {
      this.logger.error('获取诊断详情失败', { error, id: req.params.id });
      next(error);
    }
  }
  
  /**
   * 通过会话ID获取诊断结果
   * @param req 请求对象
   * @param res 响应对象
   * @param next 下一个中间件
   */
  async getDiagnosisBySessionId(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const sessionId = req.params.sessionId;
      this.logger.info(`通过会话ID获取诊断结果，会话ID: ${sessionId}`);
      
      const diagnosis = await this.diagnosisService.getDiagnosisBySessionId(sessionId);
      
      res.status(200).json(formatSuccess(diagnosis, '诊断结果获取成功'));
    } catch (error) {
      this.logger.error(`通过会话ID获取诊断结果失败: ${error.message}`, { error });
      
      if (error instanceof NotFoundError) {
        res.status(404).json(formatError('该会话的诊断结果不存在', 404));
        return;
      }
      
      next(error);
    }
  }
  
  /**
   * 获取用户的诊断历史
   * @param req 请求对象
   * @param res 响应对象
   * @param next 下一个中间件
   */
  async getUserDiagnosisHistory(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.params.userId;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 10;
      const offset = req.query.offset ? parseInt(req.query.offset as string) : 0;
      
      this.logger.info(`获取用户诊断历史，用户ID: ${userId}`);
      
      const diagnoses = await this.diagnosisService.getUserDiagnosisHistory(userId, limit, offset);
      
      res.status(200).json(formatSuccess(
        {
          diagnoses,
          pagination: {
            limit,
            offset,
            total: diagnoses.length // 实际项目中应返回总数
          }
        },
        '用户诊断历史获取成功'
      ));
    } catch (error) {
      this.logger.error(`获取用户诊断历史失败: ${error.message}`, { error });
      next(error);
    }
  }
}