import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import { Logger } from '../utils/logger';
import { AppError } from '../middlewares/error.middleware';
import { FourDiagnosisCoordinatorService } from '../services/four-diagnosis-coordinator.service';
import { FourDiagnosisResponse } from '../interfaces/four-diagnosis.interface';

const logger = new Logger('FourDiagnosisCoordinatorController');
const fourDiagnosisService = new FourDiagnosisCoordinatorService();

/**
 * 获取患者四诊数据
 */
export const getPatientFourDiagnosisData = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    // 验证请求
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new AppError(`验证错误: ${JSON.stringify(errors.array())}`, 400);
    }

    const { patientId } = req.params;

    logger.info(`获取患者四诊数据，患者ID: ${patientId}`);
    
    // 调用服务获取数据
    const fourDiagnosisData = await fourDiagnosisService.getPatientFourDiagnosisData(patientId);

    const response: FourDiagnosisResponse = {
      success: true,
      message: '获取四诊数据成功',
      data: fourDiagnosisData
    };

    res.status(200).json(response);
  } catch (error) {
    next(error);
  }
};

/**
 * 分析患者四诊数据
 */
export const analyzeFourDiagnosis = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    // 验证请求
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new AppError(`验证错误: ${JSON.stringify(errors.array())}`, 400);
    }

    const { patientId } = req.body;

    logger.info(`分析患者四诊数据，患者ID: ${patientId}`);
    
    // 调用服务进行分析
    const analysisResult = await fourDiagnosisService.analyzeFourDiagnosis(patientId);

    const response: FourDiagnosisResponse = {
      success: true,
      message: '四诊合参分析完成',
      data: analysisResult
    };

    res.status(200).json(response);
  } catch (error) {
    next(error);
  }
};

/**
 * 获取患者诊断历史记录
 */
export const getPatientDiagnosisHistory = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const { patientId } = req.params;
    const { startDate, endDate, limit = '10', offset = '0' } = req.query;

    logger.info(`获取患者诊断历史记录，患者ID: ${patientId}`, { 
      startDate, 
      endDate, 
      limit, 
      offset 
    });
    
    // 调用服务获取历史数据
    const historyData = await fourDiagnosisService.getPatientDiagnosisHistory(
      patientId,
      startDate as string,
      endDate as string,
      parseInt(limit as string, 10),
      parseInt(offset as string, 10)
    );

    res.status(200).json({
      success: true,
      message: '获取诊断历史记录成功',
      data: historyData
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 健康检查端点
 */
export const healthCheck = (req: Request, res: Response): void => {
  res.status(200).json({ status: 'ok', service: 'four-diagnosis-coordinator-service' });
}; 