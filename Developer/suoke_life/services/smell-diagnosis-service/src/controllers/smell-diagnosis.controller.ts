import { Request, Response, NextFunction } from 'express';
import { Container } from 'typedi';
import { SmellDiagnosisService } from '../services/smell-diagnosis.service';
import { SmellDiagnosisType, SampleType } from '../interfaces/smell-diagnosis.interface';
import { AppError } from '../middlewares/error.middleware';
import { Logger } from '../utils/logger';

export class SmellDiagnosisController {
  private service: SmellDiagnosisService;
  private logger: Logger;

  constructor() {
    this.service = Container.get(SmellDiagnosisService);
    this.logger = new Logger('SmellDiagnosisController');
  }

  /**
   * 分析气味
   */
  analyze = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { userId, diagnosisType, description, metadata, sampleType } = req.body;

      // 验证请求数据
      if (!userId) {
        throw new AppError('缺少用户ID', 400);
      }

      if (!diagnosisType || !Object.values(SmellDiagnosisType).includes(diagnosisType)) {
        throw new AppError('无效的诊断类型', 400);
      }

      // 构建请求对象
      const request: any = {
        userId,
        diagnosisType,
        description,
        metadata,
        sampleType: sampleType || SampleType.TEXT_DESCRIPTION
      };

      // 处理音频数据（如果有）
      if (req.file) {
        request.audioData = req.file.buffer;
      }

      this.logger.info('收到闻诊分析请求', { userId, diagnosisType });

      // 调用服务进行分析
      const result = await this.service.analyzeSmell(request);

      // 返回结果
      res.status(200).json({
        success: true,
        data: result.toJSON()
      });
    } catch (error) {
      next(error);
    }
  };

  /**
   * 获取历史分析结果
   */
  getHistory = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { userId } = req.params;
      const limit = parseInt(req.query.limit as string) || 20;
      const skip = parseInt(req.query.skip as string) || 0;

      if (!userId) {
        throw new AppError('缺少用户ID', 400);
      }

      this.logger.info('获取闻诊历史请求', { userId, limit, skip });
      
      // 调用服务获取历史数据
      const results = await this.service.getUserDiagnosisHistory(userId, limit, skip);
      
      res.status(200).json({
        success: true,
        data: results.map(result => result.toJSON())
      });
    } catch (error) {
      next(error);
    }
  };
  
  /**
   * 根据ID获取诊断结果
   */
  getDiagnosisById = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { id } = req.params;
      
      if (!id) {
        throw new AppError('缺少诊断ID', 400);
      }
      
      this.logger.info('获取诊断详情请求', { id });
      
      const result = await this.service.getDiagnosisResultById(id);
      
      if (!result) {
        throw new AppError('诊断结果不存在', 404);
      }
      
      res.status(200).json({
        success: true,
        data: result.toJSON()
      });
    } catch (error) {
      next(error);
    }
  };

  /**
   * 健康检查接口
   */
  healthCheck = (req: Request, res: Response): void => {
    res.status(200).json({
      success: true,
      service: 'smell-diagnosis-service',
      status: 'OK',
      timestamp: new Date().toISOString()
    });
  };
} 