import { Logger } from '../utils/logger';
import { AppError } from '../middlewares/error.middleware';
import { v4 as uuidv4 } from 'uuid';
import {
  PulseDiagnosisData,
  AbdominalDiagnosisData,
  TouchDiagnosisAnalysis,
  IPulseDiagnosisData,
  IAbdominalDiagnosisData,
  ITouchDiagnosisAnalysis
} from '../models/touch-diagnosis.model';

const logger = new Logger('TouchDiagnosisRepository');

/**
 * 触诊服务数据访问层
 */
export class TouchDiagnosisRepository {
  /**
   * 保存脉诊数据
   */
  async savePulseDiagnosisData(data: any): Promise<IPulseDiagnosisData> {
    try {
      logger.debug('保存脉诊数据');
      const pulseData = new PulseDiagnosisData(data);
      return await pulseData.save();
    } catch (error) {
      logger.error('保存脉诊数据失败', { error });
      throw new AppError('保存脉诊数据失败', 500);
    }
  }

  /**
   * 保存腹诊数据
   */
  async saveAbdominalDiagnosisData(data: any): Promise<IAbdominalDiagnosisData> {
    try {
      logger.debug('保存腹诊数据');
      const abdominalData = new AbdominalDiagnosisData(data);
      return await abdominalData.save();
    } catch (error) {
      logger.error('保存腹诊数据失败', { error });
      throw new AppError('保存腹诊数据失败', 500);
    }
  }

  /**
   * 保存触诊分析结果
   */
  async saveTouchDiagnosisAnalysis(data: any): Promise<ITouchDiagnosisAnalysis> {
    try {
      logger.debug('保存触诊分析结果');
      
      // 如果没有提供诊断ID则生成一个
      if (!data.diagnosisId) {
        data.diagnosisId = uuidv4();
      }
      
      const analysisData = new TouchDiagnosisAnalysis(data);
      return await analysisData.save();
    } catch (error) {
      logger.error('保存触诊分析结果失败', { error });
      throw new AppError('保存触诊分析结果失败', 500);
    }
  }

  /**
   * 获取患者最新的触诊分析结果
   */
  async getLatestTouchDiagnosisByPatientId(patientId: string): Promise<ITouchDiagnosisAnalysis | null> {
    try {
      logger.debug(`获取患者最新触诊分析结果: ${patientId}`);
      return await TouchDiagnosisAnalysis.findOne({ patientId })
        .sort({ diagnosisTime: -1 })
        .populate('pulseFindings')
        .populate('abdominalFindings');
    } catch (error) {
      logger.error(`获取患者最新触诊分析结果失败: ${patientId}`, { error });
      throw new AppError('获取患者最新触诊分析结果失败', 500);
    }
  }

  /**
   * 根据ID获取触诊分析结果
   */
  async getTouchDiagnosisById(diagnosisId: string): Promise<ITouchDiagnosisAnalysis | null> {
    try {
      logger.debug(`根据ID获取触诊分析结果: ${diagnosisId}`);
      return await TouchDiagnosisAnalysis.findOne({ diagnosisId })
        .populate('pulseFindings')
        .populate('abdominalFindings');
    } catch (error) {
      logger.error(`根据ID获取触诊分析结果失败: ${diagnosisId}`, { error });
      throw new AppError('根据ID获取触诊分析结果失败', 500);
    }
  }

  /**
   * 获取患者触诊分析历史记录
   */
  async getPatientTouchDiagnosisHistory(
    patientId: string,
    startDate?: string,
    endDate?: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<{ total: number; data: ITouchDiagnosisAnalysis[] }> {
    try {
      logger.debug(`获取患者触诊分析历史记录: ${patientId}`, { startDate, endDate, limit, offset });
      
      // 构建查询条件
      const query: any = { patientId };
      
      if (startDate || endDate) {
        query.diagnosisTime = {};
        if (startDate) {
          query.diagnosisTime.$gte = new Date(startDate);
        }
        if (endDate) {
          query.diagnosisTime.$lte = new Date(endDate);
        }
      }
      
      // 获取总记录数
      const total = await TouchDiagnosisAnalysis.countDocuments(query);
      
      // 获取分页数据
      const data = await TouchDiagnosisAnalysis.find(query)
        .sort({ diagnosisTime: -1 })
        .skip(offset)
        .limit(limit)
        .populate('pulseFindings')
        .populate('abdominalFindings');
      
      return { total, data };
    } catch (error) {
      logger.error(`获取患者触诊分析历史记录失败: ${patientId}`, { error });
      throw new AppError('获取患者触诊分析历史记录失败', 500);
    }
  }

  /**
   * 更新触诊分析结果
   */
  async updateTouchDiagnosisAnalysis(diagnosisId: string, updateData: any): Promise<ITouchDiagnosisAnalysis | null> {
    try {
      logger.debug(`更新触诊分析结果: ${diagnosisId}`);
      return await TouchDiagnosisAnalysis.findOneAndUpdate(
        { diagnosisId },
        { $set: updateData },
        { new: true }
      )
        .populate('pulseFindings')
        .populate('abdominalFindings');
    } catch (error) {
      logger.error(`更新触诊分析结果失败: ${diagnosisId}`, { error });
      throw new AppError('更新触诊分析结果失败', 500);
    }
  }
}

// 导出默认实例
export default new TouchDiagnosisRepository(); 