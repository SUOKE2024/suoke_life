import { Request, Response } from 'express';
import { Service } from 'typedi';
import { Container } from 'typedi';
import { body, query, param, validationResult } from 'express-validator';
import { Logger } from '../utils/logger';
import { PostureAnalysisService } from '../services/posture-analysis/posture-analysis.service';
import { CoordinatorClientService } from '../services/four-diagnosis-coordinator/coordinator-client.service';

/**
 * 体态分析控制器
 * 处理体态分析相关API请求
 */
export class PostureAnalysisController {
  private logger = new Logger('PostureAnalysisController');
  private postureAnalysisService: PostureAnalysisService;
  private coordinatorService: CoordinatorClientService;
  
  constructor() {
    this.postureAnalysisService = Container.get(PostureAnalysisService);
    this.coordinatorService = Container.get(CoordinatorClientService);
  }
  
  /**
   * 健康检查端点
   */
  async healthCheck(req: Request, res: Response): Promise<void> {
    res.status(200).json({
      status: 'success',
      message: '体态分析服务运行正常',
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * 体态分析验证规则
   */
  static postureAnalysisValidation = [
    body('imageBase64')
      .isString()
      .notEmpty()
      .withMessage('图像数据不能为空'),
    body('sessionId')
      .isString()
      .notEmpty()
      .withMessage('会话ID不能为空'),
    body('userId')
      .optional()
      .isString()
      .withMessage('用户ID必须是字符串'),
    body('metadata')
      .optional()
      .isObject()
      .withMessage('元数据必须是对象')
  ];
  
  /**
   * 分析体态
   */
  async analyzePosture(req: Request, res: Response): Promise<void> {
    try {
      // 验证请求数据
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        this.logger.error(`体态分析请求验证失败: ${JSON.stringify(errors.array())}`);
        res.status(400).json({
          success: false,
          errors: errors.array()
        });
        return;
      }
      
      const { imageBase64, sessionId, userId, metadata } = req.body;
      
      this.logger.info(`接收到体态分析请求，会话ID: ${sessionId}`);
      
      // 调用服务进行体态分析
      const result = await this.postureAnalysisService.analyzePosture(
        imageBase64,
        sessionId,
        userId,
        metadata
      );
      
      // 向四诊协调服务上报结果
      try {
        await this.coordinatorService.reportDiagnosisResult({
          diagnosisId: result.diagnosisId,
          sessionId: result.sessionId,
          userId: result.userId,
          diagnosisType: 'posture',
          timestamp: result.timestamp,
          result: {
            features: result.features,
            tcmImplications: result.tcmImplications,
            recommendations: result.recommendations
          }
        });
        this.logger.info(`已向四诊协调服务上报结果，诊断ID: ${result.diagnosisId}`);
      } catch (error) {
        this.logger.error(`向四诊协调服务上报结果失败: ${error.message}`);
        // 上报失败不影响API响应
      }
      
      // 返回结果
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      this.logger.error(`体态分析失败: ${error.message}`);
      res.status(500).json({
        success: false,
        message: '体态分析失败',
        error: error.message
      });
    }
  }
  
  /**
   * 历史记录查询验证规则
   */
  static historyValidation = [
    query('userId')
      .optional()
      .isString()
      .withMessage('用户ID必须是字符串'),
    query('sessionId')
      .optional()
      .isString()
      .withMessage('会话ID必须是字符串'),
    query('limit')
      .optional()
      .isInt({ min: 1, max: 100 })
      .withMessage('limit必须是1-100之间的整数')
      .toInt(),
    query('offset')
      .optional()
      .isInt({ min: 0 })
      .withMessage('offset必须是非负整数')
      .toInt()
  ];
  
  /**
   * 获取体态分析历史记录
   */
  async getPostureDiagnosisHistory(req: Request, res: Response): Promise<void> {
    try {
      // 验证请求参数
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        this.logger.error(`获取体态分析历史记录请求验证失败: ${JSON.stringify(errors.array())}`);
        res.status(400).json({
          success: false,
          errors: errors.array()
        });
        return;
      }
      
      const { userId, sessionId } = req.query;
      const limit = parseInt(req.query.limit as string) || 10;
      const offset = parseInt(req.query.offset as string) || 0;
      
      if (!userId && !sessionId) {
        res.status(400).json({
          success: false,
          message: '必须提供userId或sessionId参数'
        });
        return;
      }
      
      let results;
      if (userId) {
        this.logger.info(`获取用户体态分析历史记录，用户ID: ${userId}`);
        results = await this.postureAnalysisService.getPostureDiagnosisByUserId(
          userId as string,
          limit,
          offset
        );
      } else {
        this.logger.info(`获取会话体态分析历史记录，会话ID: ${sessionId}`);
        results = await this.postureAnalysisService.getPostureDiagnosisBySessionId(
          sessionId as string,
          limit,
          offset
        );
      }
      
      res.status(200).json({
        success: true,
        data: results
      });
    } catch (error) {
      this.logger.error(`获取体态分析历史记录失败: ${error.message}`);
      res.status(500).json({
        success: false,
        message: '获取体态分析历史记录失败',
        error: error.message
      });
    }
  }
  
  /**
   * 诊断ID验证规则
   */
  static diagnosisIdValidation = [
    param('diagnosisId')
      .isString()
      .notEmpty()
      .withMessage('诊断ID不能为空')
  ];
  
  /**
   * 通过ID获取体态分析记录
   */
  async getPostureDiagnosisById(req: Request, res: Response): Promise<void> {
    try {
      // 验证请求参数
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        this.logger.error(`获取体态分析记录请求验证失败: ${JSON.stringify(errors.array())}`);
        res.status(400).json({
          success: false,
          errors: errors.array()
        });
        return;
      }
      
      const { diagnosisId } = req.params;
      
      this.logger.info(`获取体态分析记录，诊断ID: ${diagnosisId}`);
      const result = await this.postureAnalysisService.getPostureDiagnosisById(diagnosisId);
      
      if (!result) {
        res.status(404).json({
          success: false,
          message: `未找到ID为 ${diagnosisId} 的体态分析记录`
        });
        return;
      }
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      this.logger.error(`获取体态分析记录失败: ${error.message}`);
      res.status(500).json({
        success: false,
        message: '获取体态分析记录失败',
        error: error.message
      });
    }
  }
} 