import { Logger } from '../utils/logger';
import { AppError } from '../middlewares/error.middleware';
import {
  DiagnosisAnalysis,
  FiveElementsAnalysis,
  YinYangAnalysis,
  OrganAnalysis,
  BodyConditionAnalysis,
  IntegratedAssessment,
  FourDiagnosisData,
  IDiagnosisAnalysis,
  IFiveElementsAnalysis,
  IYinYangAnalysis,
  IOrganAnalysis,
  IBodyConditionAnalysis,
  IIntegratedAssessment,
  IFourDiagnosisData
} from '../models/diagnosis.model';

const logger = new Logger('FourDiagnosisRepository');

/**
 * 四诊协调服务数据访问层
 */
export class FourDiagnosisRepository {
  /**
   * 保存单项诊断分析结果
   */
  async saveDiagnosisAnalysis(data: Partial<IDiagnosisAnalysis>): Promise<IDiagnosisAnalysis> {
    try {
      logger.debug('保存诊断分析数据');
      const diagnosis = new DiagnosisAnalysis(data);
      return await diagnosis.save();
    } catch (error) {
      logger.error('保存诊断分析数据失败', { error });
      throw new AppError('保存诊断分析数据失败', 500);
    }
  }

  /**
   * 保存五行分析结果
   */
  async saveFiveElementsAnalysis(data: Partial<IFiveElementsAnalysis>): Promise<IFiveElementsAnalysis> {
    try {
      logger.debug('保存五行分析结果');
      const fiveElements = new FiveElementsAnalysis(data);
      return await fiveElements.save();
    } catch (error) {
      logger.error('保存五行分析结果失败', { error });
      throw new AppError('保存五行分析结果失败', 500);
    }
  }

  /**
   * 保存阴阳平衡分析结果
   */
  async saveYinYangAnalysis(data: Partial<IYinYangAnalysis>): Promise<IYinYangAnalysis> {
    try {
      logger.debug('保存阴阳平衡分析结果');
      const yinYang = new YinYangAnalysis(data);
      return await yinYang.save();
    } catch (error) {
      logger.error('保存阴阳平衡分析结果失败', { error });
      throw new AppError('保存阴阳平衡分析结果失败', 500);
    }
  }

  /**
   * 保存脏腑分析结果
   */
  async saveOrganAnalysis(data: Partial<IOrganAnalysis>): Promise<IOrganAnalysis> {
    try {
      logger.debug('保存脏腑分析结果');
      const organ = new OrganAnalysis(data);
      return await organ.save();
    } catch (error) {
      logger.error('保存脏腑分析结果失败', { error });
      throw new AppError('保存脏腑分析结果失败', 500);
    }
  }

  /**
   * 保存身体状况分析结果
   */
  async saveBodyConditionAnalysis(data: Partial<IBodyConditionAnalysis>): Promise<IBodyConditionAnalysis> {
    try {
      logger.debug('保存身体状况分析结果');
      const bodyCondition = new BodyConditionAnalysis(data);
      return await bodyCondition.save();
    } catch (error) {
      logger.error('保存身体状况分析结果失败', { error });
      throw new AppError('保存身体状况分析结果失败', 500);
    }
  }

  /**
   * 保存综合分析结果
   */
  async saveIntegratedAssessment(data: Partial<IIntegratedAssessment>): Promise<IIntegratedAssessment> {
    try {
      logger.debug('保存综合分析结果');
      const integratedAssessment = new IntegratedAssessment(data);
      return await integratedAssessment.save();
    } catch (error) {
      logger.error('保存综合分析结果失败', { error });
      throw new AppError('保存综合分析结果失败', 500);
    }
  }

  /**
   * 保存四诊合参数据
   */
  async saveFourDiagnosisData(data: Partial<IFourDiagnosisData>): Promise<IFourDiagnosisData> {
    try {
      logger.debug('保存四诊合参数据');
      const fourDiagnosis = new FourDiagnosisData(data);
      return await fourDiagnosis.save();
    } catch (error) {
      logger.error('保存四诊合参数据失败', { error });
      throw new AppError('保存四诊合参数据失败', 500);
    }
  }

  /**
   * 获取患者最新的四诊合参数据
   */
  async getLatestFourDiagnosisData(patientId: string): Promise<IFourDiagnosisData | null> {
    try {
      logger.debug(`获取患者最新四诊合参数据: ${patientId}`);
      return await FourDiagnosisData.findOne({ patientId })
        .sort({ timestamp: -1 })
        .populate('looking')
        .populate('smell')
        .populate('inquiry')
        .populate('touch')
        .populate({
          path: 'integratedAssessment',
          populate: {
            path: 'bodyCondition',
            populate: ['yinYang', 'fiveElements', 'organs']
          }
        });
    } catch (error) {
      logger.error(`获取患者最新四诊合参数据失败: ${patientId}`, { error });
      throw new AppError('获取患者最新四诊合参数据失败', 500);
    }
  }

  /**
   * 获取患者所有诊断历史记录
   */
  async getPatientDiagnosisHistory(
    patientId: string,
    startDate?: string,
    endDate?: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<{ total: number; data: IFourDiagnosisData[] }> {
    try {
      logger.debug(`获取患者诊断历史记录: ${patientId}`, { startDate, endDate, limit, offset });
      
      // 构建查询条件
      const query: any = { patientId };
      
      if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) {
          query.timestamp.$gte = new Date(startDate);
        }
        if (endDate) {
          query.timestamp.$lte = new Date(endDate);
        }
      }
      
      // 获取总记录数
      const total = await FourDiagnosisData.countDocuments(query);
      
      // 获取分页数据
      const data = await FourDiagnosisData.find(query)
        .sort({ timestamp: -1 })
        .skip(offset)
        .limit(limit)
        .populate('looking')
        .populate('smell')
        .populate('inquiry')
        .populate('touch')
        .populate({
          path: 'integratedAssessment',
          populate: {
            path: 'bodyCondition',
            populate: ['yinYang', 'fiveElements', 'organs']
          }
        });
      
      return { total, data };
    } catch (error) {
      logger.error(`获取患者诊断历史记录失败: ${patientId}`, { error, startDate, endDate });
      throw new AppError('获取患者诊断历史记录失败', 500);
    }
  }

  /**
   * 根据ID获取四诊合参数据
   */
  async getFourDiagnosisById(diagnosisId: string): Promise<IFourDiagnosisData | null> {
    try {
      logger.debug(`根据ID获取四诊合参数据: ${diagnosisId}`);
      return await FourDiagnosisData.findOne({ diagnosisId })
        .populate('looking')
        .populate('smell')
        .populate('inquiry')
        .populate('touch')
        .populate({
          path: 'integratedAssessment',
          populate: {
            path: 'bodyCondition',
            populate: ['yinYang', 'fiveElements', 'organs']
          }
        });
    } catch (error) {
      logger.error(`根据ID获取四诊合参数据失败: ${diagnosisId}`, { error });
      throw new AppError('根据ID获取四诊合参数据失败', 500);
    }
  }
} 