import { Request, Response } from 'express';
import { Service } from 'typedi';
import { LookingDiagnosisService } from '../services/looking-diagnosis.service';
import logger from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';

@Service()
export class LookingDiagnosisController {
  constructor(private lookingDiagnosisService: LookingDiagnosisService) {}

  /**
   * 舌诊分析
   */
  async analyzeTongue(req: Request, res: Response): Promise<void> {
    const requestId = req.headers['x-request-id'] as string || uuidv4();
    try {
      const userId = req.body.userId;
      const imageFile = req.file;
      
      if (!userId || !imageFile) {
        res.status(400).json({
          success: false,
          message: '用户ID和图像文件不能为空'
        });
        return;
      }
      
      logger.info(`舌诊分析请求`, { requestId, userId });
      
      const result = await this.lookingDiagnosisService.analyzeTongue(userId, imageFile.path);
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error(`舌诊分析失败`, { requestId, error });
      res.status(500).json({
        success: false,
        message: '舌诊分析时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  /**
   * 面诊分析
   */
  async analyzeFace(req: Request, res: Response): Promise<void> {
    const requestId = req.headers['x-request-id'] as string || uuidv4();
    try {
      const userId = req.body.userId;
      const imageFile = req.file;
      
      if (!userId || !imageFile) {
        res.status(400).json({
          success: false,
          message: '用户ID和图像文件不能为空'
        });
        return;
      }
      
      logger.info(`面诊分析请求`, { requestId, userId });
      
      const result = await this.lookingDiagnosisService.analyzeFace(userId, imageFile.path);
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error(`面诊分析失败`, { requestId, error });
      res.status(500).json({
        success: false,
        message: '面诊分析时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }
  
  /**
   * 健康检查
   */
  async checkHealth(req: Request, res: Response): Promise<void> {
    res.status(200).json({
      success: true,
      service: 'looking-diagnosis-service',
      status: 'ok',
      version: '1.0.0'
    });
  }
}
