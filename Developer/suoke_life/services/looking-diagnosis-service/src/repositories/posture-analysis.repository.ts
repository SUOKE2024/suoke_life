import { v4 as uuidv4 } from 'uuid';
import PostureDiagnosisModel, { PostureDiagnosis } from '../models/diagnosis/posture.model';
import { Logger } from '../utils/logger';

/**
 * 体态分析存储库类
 * 负责体态分析数据的存储和检索
 */
export class PostureAnalysisRepository {
  private logger = new Logger('PostureAnalysisRepository');
  
  /**
   * 保存体态分析诊断结果
   * @param postureDiagnosis 体态分析数据
   * @returns 保存的体态分析数据
   */
  async savePostureDiagnosis(postureDiagnosis: Partial<PostureDiagnosis>): Promise<PostureDiagnosis> {
    try {
      // 如果没有诊断ID，生成一个新的
      if (!postureDiagnosis.diagnosisId) {
        postureDiagnosis.diagnosisId = `ld-posture-${Date.now()}-${uuidv4().substring(0, 8)}`;
      }

      // 保存到数据库
      const newDiagnosis = new PostureDiagnosisModel(postureDiagnosis);
      return await newDiagnosis.save();
    } catch (error) {
      this.logger.error(`保存体态分析诊断失败: ${error.message}`);
      throw new Error(`保存体态分析诊断失败: ${error.message}`);
    }
  }

  /**
   * 通过ID获取体态分析诊断
   * @param diagnosisId 诊断ID
   * @returns 体态分析诊断数据
   */
  async getPostureDiagnosisById(diagnosisId: string): Promise<PostureDiagnosis | null> {
    try {
      return await PostureDiagnosisModel.findOne({ diagnosisId });
    } catch (error) {
      this.logger.error(`通过ID获取体态分析诊断失败: ${error.message}`);
      throw new Error(`通过ID获取体态分析诊断失败: ${error.message}`);
    }
  }

  /**
   * 获取用户的体态分析历史记录
   * @param userId 用户ID
   * @param limit 记录限制数
   * @param offset 偏移量
   * @returns 体态分析诊断记录列表
   */
  async getPostureDiagnosisByUserId(userId: string, limit: number = 10, offset: number = 0): Promise<PostureDiagnosis[]> {
    try {
      return await PostureDiagnosisModel.find({ userId })
        .sort({ timestamp: -1 })
        .skip(offset)
        .limit(limit);
    } catch (error) {
      this.logger.error(`获取用户体态分析历史记录失败: ${error.message}`);
      throw new Error(`获取用户体态分析历史记录失败: ${error.message}`);
    }
  }

  /**
   * 获取会话的体态分析历史记录
   * @param sessionId 会话ID
   * @param limit 记录限制数
   * @param offset 偏移量
   * @returns 体态分析诊断记录列表
   */
  async getPostureDiagnosisBySessionId(sessionId: string, limit: number = 10, offset: number = 0): Promise<PostureDiagnosis[]> {
    try {
      return await PostureDiagnosisModel.find({ sessionId })
        .sort({ timestamp: -1 })
        .skip(offset)
        .limit(limit);
    } catch (error) {
      this.logger.error(`获取会话体态分析历史记录失败: ${error.message}`);
      throw new Error(`获取会话体态分析历史记录失败: ${error.message}`);
    }
  }

  /**
   * 更新体态分析诊断记录
   * @param diagnosisId 诊断ID
   * @param updateData 更新数据
   * @returns 更新后的体态分析诊断记录
   */
  async updatePostureDiagnosis(diagnosisId: string, updateData: Partial<PostureDiagnosis>): Promise<PostureDiagnosis | null> {
    try {
      return await PostureDiagnosisModel.findOneAndUpdate(
        { diagnosisId },
        { $set: updateData },
        { new: true }
      );
    } catch (error) {
      this.logger.error(`更新体态分析诊断失败: ${error.message}`);
      throw new Error(`更新体态分析诊断失败: ${error.message}`);
    }
  }

  /**
   * 删除体态分析诊断记录
   * @param diagnosisId 诊断ID
   * @returns 操作结果
   */
  async deletePostureDiagnosis(diagnosisId: string): Promise<boolean> {
    try {
      const result = await PostureDiagnosisModel.deleteOne({ diagnosisId });
      return result.deletedCount > 0;
    } catch (error) {
      this.logger.error(`删除体态分析诊断失败: ${error.message}`);
      throw new Error(`删除体态分析诊断失败: ${error.message}`);
    }
  }
} 