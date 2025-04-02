import { Request, Response, NextFunction } from 'express';
import { Container } from 'typedi';
import { FaceAnalysisService } from '../services/face-analysis/face-analysis.service';
import { Logger } from '../utils/logger';

/**
 * 面诊分析请求接口
 */
interface FaceDiagnosisRequest {
  /**
   * Base64编码的面部图像
   */
  imageBase64: string;
  
  /**
   * 会话ID
   */
  sessionId: string;
  
  /**
   * 元数据
   */
  metadata?: Record<string, any>;
}

export class FaceAnalysisController {
  private logger = new Logger('FaceAnalysisController');
  private faceAnalysisService: FaceAnalysisService;
  
  constructor() {
    this.faceAnalysisService = Container.get(FaceAnalysisService);
  }
  
  /**
   * 分析面色
   * @param req Express请求对象
   * @param res Express响应对象
   * @param next Express下一个中间件
   */
  async analyzeFace(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      this.logger.logWithRequestId(req, '收到面诊分析请求');
      
      // 验证请求数据
      const { imageBase64, sessionId, metadata } = req.body as FaceDiagnosisRequest;
      // 从请求头或其他来源获取用户ID
      const userId = req.headers['user-id'] as string;
      
      if (!imageBase64) {
        this.logger.error('面诊请求缺少图像数据');
        res.status(400).json({
          success: false,
          message: '请求缺少图像数据',
          error: 'MISSING_IMAGE_DATA'
        });
        return;
      }
      
      if (!sessionId) {
        this.logger.error('面诊请求缺少会话ID');
        res.status(400).json({
          success: false,
          message: '请求缺少会话ID',
          error: 'MISSING_SESSION_ID'
        });
        return;
      }
      
      // 将Base64图像转换为Buffer
      const imageBuffer = Buffer.from(imageBase64, 'base64');
      
      // 调用服务进行面诊分析
      const result = await this.faceAnalysisService.analyze(imageBuffer, sessionId, metadata || {});
      
      this.logger.logWithRequestId(req, `面诊分析完成，诊断ID: ${result.diagnosisId}`);
      
      // 返回分析结果
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      this.logger.error(`面诊分析处理错误: ${error.message}`);
      next(error);
    }
  }
  
  /**
   * 获取面诊历史记录
   * @param req Express请求对象
   * @param res Express响应对象
   * @param next Express下一个中间件
   */
  async getFaceDiagnosisHistory(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      this.logger.logWithRequestId(req, '收到获取面诊历史记录请求');
      
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
      
      // TODO: 实现获取面诊历史记录功能
      // 临时返回空数据
      res.status(200).json({
        success: true,
        data: {
          total: 0,
          offset,
          limit,
          records: []
        }
      });
    } catch (error) {
      this.logger.error(`获取面诊历史记录错误: ${error.message}`);
      next(error);
    }
  }
  
  /**
   * 获取特定的面诊记录
   * @param req Express请求对象
   * @param res Express响应对象
   * @param next Express下一个中间件
   */
  async getFaceDiagnosisById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { diagnosisId } = req.params;
      this.logger.logWithRequestId(req, `收到获取面诊记录请求，ID: ${diagnosisId}`);
      
      if (!diagnosisId) {
        this.logger.error('请求缺少诊断ID');
        res.status(400).json({
          success: false,
          message: '请求缺少诊断ID',
          error: 'MISSING_DIAGNOSIS_ID'
        });
        return;
      }
      
      // TODO: 实现获取单个面诊记录功能
      // 临时返回404
      res.status(404).json({
        success: false,
        message: '未找到指定的面诊记录',
        error: 'DIAGNOSIS_NOT_FOUND'
      });
    } catch (error) {
      this.logger.error(`获取面诊记录错误: ${error.message}`);
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
      service: 'face-analysis-service',
      timestamp: new Date().toISOString()
    });
  }
} 