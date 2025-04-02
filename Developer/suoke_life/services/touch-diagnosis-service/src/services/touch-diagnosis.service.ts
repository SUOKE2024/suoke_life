import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { Logger } from '../utils/logger';
import { TouchDiagnosisModel, IPulseDiagnosis, IAbdominalDiagnosis } from '../models/touch-diagnosis.model';
import { 
  TouchDiagnosisResponse, 
  AnalysisRequest,
  HistoryQuery
} from '../interfaces/touch-diagnosis.interface';
import { HealthSuggestionsGenerator } from '../engines/health-suggestions.engine';
import { TouchDiagnosisAnalysisEngine } from '../engines/touch-diagnosis-analysis.engine';

/**
 * 触诊服务
 * 负责处理触诊数据的存储、检索和分析
 */
class TouchDiagnosisService {
  private analysisEngine: TouchDiagnosisAnalysisEngine;
  private suggestionsGenerator: HealthSuggestionsGenerator;
  private fourDiagnosisCoordinatorUrl: string;
  private patientServiceUrl: string;

  constructor() {
    this.analysisEngine = new TouchDiagnosisAnalysisEngine();
    this.suggestionsGenerator = new HealthSuggestionsGenerator();
    this.fourDiagnosisCoordinatorUrl = process.env.FOUR_DIAGNOSIS_COORDINATOR_URL || 'http://localhost:3001/api/four-diagnosis';
    this.patientServiceUrl = process.env.PATIENT_SERVICE_URL || 'http://localhost:3005/api/patients';
  }

  /**
   * 保存脉诊数据
   * @param patientId 患者ID
   * @param practitionerId 医师ID
   * @param pulseData 脉诊数据
   * @returns 保存的诊断记录ID
   */
  public async savePulseDiagnosisData(
    patientId: string,
    practitionerId: string,
    pulseData: IPulseDiagnosis[]
  ): Promise<TouchDiagnosisResponse> {
    try {
      Logger.info(`正在保存患者 ${patientId} 的脉诊数据`);
      
      // 检查此患者是否已有当天的诊断记录
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      let diagnosisRecord = await TouchDiagnosisModel.findOne({
        patientId,
        date: { $gte: today, $lt: tomorrow }
      });
      
      // 如果没有记录，创建新的
      if (!diagnosisRecord) {
        diagnosisRecord = new TouchDiagnosisModel({
          _id: uuidv4(),
          patientId,
          practitionerId,
          date: new Date(),
          pulseData: []
        });
      }
      
      // 添加脉诊数据
      diagnosisRecord.pulseData = pulseData;
      
      // 保存记录
      await diagnosisRecord.save();
      
      return {
        success: true,
        data: { diagnosisId: diagnosisRecord._id },
        message: '脉诊数据保存成功'
      };
    } catch (error) {
      Logger.error(`保存脉诊数据失败`, { error, patientId });
      return {
        success: false,
        error: error instanceof Error ? error.message : '保存脉诊数据失败',
        message: '保存脉诊数据时发生错误'
      };
    }
  }

  /**
   * 保存腹诊数据
   * @param patientId 患者ID
   * @param practitionerId 医师ID
   * @param abdominalData 腹诊数据
   * @returns 保存的诊断记录ID
   */
  public async saveAbdominalDiagnosisData(
    patientId: string,
    practitionerId: string,
    abdominalData: IAbdominalDiagnosis[]
  ): Promise<TouchDiagnosisResponse> {
    try {
      Logger.info(`正在保存患者 ${patientId} 的腹诊数据`);
      
      // 检查此患者是否已有当天的诊断记录
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      let diagnosisRecord = await TouchDiagnosisModel.findOne({
        patientId,
        date: { $gte: today, $lt: tomorrow }
      });
      
      // 如果没有记录，创建新的
      if (!diagnosisRecord) {
        diagnosisRecord = new TouchDiagnosisModel({
          _id: uuidv4(),
          patientId,
          practitionerId,
          date: new Date(),
          abdominalData: []
        });
      }
      
      // 添加腹诊数据
      diagnosisRecord.abdominalData = abdominalData;
      
      // 保存记录
      await diagnosisRecord.save();
      
      return {
        success: true,
        data: { diagnosisId: diagnosisRecord._id },
        message: '腹诊数据保存成功'
      };
    } catch (error) {
      Logger.error(`保存腹诊数据失败`, { error, patientId });
      return {
        success: false,
        error: error instanceof Error ? error.message : '保存腹诊数据失败',
        message: '保存腹诊数据时发生错误'
      };
    }
  }

  /**
   * 获取患者的触诊记录
   * @param patientId 患者ID
   * @returns 患者的最新触诊记录
   */
  public async getPatientData(patientId: string): Promise<TouchDiagnosisResponse> {
    try {
      Logger.info(`获取患者 ${patientId} 的触诊数据`);
      
      const diagnosisRecord = await TouchDiagnosisModel.findOne(
        { patientId },
        {},
        { sort: { date: -1 } }
      );
      
      if (!diagnosisRecord) {
        return {
          success: false,
          error: '未找到患者触诊记录',
          message: '未找到患者触诊记录'
        };
      }
      
      return {
        success: true,
        data: diagnosisRecord,
        message: '成功获取患者触诊数据'
      };
    } catch (error) {
      Logger.error(`获取患者触诊数据失败`, { error, patientId });
      return {
        success: false,
        error: error instanceof Error ? error.message : '获取患者数据失败',
        message: '获取患者触诊数据时发生错误'
      };
    }
  }

  /**
   * 根据ID获取触诊记录
   * @param diagnosisId 触诊记录ID
   * @returns 触诊记录
   */
  public async getDiagnosisById(diagnosisId: string): Promise<TouchDiagnosisResponse> {
    try {
      Logger.info(`获取触诊记录ID: ${diagnosisId}`);
      
      const diagnosisRecord = await TouchDiagnosisModel.findOne({ _id: diagnosisId });
      
      if (!diagnosisRecord) {
        return {
          success: false,
          error: '未找到指定的触诊记录',
          message: '未找到指定的触诊记录'
        };
      }
      
      return {
        success: true,
        data: diagnosisRecord,
        message: '成功获取触诊记录'
      };
    } catch (error) {
      Logger.error(`获取触诊记录失败`, { error, diagnosisId });
      return {
        success: false,
        error: error instanceof Error ? error.message : '获取触诊记录失败',
        message: '获取触诊记录时发生错误'
      };
    }
  }

  /**
   * 请求分析患者触诊数据
   * @param request 分析请求
   * @returns 分析结果
   */
  public async requestAnalysis(request: AnalysisRequest): Promise<TouchDiagnosisResponse> {
    try {
      const { patientId, diagnosisId } = request;
      Logger.info(`请求分析患者 ${patientId} 的触诊数据`);
      
      // 获取触诊记录
      let diagnosisRecord;
      if (diagnosisId) {
        diagnosisRecord = await TouchDiagnosisModel.findOne({ _id: diagnosisId });
      } else {
        diagnosisRecord = await TouchDiagnosisModel.findOne(
          { patientId },
          {},
          { sort: { date: -1 } }
        );
      }
      
      if (!diagnosisRecord) {
        return {
          success: false,
          error: '未找到触诊记录',
          message: '未找到要分析的触诊记录'
        };
      }
      
      // 使用分析引擎分析数据
      const analysisResults = await this.analysisEngine.analyze(
        patientId,
        diagnosisRecord.pulseData || [],
        diagnosisRecord.abdominalData || []
      );
      
      // 生成健康建议
      const recommendations = await this.suggestionsGenerator.generateSuggestions(
        patientId,
        analysisResults.constitutionTypes,
        analysisResults.healthImbalances
      );
      
      // 更新触诊记录的分析结果
      diagnosisRecord.analysisResults = {
        constitutionTypes: analysisResults.constitutionTypes,
        healthImbalances: analysisResults.healthImbalances,
        recommendations,
        severity: analysisResults.severity,
        confidence: analysisResults.confidence
      };
      
      await diagnosisRecord.save();
      
      // 向四诊合参服务发送数据（异步，不等待结果）
      this.notifyFourDiagnosisCoordinator(patientId, diagnosisRecord._id).catch(error => {
        Logger.error('通知四诊合参服务失败', { error, patientId });
      });
      
      return {
        success: true,
        data: {
          diagnosisId: diagnosisRecord._id,
          analysisResults: diagnosisRecord.analysisResults
        },
        message: '触诊数据分析成功'
      };
    } catch (error) {
      Logger.error(`分析触诊数据失败`, { error, patientId: request.patientId });
      return {
        success: false,
        error: error instanceof Error ? error.message : '分析触诊数据失败',
        message: '分析触诊数据时发生错误'
      };
    }
  }

  /**
   * 获取患者的触诊历史记录
   * @param query 历史查询参数
   * @returns 触诊历史记录
   */
  public async getPatientDiagnosisHistory(query: HistoryQuery): Promise<TouchDiagnosisResponse> {
    try {
      const { patientId, startDate, endDate, limit = 10, offset = 0 } = query;
      Logger.info(`获取患者 ${patientId} 的触诊历史记录`);
      
      // 构建查询条件
      const queryConditions: any = { patientId };
      
      if (startDate || endDate) {
        queryConditions.date = {};
        if (startDate) {
          queryConditions.date.$gte = new Date(startDate);
        }
        if (endDate) {
          queryConditions.date.$lte = new Date(endDate);
        }
      }
      
      // 获取患者的触诊历史记录
      const diagnosisRecords = await TouchDiagnosisModel.find(queryConditions)
        .sort({ date: -1 })
        .skip(offset)
        .limit(limit);
      
      // 获取记录总数
      const totalCount = await TouchDiagnosisModel.countDocuments(queryConditions);
      
      return {
        success: true,
        data: {
          records: diagnosisRecords,
          pagination: {
            total: totalCount,
            offset,
            limit,
            hasMore: offset + diagnosisRecords.length < totalCount
          }
        },
        message: '成功获取患者触诊历史记录'
      };
    } catch (error) {
      Logger.error(`获取患者触诊历史记录失败`, { error, patientId: query.patientId });
      return {
        success: false,
        error: error instanceof Error ? error.message : '获取患者触诊历史记录失败',
        message: '获取患者触诊历史记录时发生错误'
      };
    }
  }

  /**
   * 通知四诊合参服务新的触诊数据已添加
   * @param patientId 患者ID
   * @param diagnosisId 诊断ID
   */
  private async notifyFourDiagnosisCoordinator(patientId: string, diagnosisId: string): Promise<void> {
    try {
      const url = `${this.fourDiagnosisCoordinatorUrl}/notify`;
      await axios.post(url, {
        serviceType: 'touch-diagnosis',
        patientId,
        diagnosisId,
        timestamp: new Date().toISOString()
      });
      Logger.info(`已通知四诊合参服务，患者: ${patientId}, 诊断ID: ${diagnosisId}`);
    } catch (error) {
      Logger.error('通知四诊合参服务失败', { error, patientId, diagnosisId });
      // 不向上层抛出错误，以免影响主流程
    }
  }
}

export const touchDiagnosisService = new TouchDiagnosisService(); 