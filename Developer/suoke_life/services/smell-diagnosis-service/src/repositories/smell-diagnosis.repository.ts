import { Service } from 'typedi';
import { Logger } from '../utils/logger';
import { 
  SmellAnalysisResultModel, 
  SmellDiagnosisResultModel,
  SmellAnalysisResultDocument,
  SmellDiagnosisResultDocument
} from '../database/schemas/smell-diagnosis.schema';
import { 
  SmellAnalysisResult, 
  SmellDiagnosisResult,
  SmellDiagnosisType
} from '../interfaces/smell-diagnosis.interface';
import { SmellAnalysisResultModel as SmellAnalysisResultDomainModel } from '../models/smell-diagnosis.model';
import { SmellDiagnosisResultModel as SmellDiagnosisResultDomainModel } from '../models/smell-diagnosis.model';

@Service()
export class SmellDiagnosisRepository {
  private logger: Logger;

  constructor() {
    this.logger = new Logger('SmellDiagnosisRepository');
  }

  /**
   * 保存气味分析结果
   * @param result 分析结果
   */
  async saveAnalysisResult(result: SmellAnalysisResult): Promise<SmellAnalysisResultDocument> {
    try {
      this.logger.info('保存气味分析结果', { userId: result.userId, smellType: result.smellType });
      
      const analysisResult = new SmellAnalysisResultModel({
        userId: result.userId,
        smellType: result.smellType,
        intensity: result.intensity,
        description: result.description,
        relatedConditions: result.relatedConditions,
        confidence: result.confidence,
        rawData: result.rawData,
        metadata: result.metadata
      });
      
      return await analysisResult.save();
    } catch (error) {
      this.logger.error('保存气味分析结果失败', { error: (error as Error).message });
      throw error;
    }
  }

  /**
   * 保存闻诊诊断结果
   * @param diagnosisResult 诊断结果
   * @param analysisResultIds 分析结果ID数组
   */
  async saveDiagnosisResult(
    diagnosisResult: SmellDiagnosisResult, 
    analysisResultIds: string[]
  ): Promise<SmellDiagnosisResultDocument> {
    try {
      this.logger.info('保存闻诊诊断结果', { 
        userId: diagnosisResult.userId, 
        requestId: diagnosisResult.requestId 
      });
      
      const result = new SmellDiagnosisResultModel({
        userId: diagnosisResult.userId,
        requestId: diagnosisResult.requestId,
        diagnosisType: diagnosisResult.diagnosisType,
        analysisResults: analysisResultIds,
        tcmImplications: diagnosisResult.tcmImplications,
        recommendations: diagnosisResult.recommendations,
        confidence: diagnosisResult.confidence,
        metadata: diagnosisResult.metadata
      });
      
      return await result.save();
    } catch (error) {
      this.logger.error('保存闻诊诊断结果失败', { error: (error as Error).message });
      throw error;
    }
  }

  /**
   * 获取用户的诊断历史记录
   * @param userId 用户ID
   * @param limit 限制条数
   * @param skip 跳过条数
   */
  async getUserDiagnosisHistory(
    userId: string,
    limit: number = 20,
    skip: number = 0
  ): Promise<SmellDiagnosisResultDomainModel[]> {
    try {
      this.logger.info('获取用户诊断历史', { userId, limit, skip });
      
      const results = await SmellDiagnosisResultModel
        .find({ userId })
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .populate('analysisResults')
        .exec();
      
      // 将数据库模型转换为领域模型
      return results.map(result => this.mapToDiagnosisResultDomain(result));
    } catch (error) {
      this.logger.error('获取用户诊断历史失败', { error: (error as Error).message });
      throw error;
    }
  }

  /**
   * 根据ID获取诊断结果
   * @param id 诊断结果ID
   */
  async getDiagnosisResultById(id: string): Promise<SmellDiagnosisResultDomainModel | null> {
    try {
      this.logger.info('根据ID获取诊断结果', { id });
      
      const result = await SmellDiagnosisResultModel
        .findById(id)
        .populate('analysisResults')
        .exec();
      
      return result ? this.mapToDiagnosisResultDomain(result) : null;
    } catch (error) {
      this.logger.error('根据ID获取诊断结果失败', { error: (error as Error).message });
      throw error;
    }
  }

  /**
   * 获取诊断类型统计
   * @param userId 用户ID
   */
  async getDiagnosisTypeStats(userId: string): Promise<Record<string, number>> {
    try {
      const stats = await SmellDiagnosisResultModel.aggregate([
        { $match: { userId } },
        { $group: { _id: '$diagnosisType', count: { $sum: 1 } } }
      ]);
      
      const result: Record<string, number> = {};
      stats.forEach((stat: any) => {
        result[stat._id] = stat.count;
      });
      
      return result;
    } catch (error) {
      this.logger.error('获取诊断类型统计失败', { error: (error as Error).message });
      throw error;
    }
  }

  /**
   * 将数据库模型映射为领域模型
   * @param dbModel 数据库模型
   */
  private mapToDiagnosisResultDomain(dbModel: SmellDiagnosisResultDocument): SmellDiagnosisResultDomainModel {
    // 映射分析结果
    const analysisResults = (dbModel.analysisResults as SmellAnalysisResultDocument[])
      .map(result => new SmellAnalysisResultDomainModel({
        id: result._id.toString(),
        userId: result.userId,
        timestamp: result.createdAt,
        smellType: result.smellType,
        intensity: result.intensity,
        description: result.description,
        relatedConditions: result.relatedConditions,
        confidence: result.confidence,
        rawData: result.rawData,
        metadata: result.metadata
      }));
      
    // 创建诊断结果领域模型
    return new SmellDiagnosisResultDomainModel({
      id: dbModel._id.toString(),
      userId: dbModel.userId,
      requestId: dbModel.requestId,
      timestamp: dbModel.createdAt,
      diagnosisType: dbModel.diagnosisType as SmellDiagnosisType,
      analysisResults,
      tcmImplications: dbModel.tcmImplications,
      recommendations: dbModel.recommendations,
      confidence: dbModel.confidence,
      metadata: dbModel.metadata
    });
  }
}