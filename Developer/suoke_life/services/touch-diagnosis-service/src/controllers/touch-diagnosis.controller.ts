import { Request, Response, NextFunction } from 'express';
import { validationResult, body, param, query } from 'express-validator';
import { v4 as uuidv4 } from 'uuid';
import { Logger } from '../utils/logger';
import { AppError } from '../middlewares/error.middleware';
import { 
  TouchDiagnosisRequest, 
  TouchDiagnosisResponse,
  PulseDiagnosisData,
  AbdominalDiagnosisData
} from '../interfaces/touch-diagnosis.interface';
import * as touchDiagnosisService from '../services/touch-diagnosis.service';

const logger = new Logger('TouchDiagnosisController');

/**
 * 记录脉诊数据
 */
export const recordPulseDiagnosis = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    // 验证请求数据
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new AppError(`验证错误: ${JSON.stringify(errors.array())}`, 400);
    }

    const { patientId, practitionerId, pulseData, notes } = req.body;

    logger.info(`记录脉诊数据，患者ID: ${patientId}`, { practitionerId });
    
    // 标准化脉诊数据
    const normalizedPulseData: PulseDiagnosisData[] = pulseData.map((data: any) => ({
      ...data,
      timestamp: new Date(),
      id: uuidv4()
    }));

    // 调用服务保存数据
    const result = await touchDiagnosisService.savePulseDiagnosisData({
      patientId,
      practitionerId,
      pulseData: normalizedPulseData,
      notes
    });

    const response: TouchDiagnosisResponse = {
      success: true,
      message: '脉诊数据保存成功',
      data: result
    };

    res.status(201).json(response);
  } catch (error) {
    next(error);
  }
};

/**
 * 记录腹诊数据
 */
export const recordAbdominalDiagnosis = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    // 验证请求数据
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new AppError(`验证错误: ${JSON.stringify(errors.array())}`, 400);
    }

    const { patientId, practitionerId, abdominalData, notes } = req.body;

    logger.info(`记录腹诊数据，患者ID: ${patientId}`, { practitionerId });
    
    // 标准化腹诊数据
    const normalizedAbdominalData: AbdominalDiagnosisData[] = abdominalData.map((data: any) => ({
      ...data,
      timestamp: new Date(),
      id: uuidv4()
    }));

    // 调用服务保存数据
    const result = await touchDiagnosisService.saveAbdominalDiagnosisData({
      patientId,
      practitionerId,
      abdominalData: normalizedAbdominalData,
      notes
    });

    const response: TouchDiagnosisResponse = {
      success: true,
      message: '腹诊数据保存成功',
      data: result
    };

    res.status(201).json(response);
  } catch (error) {
    next(error);
  }
};

/**
 * 分析触诊数据并生成结论
 */
export const analyzeTouchDiagnosis = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    await Promise.all([
      param('patientId').isString().notEmpty().withMessage('患者ID不能为空').run(req),
      body('diagnosisId').optional().isString().withMessage('诊断ID必须是字符串').run(req)
    ]);

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      res.status(400).json({ success: false, error: errors.array() });
      return;
    }

    const { patientId } = req.params;
    const { diagnosisId } = req.body;

    const result = await touchDiagnosisService.requestAnalysis({ patientId, diagnosisId });

    if (!result.success) {
      res.status(result.error === '未找到触诊记录' ? 404 : 500).json(result);
      return;
    }

    res.status(200).json(result);
  } catch (error) {
    Logger.error('分析触诊数据失败', { error });
    next(error);
  }
};

/**
 * 获取患者的触诊记录
 */
export const getPatientTouchDiagnosis = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    await param('patientId').isString().notEmpty().withMessage('患者ID不能为空').run(req);

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      res.status(400).json({ success: false, error: errors.array() });
      return;
    }

    const { patientId } = req.params;

    const result = await touchDiagnosisService.getPatientData(patientId);

    if (!result.success) {
      res.status(404).json(result);
      return;
    }

    res.status(200).json(result);
  } catch (error) {
    Logger.error('获取患者触诊记录失败', { error });
    next(error);
  }
};

/**
 * 获取患者的触诊历史记录
 */
export const getPatientTouchDiagnosisHistory = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    await Promise.all([
      param('patientId').isString().notEmpty().withMessage('患者ID不能为空').run(req),
      query('startDate').optional().isString().withMessage('开始日期必须是字符串').run(req),
      query('endDate').optional().isString().withMessage('结束日期必须是字符串').run(req),
      query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('每页数量必须是1-100之间的整数').toInt().run(req),
      query('offset').optional().isInt({ min: 0 }).withMessage('偏移量必须是非负整数').toInt().run(req)
    ]);

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      res.status(400).json({ success: false, error: errors.array() });
      return;
    }

    const { patientId } = req.params;
    const { startDate, endDate, limit, offset } = req.query;

    const result = await touchDiagnosisService.getPatientDiagnosisHistory({
      patientId,
      startDate: startDate as string,
      endDate: endDate as string,
      limit: limit as unknown as number,
      offset: offset as unknown as number
    });

    res.status(200).json(result);
  } catch (error) {
    Logger.error('获取患者触诊历史记录失败', { error });
    next(error);
  }
};

/**
 * 创建触诊记录
 * 处理脉诊和腹诊数据的提交
 */
export const createTouchDiagnosis = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    // 验证请求
    await Promise.all([
      body('patientId').isString().notEmpty().withMessage('患者ID不能为空').run(req),
      body('practitionerId').isString().notEmpty().withMessage('医师ID不能为空').run(req),
      body('pulseData').optional().isArray().withMessage('脉诊数据必须是数组').run(req),
      body('abdominalData').optional().isArray().withMessage('腹诊数据必须是数组').run(req)
    ]);

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      res.status(400).json({ success: false, error: errors.array() });
      return;
    }

    const { patientId, practitionerId, pulseData, abdominalData } = req.body;

    // 确保至少提供了一种诊断数据
    if ((!pulseData || pulseData.length === 0) && (!abdominalData || abdominalData.length === 0)) {
      res.status(400).json({
        success: false,
        error: '必须提供脉诊或腹诊数据'
      });
      return;
    }

    // 处理诊断数据
    let diagnosisId;
    let result;

    // 保存脉诊数据（如果有）
    if (pulseData && pulseData.length > 0) {
      result = await touchDiagnosisService.savePulseDiagnosisData(patientId, practitionerId, pulseData);
      if (!result.success) {
        res.status(500).json(result);
        return;
      }
      diagnosisId = result.data?.diagnosisId;
    }

    // 保存腹诊数据（如果有）
    if (abdominalData && abdominalData.length > 0) {
      if (diagnosisId) {
        // 如果已经有诊断ID，使用相同的记录
        result = await touchDiagnosisService.saveAbdominalDiagnosisData(patientId, practitionerId, abdominalData);
      } else {
        result = await touchDiagnosisService.saveAbdominalDiagnosisData(patientId, practitionerId, abdominalData);
        diagnosisId = result.data?.diagnosisId;
      }

      if (!result.success) {
        res.status(500).json(result);
        return;
      }
    }

    // 返回成功响应
    res.status(201).json({
      success: true,
      message: '触诊记录创建成功',
      data: { diagnosisId }
    });
  } catch (error) {
    Logger.error('创建触诊记录失败', { error });
    next(error);
  }
};

/**
 * 获取患者触诊数据
 */
export const getPatientTouchDiagnosisData = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const patientId = req.params.patientId;
    
    if (!patientId) {
      throw new AppError('患者ID不能为空', 400);
    }
    
    logger.debug('获取患者触诊数据', { patientId });
    
    const result = await touchDiagnosisService.getPatientData(patientId);
    
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
};

/**
 * 根据ID获取触诊数据
 */
export const getTouchDiagnosisById = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    await param('diagnosisId').isString().notEmpty().withMessage('诊断ID不能为空').run(req);

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      res.status(400).json({ success: false, error: errors.array() });
      return;
    }

    const { diagnosisId } = req.params;

    const result = await touchDiagnosisService.getDiagnosisById(diagnosisId);

    if (!result.success) {
      res.status(404).json(result);
      return;
    }

    res.status(200).json(result);
  } catch (error) {
    Logger.error('获取触诊记录失败', { error });
    next(error);
  }
};

/**
 * 分析触诊数据
 */
export const requestAnalysis = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const patientId = req.params.patientId;
    
    if (!patientId) {
      throw new AppError('患者ID不能为空', 400);
    }
    
    logger.debug('分析触诊数据', { patientId });
    
    const result = await touchDiagnosisService.requestAnalysis(patientId);
    
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
};

/**
 * 获取患者触诊历史记录
 */
export const getPatientTouchDiagnosisHistoryData = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const patientId = req.params.patientId;
    const { startDate, endDate } = req.query;
    let { limit, offset } = req.query;
    
    if (!patientId) {
      throw new AppError('患者ID不能为空', 400);
    }
    
    // 转换分页参数
    const parsedLimit = limit ? parseInt(limit as string, 10) : 10;
    const parsedOffset = offset ? parseInt(offset as string, 10) : 0;
    
    logger.debug('获取患者触诊历史记录', {
      patientId,
      startDate,
      endDate,
      limit: parsedLimit,
      offset: parsedOffset
    });
    
    const result = await touchDiagnosisService.getPatientDiagnosisHistory(
      patientId,
      startDate as string,
      endDate as string,
      parsedLimit,
      parsedOffset
    );
    
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}; 