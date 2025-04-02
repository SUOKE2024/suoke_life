import { Service } from 'typedi';
import { DiagnosisResultModel, DiagnosisResultDocument } from '../models/diagnosis-result.model';
import { DiagnosisResult } from '../../models/diagnosis.model';
import { NotFoundError, DatabaseError } from '../../utils/error-handler';
import { Logger } from '../../utils/logger';
import { v4 as uuidv4 } from 'uuid';

/**
 * 诊断结果仓储类
 * 处理诊断结果数据的存储和检索
 */
@Service()
export class DiagnosisResultRepository {
  private logger: Logger;
  
  constructor() {
    this.logger = new Logger('DiagnosisResultRepository');
  }
  
  /**
   * 创建新的诊断结果
   * @param diagnosis 诊断结果
   * @returns 创建的诊断结果
   */
  async createDiagnosis(diagnosis: Omit<DiagnosisResult, 'diagnosisId'>): Promise<DiagnosisResult> {
    try {
      const diagnosisId = diagnosis.diagnosisId || uuidv4();
      
      this.logger.info(`创建诊断结果: ${diagnosisId}, 会话: ${diagnosis.sessionId}, 用户: ${diagnosis.userId}`);
      
      const diagnosisResult = new DiagnosisResultModel({
        ...diagnosis,
        diagnosisId
      });
      
      await diagnosisResult.save();
      
      return diagnosisResult.toResponse();
    } catch (error) {
      this.logger.error('创建诊断结果失败', { error, sessionId: diagnosis.sessionId });
      throw new DatabaseError(`创建诊断结果失败: ${error.message}`);
    }
  }
  
  /**
   * 通过ID获取诊断结果
   * @param diagnosisId 诊断ID
   * @returns 诊断结果
   * @throws NotFoundError 如果诊断结果不存在
   */
  async getDiagnosisById(diagnosisId: string): Promise<DiagnosisResult> {
    try {
      const diagnosis = await DiagnosisResultModel.findOne({ diagnosisId });
      
      if (!diagnosis) {
        throw new NotFoundError(`未找到诊断结果: ${diagnosisId}`);
      }
      
      return diagnosis.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('获取诊断结果失败', { error, diagnosisId });
      throw new DatabaseError(`获取诊断结果失败: ${error.message}`);
    }
  }
  
  /**
   * 通过会话ID获取诊断结果
   * @param sessionId 会话ID
   * @returns 诊断结果
   * @throws NotFoundError 如果诊断结果不存在
   */
  async getDiagnosisBySessionId(sessionId: string): Promise<DiagnosisResult> {
    try {
      const diagnosis = await DiagnosisResultModel.findOne({ sessionId });
      
      if (!diagnosis) {
        throw new NotFoundError(`未找到会话对应的诊断结果: ${sessionId}`);
      }
      
      return diagnosis.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('获取会话诊断结果失败', { error, sessionId });
      throw new DatabaseError(`获取会话诊断结果失败: ${error.message}`);
    }
  }
  
  /**
   * 获取用户的诊断历史
   * @param userId 用户ID
   * @param limit 结果限制
   * @param offset 结果偏移
   * @returns 诊断结果数组
   */
  async getUserDiagnosisHistory(
    userId: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<{ diagnoses: DiagnosisResult[], total: number }> {
    try {
      // 获取总数
      const total = await DiagnosisResultModel.countDocuments({ userId });
      
      // 获取分页数据
      const diagnoses = await DiagnosisResultModel.find({ userId })
        .sort({ timestamp: -1 })
        .skip(offset)
        .limit(limit);
      
      return {
        diagnoses: diagnoses.map(diagnosis => diagnosis.toResponse()),
        total
      };
    } catch (error) {
      this.logger.error('获取用户诊断历史失败', { error, userId });
      throw new DatabaseError(`获取用户诊断历史失败: ${error.message}`);
    }
  }
  
  /**
   * 获取特定体质类型的诊断结果
   * @param constitutionType 体质类型
   * @param limit 结果限制
   * @param offset 结果偏移
   * @returns 诊断结果数组
   */
  async getDiagnosesByConstitutionType(
    constitutionType: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<{ diagnoses: DiagnosisResult[], total: number }> {
    try {
      // 获取总数
      const total = await DiagnosisResultModel.countDocuments({
        'constitutionAnalysis.primaryType': constitutionType
      });
      
      // 获取分页数据
      const diagnoses = await DiagnosisResultModel.find({
        'constitutionAnalysis.primaryType': constitutionType
      })
        .sort({ timestamp: -1 })
        .skip(offset)
        .limit(limit);
      
      return {
        diagnoses: diagnoses.map(diagnosis => diagnosis.toResponse()),
        total
      };
    } catch (error) {
      this.logger.error('获取体质类型诊断结果失败', { error, constitutionType });
      throw new DatabaseError(`获取体质类型诊断结果失败: ${error.message}`);
    }
  }
  
  /**
   * 更新诊断结果
   * @param diagnosisId 诊断ID
   * @param updateData 更新数据
   * @returns 更新后的诊断结果
   * @throws NotFoundError 如果诊断结果不存在
   */
  async updateDiagnosis(
    diagnosisId: string,
    updateData: Partial<DiagnosisResult>
  ): Promise<DiagnosisResult> {
    try {
      const diagnosis = await DiagnosisResultModel.findOne({ diagnosisId });
      
      if (!diagnosis) {
        throw new NotFoundError(`未找到诊断结果: ${diagnosisId}`);
      }
      
      // 禁止更新关键字段
      delete updateData.diagnosisId;
      delete updateData.sessionId;
      delete updateData.userId;
      delete updateData.timestamp;
      
      // 更新诊断结果
      Object.assign(diagnosis, updateData);
      
      await diagnosis.save();
      
      return diagnosis.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('更新诊断结果失败', { error, diagnosisId });
      throw new DatabaseError(`更新诊断结果失败: ${error.message}`);
    }
  }
  
  /**
   * 删除诊断结果
   * @param diagnosisId 诊断ID
   * @returns 是否成功删除
   * @throws NotFoundError 如果诊断结果不存在
   */
  async deleteDiagnosis(diagnosisId: string): Promise<boolean> {
    try {
      const result = await DiagnosisResultModel.deleteOne({ diagnosisId });
      
      if (result.deletedCount === 0) {
        throw new NotFoundError(`未找到诊断结果: ${diagnosisId}`);
      }
      
      this.logger.info(`已删除诊断结果: ${diagnosisId}`);
      
      return true;
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('删除诊断结果失败', { error, diagnosisId });
      throw new DatabaseError(`删除诊断结果失败: ${error.message}`);
    }
  }
}