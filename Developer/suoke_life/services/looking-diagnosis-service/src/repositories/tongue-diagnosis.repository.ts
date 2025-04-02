import { Service } from 'typedi';
import { TongueDiagnosisResult } from '../models/diagnosis/tongue.model';
import { TongueDiagnosisModel, TongueDiagnosisDocument } from '../models/database/tongue-diagnosis.model';
import { Logger } from '../utils/logger';

@Service()
export class TongueDiagnosisRepository {
  private logger = new Logger('TongueDiagnosisRepository');

  /**
   * 保存舌诊结果到数据库
   * @param diagnosisResult 舌诊分析结果
   * @param userId 可选的用户ID
   * @returns 保存的舌诊文档
   */
  async saveDiagnosis(diagnosisResult: TongueDiagnosisResult, userId?: string): Promise<TongueDiagnosisDocument> {
    try {
      this.logger.info(`保存舌诊结果，诊断ID: ${diagnosisResult.diagnosisId}`);
      
      const diagnosisData = {
        ...diagnosisResult,
        userId
      };
      
      const tongueDiagnosis = new TongueDiagnosisModel(diagnosisData);
      const savedDiagnosis = await tongueDiagnosis.save();
      
      this.logger.info(`舌诊结果已保存，ID: ${savedDiagnosis._id}`);
      return savedDiagnosis;
    } catch (error) {
      this.logger.error(`保存舌诊结果失败: ${error.message}`);
      throw new Error(`保存舌诊结果失败: ${error.message}`);
    }
  }

  /**
   * 根据诊断ID获取舌诊结果
   * @param diagnosisId 舌诊记录ID
   * @returns 舌诊文档或null
   */
  async getDiagnosisById(diagnosisId: string): Promise<TongueDiagnosisDocument | null> {
    try {
      this.logger.info(`查询舌诊结果，诊断ID: ${diagnosisId}`);
      
      const diagnosis = await TongueDiagnosisModel.findOne({ diagnosisId });
      
      if (!diagnosis) {
        this.logger.warn(`未找到舌诊结果，诊断ID: ${diagnosisId}`);
      }
      
      return diagnosis;
    } catch (error) {
      this.logger.error(`查询舌诊结果失败: ${error.message}`);
      throw new Error(`查询舌诊结果失败: ${error.message}`);
    }
  }

  /**
   * 获取舌诊历史记录
   * @param filters 过滤条件
   * @param limit 返回记录数限制
   * @param offset 分页偏移量
   * @returns 舌诊结果列表和总数
   */
  async getDiagnosisHistory(
    filters: { userId?: string; sessionId?: string },
    limit: number = 10,
    offset: number = 0
  ): Promise<{ results: TongueDiagnosisDocument[]; total: number }> {
    try {
      const { userId, sessionId } = filters;
      
      // 构建查询条件
      const query: any = {};
      
      if (userId) {
        query.userId = userId;
      }
      
      if (sessionId) {
        query.sessionId = sessionId;
      }
      
      this.logger.info(`查询舌诊历史记录，条件: ${JSON.stringify(query)}`);
      
      // 执行查询
      const results = await TongueDiagnosisModel.find(query)
        .sort({ createdAt: -1 }) // 按创建时间降序
        .skip(offset)
        .limit(limit);
      
      const total = await TongueDiagnosisModel.countDocuments(query);
      
      this.logger.info(`查询到 ${results.length} 条舌诊记录，总数: ${total}`);
      
      return { results, total };
    } catch (error) {
      this.logger.error(`查询舌诊历史记录失败: ${error.message}`);
      throw new Error(`查询舌诊历史记录失败: ${error.message}`);
    }
  }

  /**
   * 删除舌诊记录
   * @param diagnosisId 舌诊记录ID
   * @returns 是否成功删除
   */
  async deleteDiagnosis(diagnosisId: string): Promise<boolean> {
    try {
      this.logger.info(`删除舌诊结果，诊断ID: ${diagnosisId}`);
      
      const result = await TongueDiagnosisModel.deleteOne({ diagnosisId });
      
      if (result.deletedCount === 0) {
        this.logger.warn(`未找到要删除的舌诊结果，诊断ID: ${diagnosisId}`);
        return false;
      }
      
      this.logger.info(`舌诊结果已删除，诊断ID: ${diagnosisId}`);
      return true;
    } catch (error) {
      this.logger.error(`删除舌诊结果失败: ${error.message}`);
      throw new Error(`删除舌诊结果失败: ${error.message}`);
    }
  }
} 