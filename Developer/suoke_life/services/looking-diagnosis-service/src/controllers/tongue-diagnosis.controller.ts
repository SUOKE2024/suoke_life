import { Request, Response, NextFunction } from 'express';
import { Container } from 'typedi';
import { TongueDiagnosisService } from '../services/tongue-diagnosis/tongue-diagnosis.service';
import { Logger } from '../utils/logger';
import { TongueDiagnosisRequest } from '../models/diagnosis/tongue.model';

export class TongueDiagnosisController {
  private logger = new Logger('TongueDiagnosisController');
  private tongueDiagnosisService: TongueDiagnosisService;
  
  constructor() {
    this.tongueDiagnosisService = Container.get(TongueDiagnosisService);
  }
  
  /**
   * 分析舌象
   * @param req Express请求对象
   * @param res Express响应对象
   * @param next Express下一个中间件
   */
  async analyzeTongue(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      this.logger.logWithRequestId(req, '收到舌诊分析请求');
      
      // 验证请求数据
      const { imageBase64, sessionId, metadata } = req.body as TongueDiagnosisRequest;
      // 从请求头或其他来源获取用户ID
      const userId = req.headers['user-id'] as string;
      
      if (!imageBase64) {
        this.logger.error('舌诊请求缺少图像数据');
        res.status(400).json({
          success: false,
          message: '请求缺少图像数据',
          error: 'MISSING_IMAGE_DATA'
        });
        return;
      }
      
      if (!sessionId) {
        this.logger.error('舌诊请求缺少会话ID');
        res.status(400).json({
          success: false,
          message: '请求缺少会话ID',
          error: 'MISSING_SESSION_ID'
        });
        return;
      }
      
      // 将Base64图像转换为Buffer
      const imageBuffer = Buffer.from(imageBase64, 'base64');
      
      // 调用服务进行舌诊分析
      const result = await this.tongueDiagnosisService.analyze(imageBuffer, sessionId, metadata || {}, userId);
      
      this.logger.logWithRequestId(req, `舌诊分析完成，诊断ID: ${result.diagnosisId}`);
      
      // 返回分析结果
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      this.logger.error(`舌诊分析处理错误: ${error.message}`);
      next(error);
    }
  }
  
  /**
   * 获取舌诊历史记录
   * @param req Express请求对象
   * @param res Express响应对象
   * @param next Express下一个中间件
   */
  async getTongueDiagnosisHistory(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      this.logger.logWithRequestId(req, '收到获取舌诊历史记录请求');
      
      const userId = req.query.userId as string;
      const sessionId = req.query.sessionId as string;
      const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : 10;
      const offset = req.query.offset ? parseInt(req.query.offset as string, 10) : 0;
      
      // 验证请求参数
      if (!userId && !sessionId) {
        this.logger.error('历史记录请求缺少用户ID或会话ID');
        res.status(400).json({
          success: false,
          message: '请求缺少用户ID或会话ID',
          error: 'MISSING_REQUIRED_PARAMETERS'
        });
        return;
      }
      
      // 调用服务获取历史记录
      const { records, total } = await this.tongueDiagnosisService.getDiagnosisHistory(
        userId, 
        sessionId, 
        limit, 
        offset
      );
      
      this.logger.logWithRequestId(req, `获取到${records.length}条舌诊历史记录`);
      
      // 返回历史记录
      res.status(200).json({
        success: true,
        data: {
          total,
          offset,
          limit,
          records
        }
      });
    } catch (error) {
      this.logger.error(`获取舌诊历史记录错误: ${error.message}`);
      next(error);
    }
  }
  
  /**
   * 获取特定的舌诊记录
   * @param req Express请求对象
   * @param res Express响应对象
   * @param next Express下一个中间件
   */
  async getTongueDiagnosisById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { diagnosisId } = req.params;
      this.logger.logWithRequestId(req, `收到获取舌诊记录请求，ID: ${diagnosisId}`);
      
      if (!diagnosisId) {
        this.logger.error('请求缺少诊断ID');
        res.status(400).json({
          success: false,
          message: '请求缺少诊断ID',
          error: 'MISSING_DIAGNOSIS_ID'
        });
        return;
      }
      
      // 调用服务获取单个诊断记录
      const diagnosisResult = await this.tongueDiagnosisService.getDiagnosisById(diagnosisId);
      
      if (!diagnosisResult) {
        this.logger.warn(`未找到舌诊记录，ID: ${diagnosisId}`);
        res.status(404).json({
          success: false,
          message: '未找到指定的舌诊记录',
          error: 'DIAGNOSIS_NOT_FOUND'
        });
        return;
      }
      
      this.logger.logWithRequestId(req, `成功获取舌诊记录，ID: ${diagnosisId}`);
      
      // 返回诊断记录
      res.status(200).json({
        success: true,
        data: diagnosisResult
      });
    } catch (error) {
      this.logger.error(`获取舌诊记录错误: ${error.message}`);
      next(error);
    }
  }
  
  /**
   * 健康检查端点
   * @param req Express请求对象
   * @param res Express响应对象
   */
  healthCheck(req: Request, res: Response): void {
    res.status(200).json({
      status: 'ok',
      service: 'tongue-diagnosis-service',
      timestamp: new Date().toISOString()
    });
  }
}