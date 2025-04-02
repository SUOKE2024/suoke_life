import { Service } from 'typedi';
import { InquirySessionModel, InquirySessionDocument } from '../models/inquiry-session.model';
import { InquirySession, InquiryExchange, InquiryDiagnosis } from '../../models/inquiry.model';
import { NotFoundError, DatabaseError } from '../../utils/error-handler';
import { Logger } from '../../utils/logger';
import { v4 as uuidv4 } from 'uuid';

/**
 * 问诊会话仓储类
 * 处理问诊会话数据的存储和检索
 */
@Service()
export class InquirySessionRepository {
  private logger: Logger;
  
  constructor() {
    this.logger = new Logger('InquirySessionRepository');
  }
  
  /**
   * 创建新的问诊会话
   * @param userId 用户ID
   * @param patientInfo 患者信息
   * @param preferences 偏好设置
   * @returns 创建的问诊会话
   */
  async createSession(
    userId: string,
    patientInfo?: any,
    preferences?: any
  ): Promise<InquirySession> {
    try {
      const sessionId = uuidv4();
      
      this.logger.info(`创建问诊会话: ${sessionId}, 用户: ${userId}`);
      
      const session = new InquirySessionModel({
        sessionId,
        userId,
        patientInfo,
        preferences,
        exchanges: [],
        status: 'active'
      });
      
      await session.save();
      
      return session.toResponse();
    } catch (error) {
      this.logger.error('创建问诊会话失败', { error, userId });
      throw new DatabaseError(`创建问诊会话失败: ${error.message}`);
    }
  }
  
  /**
   * 通过ID获取问诊会话
   * @param sessionId 会话ID
   * @returns 问诊会话
   * @throws NotFoundError 如果会话不存在
   */
  async getSessionById(sessionId: string): Promise<InquirySession> {
    try {
      const session = await InquirySessionModel.findOne({ sessionId });
      
      if (!session) {
        throw new NotFoundError(`未找到会话: ${sessionId}`);
      }
      
      return session.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('获取问诊会话失败', { error, sessionId });
      throw new DatabaseError(`获取问诊会话失败: ${error.message}`);
    }
  }
  
  /**
   * 获取用户的问诊会话列表
   * @param userId 用户ID
   * @param limit 结果限制
   * @param offset 结果偏移
   * @returns 问诊会话数组
   */
  async getUserSessions(
    userId: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<{ sessions: InquirySession[], total: number }> {
    try {
      // 获取总数
      const total = await InquirySessionModel.countDocuments({ userId });
      
      // 获取分页数据
      const sessions = await InquirySessionModel.find({ userId })
        .sort({ createdAt: -1 })
        .skip(offset)
        .limit(limit);
      
      return {
        sessions: sessions.map(session => session.toResponse()),
        total
      };
    } catch (error) {
      this.logger.error('获取用户问诊会话列表失败', { error, userId });
      throw new DatabaseError(`获取用户问诊会话列表失败: ${error.message}`);
    }
  }
  
  /**
   * 更新会话偏好设置
   * @param sessionId 会话ID
   * @param preferences 偏好设置
   * @returns 更新后的会话
   * @throws NotFoundError 如果会话不存在
   */
  async updateSessionPreferences(
    sessionId: string,
    preferences: any
  ): Promise<InquirySession> {
    try {
      const session = await InquirySessionModel.findOne({ sessionId });
      
      if (!session) {
        throw new NotFoundError(`未找到会话: ${sessionId}`);
      }
      
      // 更新偏好设置
      session.preferences = {
        ...session.preferences,
        ...preferences
      };
      
      await session.save();
      
      return session.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('更新会话偏好设置失败', { error, sessionId });
      throw new DatabaseError(`更新会话偏好设置失败: ${error.message}`);
    }
  }
  
  /**
   * 添加问诊交互
   * @param sessionId 会话ID
   * @param exchange 问诊交互
   * @returns 更新后的会话
   * @throws NotFoundError 如果会话不存在
   */
  async addExchange(
    sessionId: string,
    exchange: InquiryExchange
  ): Promise<InquirySession> {
    try {
      const session = await InquirySessionModel.findOne({ sessionId });
      
      if (!session) {
        throw new NotFoundError(`未找到会话: ${sessionId}`);
      }
      
      // 添加交互
      session.exchanges.push(exchange);
      
      await session.save();
      
      return session.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('添加问诊交互失败', { error, sessionId });
      throw new DatabaseError(`添加问诊交互失败: ${error.message}`);
    }
  }
  
  /**
   * 更新会话诊断
   * @param sessionId 会话ID
   * @param diagnosis 诊断结果
   * @returns 更新后的会话
   * @throws NotFoundError 如果会话不存在
   */
  async updateDiagnosis(
    sessionId: string,
    diagnosis: InquiryDiagnosis
  ): Promise<InquirySession> {
    try {
      const session = await InquirySessionModel.findOne({ sessionId });
      
      if (!session) {
        throw new NotFoundError(`未找到会话: ${sessionId}`);
      }
      
      // 更新诊断
      session.diagnosis = diagnosis;
      
      await session.save();
      
      return session.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('更新会话诊断失败', { error, sessionId });
      throw new DatabaseError(`更新会话诊断失败: ${error.message}`);
    }
  }
  
  /**
   * 结束问诊会话
   * @param sessionId 会话ID
   * @returns 更新后的会话
   * @throws NotFoundError 如果会话不存在
   */
  async endSession(sessionId: string): Promise<InquirySession> {
    try {
      const session = await InquirySessionModel.findOne({ sessionId });
      
      if (!session) {
        throw new NotFoundError(`未找到会话: ${sessionId}`);
      }
      
      // 更新状态
      session.status = 'completed';
      
      await session.save();
      
      return session.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('结束问诊会话失败', { error, sessionId });
      throw new DatabaseError(`结束问诊会话失败: ${error.message}`);
    }
  }
  
  /**
   * 放弃问诊会话
   * @param sessionId 会话ID
   * @returns 更新后的会话
   * @throws NotFoundError 如果会话不存在
   */
  async abandonSession(sessionId: string): Promise<InquirySession> {
    try {
      const session = await InquirySessionModel.findOne({ sessionId });
      
      if (!session) {
        throw new NotFoundError(`未找到会话: ${sessionId}`);
      }
      
      // 更新状态
      session.status = 'abandoned';
      
      await session.save();
      
      return session.toResponse();
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      this.logger.error('放弃问诊会话失败', { error, sessionId });
      throw new DatabaseError(`放弃问诊会话失败: ${error.message}`);
    }
  }
}