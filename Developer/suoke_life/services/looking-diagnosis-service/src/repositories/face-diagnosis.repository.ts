import { Service } from 'typedi';
import { FaceDiagnosisResult } from '../services/face-analysis/face-analysis.service';
import { FaceDiagnosisModel, FaceDiagnosisDocument } from '../models/database/face-diagnosis.model';
import { Logger } from '../utils/logger';

@Service()
export class FaceDiagnosisRepository {
  private logger = new Logger('FaceDiagnosisRepository');

  /**
   * 保存面诊结果到数据库
   * @param diagnosisResult 面诊分析结果
   * @param userId 可选的用户ID
   * @returns 保存的面诊文档
   */
  async saveDiagnosis(diagnosisResult: FaceDiagnosisResult, userId?: string): Promise<FaceDiagnosisDocument> {
    try {
      this.logger.info(`保存面诊结果，诊断ID: ${diagnosisResult.diagnosisId}`);
      
      const diagnosisData = {
        ...diagnosisResult,
        userId
      };
      
      const faceDiagnosis = new FaceDiagnosisModel(diagnosisData);
      const savedDiagnosis = await faceDiagnosis.save();
      
      this.logger.info(`面诊结果已保存，ID: ${savedDiagnosis._id}`);
      return savedDiagnosis;
    } catch (error) {
      this.logger.error(`保存面诊结果失败: ${error.message}`);
      throw new Error(`保存面诊结果失败: ${error.message}`);
    }
  }

  /**
   * 根据诊断ID获取面诊结果
   * @param diagnosisId 面诊记录ID
   * @returns 面诊文档或null
   */
  async getDiagnosisById(diagnosisId: string): Promise<FaceDiagnosisDocument | null> {
    try {
      this.logger.info(`查询面诊结果，诊断ID: ${diagnosisId}`);
      
      const diagnosis = await FaceDiagnosisModel.findOne({ diagnosisId });
      
      if (!diagnosis) {
        this.logger.warn(`未找到面诊结果，诊断ID: ${diagnosisId}`);
      }
      
      return diagnosis;
    } catch (error) {
      this.logger.error(`查询面诊结果失败: ${error.message}`);
      throw new Error(`查询面诊结果失败: ${error.message}`);
    }
  }

  /**
   * 获取面诊历史记录
   * @param filters 过滤条件
   * @param limit 返回记录数限制
   * @param offset 分页偏移量
   * @returns 面诊结果列表和总数
   */
  async getDiagnosisHistory(
    filters: { userId?: string; sessionId?: string },
    limit: number = 10,
    offset: number = 0
  ): Promise<{ results: FaceDiagnosisDocument[]; total: number }> {
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
      
      this.logger.info(`查询面诊历史记录，条件: ${JSON.stringify(query)}`);
      
      // 执行查询
      const results = await FaceDiagnosisModel.find(query)
        .sort({ createdAt: -1 }) // 按创建时间降序
        .skip(offset)
        .limit(limit);
      
      const total = await FaceDiagnosisModel.countDocuments(query);
      
      this.logger.info(`查询到 ${results.length} 条面诊记录，总数: ${total}`);
      
      return { results, total };
    } catch (error) {
      this.logger.error(`查询面诊历史记录失败: ${error.message}`);
      throw new Error(`查询面诊历史记录失败: ${error.message}`);
    }
  }

  /**
   * 删除面诊记录
   * @param diagnosisId 面诊记录ID
   * @returns 是否成功删除
   */
  async deleteDiagnosis(diagnosisId: string): Promise<boolean> {
    try {
      this.logger.info(`删除面诊结果，诊断ID: ${diagnosisId}`);
      
      const result = await FaceDiagnosisModel.deleteOne({ diagnosisId });
      
      if (result.deletedCount === 0) {
        this.logger.warn(`未找到要删除的面诊结果，诊断ID: ${diagnosisId}`);
        return false;
      }
      
      this.logger.info(`面诊结果已删除，诊断ID: ${diagnosisId}`);
      return true;
    } catch (error) {
      this.logger.error(`删除面诊结果失败: ${error.message}`);
      throw new Error(`删除面诊结果失败: ${error.message}`);
    }
  }
} 