import { Service } from 'typedi';
import { v4 as uuidv4 } from 'uuid';
import { Logger } from '../utils/logger';
import { 
  InquirySession, 
  InquiryExchange,
  ExtractedSymptom,
  InquiryDiagnosis, 
  InquiryRequest,
  InquiryResponse
} from '../models/inquiry.model';
import { NotFoundError, BusinessError, AIServiceError } from '../utils/error-handler';
import { InquirySessionRepository } from '../db/repositories/inquiry-session.repository';
import { FourDiagnosisCoordinatorService } from '../integrations/four-diagnosis-coordinator.service';
import axios from 'axios';

/**
 * 问诊服务类
 * 处理问诊会话、提问处理、症状提取和诊断生成
 */
@Service()
export class InquiryService {
  private logger: Logger;
  
  constructor(
    private inquirySessionRepository: InquirySessionRepository,
    private coordinatorService: FourDiagnosisCoordinatorService
  ) {
    this.logger = new Logger('InquiryService');
  }

  /**
   * 创建新的问诊会话
   * @param userId 用户ID
   * @param patientInfo 患者基本信息
   * @param preferences 偏好设置
   * @returns 新创建的问诊会话
   */
  async createSession(
    userId: string, 
    patientInfo?: any,
    preferences?: any
  ): Promise<InquirySession> {
    this.logger.info(`创建问诊会话，用户ID: ${userId}`);
    
    try {
      // 创建会话并保存到数据库
      const session = await this.inquirySessionRepository.createSession(
        userId,
        patientInfo,
        preferences
      );
      
      return session;
    } catch (error) {
      this.logger.error(`创建问诊会话失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 更新会话首选项
   * @param sessionId 会话ID
   * @param preferences 首选项设置
   * @returns 更新后的会话
   */
  async updateSessionPreferences(sessionId: string, preferences: any): Promise<InquirySession> {
    this.logger.info(`更新会话首选项，会话ID: ${sessionId}`);
    
    try {
      // 更新会话首选项
      const updatedSession = await this.inquirySessionRepository.updateSessionPreferences(
        sessionId,
        preferences
      );
      
      return updatedSession;
    } catch (error) {
      this.logger.error(`更新会话首选项失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 获取会话
   * @param sessionId 会话ID
   * @returns 会话对象
   */
  async getSessionById(sessionId: string): Promise<InquirySession> {
    this.logger.info(`获取会话，会话ID: ${sessionId}`);
    
    try {
      return await this.inquirySessionRepository.getSessionById(sessionId);
    } catch (error) {
      this.logger.error(`获取会话失败: ${error.message}`, { error });
      throw error;
    }
  }

  /**
   * 获取用户的会话列表
   * @param userId 用户ID
   * @param limit 返回的数量限制
   * @param offset 偏移量
   * @returns 会话列表和总数
   */
  async getUserSessions(
    userId: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<{ sessions: InquirySession[], total: number }> {
    this.logger.info(`获取用户会话列表，用户ID: ${userId}`);
    
    try {
      return await this.inquirySessionRepository.getUserSessions(userId, limit, offset);
    } catch (error) {
      this.logger.error(`获取用户会话列表失败: ${error.message}`, { error });
      throw error;
    }
  }

  /**
   * 处理问诊请求
   * @param request 问诊请求
   * @returns 问诊响应
   */
  async processInquiry(request: InquiryRequest): Promise<InquiryResponse> {
    const { sessionId, userId, question } = request;
    this.logger.info(`处理问诊请求，会话ID: ${sessionId}, 用户ID: ${userId}`);
    
    try {
      // 检索现有会话
      const session = await this.inquirySessionRepository.getSessionById(sessionId);
      
      if (session.status !== 'active') {
        throw new BusinessError('会话已结束，无法处理问诊');
      }
      
      // 1. 生成回答
      const answer = await this.generateAnswer(question, session);
      
      // 2. 提取症状
      const extractedSymptoms = await this.extractSymptoms(question, answer, session);
      
      // 3. 创建交流记录
      const exchange: InquiryExchange = {
        exchangeId: uuidv4(),
        timestamp: new Date().toISOString(),
        question,
        answer,
        extractedSymptoms,
        intentType: 'symptom_description', // 默认意图类型
        confidence: 0.8 // 默认置信度
      };
      
      // 4. 更新会话
      await this.inquirySessionRepository.addExchange(sessionId, exchange);
      
      // 5. 检查是否应该生成诊断
      const shouldGenerateDiagnosis = this.shouldGenerateDiagnosis(session);
      
      if (shouldGenerateDiagnosis) {
        // 异步生成诊断，不阻塞响应
        this.generateDiagnosis(session).catch(err => {
          this.logger.error(`生成诊断失败: ${err.message}`, { sessionId, error: err });
        });
      }
      
      // 返回响应
      return {
        exchangeId: exchange.exchangeId,
        answer,
        extractedSymptoms,
        needMoreInfo: !shouldGenerateDiagnosis,
        suggestedFollowUps: shouldGenerateDiagnosis ? undefined : this.generateFollowUpQuestions(session),
        metadata: {
          processingTime: Date.now(),
          intentDetected: exchange.intentType
        }
      };
    } catch (error) {
      this.logger.error(`处理问诊请求失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 获取诊断结果
   * @param sessionId 会话ID
   * @returns 诊断结果
   */
  async getDiagnosis(sessionId: string): Promise<InquiryDiagnosis> {
    this.logger.info(`获取诊断结果，会话ID: ${sessionId}`);
    
    try {
      // 获取会话
      const session = await this.inquirySessionRepository.getSessionById(sessionId);
      
      if (!session.diagnosis) {
        throw new BusinessError('诊断结果尚未生成');
      }
      
      return session.diagnosis;
    } catch (error) {
      this.logger.error(`获取诊断结果失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 结束问诊会话
   * @param sessionId 会话ID
   * @returns 结束的会话
   */
  async endSession(sessionId: string): Promise<InquirySession> {
    this.logger.info(`结束问诊会话，会话ID: ${sessionId}`);
    
    try {
      // 获取会话
      const session = await this.inquirySessionRepository.getSessionById(sessionId);
      
      if (session.status === 'completed') {
        throw new BusinessError('会话已结束');
      }
      
      // 如果没有诊断结果，尝试生成一个
      if (!session.diagnosis && session.exchanges.length > 0) {
        try {
          await this.generateDiagnosis(session);
        } catch (error) {
          this.logger.error(`结束会话时生成诊断失败: ${error.message}`, { sessionId, error });
        }
      }
      
      // 结束会话
      const endedSession = await this.inquirySessionRepository.endSession(sessionId);
      
      // 如果有诊断结果，上报给四诊协调服务
      if (endedSession.diagnosis) {
        // 异步上报，不阻塞响应
        this.coordinatorService.reportInquiryDiagnosis(sessionId, endedSession.diagnosis)
          .then(success => {
            if (success) {
              this.logger.info(`问诊诊断结果上报成功，会话ID: ${sessionId}`);
            } else {
              this.logger.warn(`问诊诊断结果上报失败，会话ID: ${sessionId}`);
            }
          })
          .catch(error => {
            this.logger.error(`问诊诊断结果上报错误: ${error.message}`, { 
              sessionId, 
              diagnosisId: endedSession.diagnosis?.diagnosisId, 
              error 
            });
          });
      }
      
      return endedSession;
    } catch (error) {
      this.logger.error(`结束问诊会话失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 获取综合四诊结果
   * @param sessionId 会话ID
   * @returns 综合四诊结果
   */
  async getIntegratedDiagnosis(sessionId: string): Promise<any> {
    this.logger.info(`获取综合四诊结果，会话ID: ${sessionId}`);
    
    try {
      // 从四诊协调服务获取综合结果
      const integratedResult = await this.coordinatorService.getIntegratedDiagnosis(sessionId);
      
      if (!integratedResult) {
        this.logger.warn(`未获取到综合四诊结果，会话ID: ${sessionId}`);
        return null;
      }
      
      this.logger.info(`成功获取综合四诊结果，会话ID: ${sessionId}`);
      return integratedResult;
    } catch (error) {
      this.logger.error(`获取综合四诊结果失败: ${error.message}`);
      throw error;
    }
  }
  
  /**
   * 生成回答
   * @param question 用户问题
   * @param session 当前会话
   * @returns 生成的回答
   */
  private async generateAnswer(question: string, session: InquirySession): Promise<string> {
    try {
      // TODO: 调用LLM服务生成回答
      // 模拟LLM服务响应
      const previousExchanges = session.exchanges.map(ex => ({
        question: ex.question,
        answer: ex.answer
      }));
      
      // 实际项目中，这里应该调用AI服务
      // 示例：
      /*
      const response = await axios.post('http://localhost:3001/api/llm/generate', {
        prompt: question,
        context: {
          sessionId: session.sessionId,
          previousExchanges,
          patientInfo: session.patientInfo,
          extractedSymptoms: session.extractedSymptoms,
          preferences: session.preferences
        },
        type: 'inquiry_response'
      });
      return response.data.result;
      */
      
      // 模拟响应
      return `感谢您的描述。根据您所述的症状，我需要了解更多信息。请问这些症状持续多久了？是否有任何特定的时间或活动会加重或缓解症状？您是否有其他伴随的不适感？`;
    } catch (error) {
      this.logger.error(`生成回答失败: ${error.message}`, { error });
      throw new AIServiceError('生成回答失败，请稍后再试');
    }
  }
  
  /**
   * 提取症状
   * @param question 用户问题
   * @param answer 生成的回答
   * @param session 当前会话
   * @returns 提取的症状列表
   */
  private async extractSymptoms(
    question: string, 
    answer: string, 
    session: InquirySession
  ): Promise<ExtractedSymptom[]> {
    try {
      // TODO: 调用NLP服务提取症状
      // 模拟NLP服务响应
      
      // 实际项目中，这里应该调用NLP服务
      // 示例：
      /*
      const response = await axios.post('http://localhost:3002/api/nlp/extract-symptoms', {
        text: question,
        context: {
          sessionId: session.sessionId,
          previousExchanges: session.exchanges,
          answer
        }
      });
      return response.data.symptoms;
      */
      
      // 模拟响应
      if (question.includes('头痛') || question.includes('头疼')) {
        return [{
          name: '头痛',
          location: '头部',
          severity: 6,
          duration: '3天',
          frequency: '间歇性',
          characteristics: ['跳痛', '刺痛'],
          aggravatingFactors: ['工作压力', '睡眠不足'],
          relievingFactors: ['休息', '按摩'],
          associatedSymptoms: ['头晕', '疲劳'],
          confidence: 0.92
        }];
      }
      
      return [];
    } catch (error) {
      this.logger.error(`提取症状失败: ${error.message}`, { error });
      // 返回空数组而不是抛出异常，确保流程可以继续
      return [];
    }
  }
  
  /**
   * 检查是否应该生成诊断
   * @param session 当前会话
   * @returns 是否应该生成诊断
   */
  private shouldGenerateDiagnosis(session: InquirySession): boolean {
    if (!session.exchanges || session.exchanges.length === 0) {
      return false;
    }
    
    // 条件1: 至少有3次交流
    const hasEnoughExchanges = session.exchanges.length >= 3;
    
    // 条件2: 至少提取到2个不同症状
    const symptoms = new Set();
    session.exchanges.forEach(exchange => {
      if (exchange.extractedSymptoms) {
        exchange.extractedSymptoms.forEach(symptom => {
          symptoms.add(symptom.name);
        });
      }
    });
    const hasEnoughSymptoms = symptoms.size >= 2;
    
    // 条件3: 最近一次交流包含了关键信息
    const lastExchange = session.exchanges[session.exchanges.length - 1];
    const lastExchangeHasKeyInfo = 
      lastExchange && 
      ((lastExchange.extractedSymptoms && lastExchange.extractedSymptoms.length > 0) || 
       lastExchange.intentType === 'symptom_confirmation');
    
    return hasEnoughExchanges && hasEnoughSymptoms && lastExchangeHasKeyInfo;
  }
  
  /**
   * 生成诊断
   * @param session 当前会话
   * @returns 生成的诊断结果
   */
  private async generateDiagnosis(session: InquirySession): Promise<InquiryDiagnosis> {
    this.logger.info(`生成诊断，会话ID: ${session.sessionId}`);
    
    try {
      // 提取所有症状
      const allSymptoms: ExtractedSymptom[] = [];
      session.exchanges.forEach(exchange => {
        if (exchange.extractedSymptoms) {
          allSymptoms.push(...exchange.extractedSymptoms);
        }
      });
      
      // TODO: 调用诊断服务生成诊断
      // 实际项目中，这里应该调用诊断服务
      // 示例：
      /*
      const response = await axios.post('http://localhost:3003/api/diagnosis/generate', {
        sessionId: session.sessionId,
        userId: session.userId,
        patientInfo: session.patientInfo,
        symptoms: allSymptoms,
        preferences: session.preferences
      });
      const diagnosis = response.data.diagnosis;
      */
      
      // 模拟诊断结果
      const diagnosis: InquiryDiagnosis = {
        diagnosisId: uuidv4(),
        timestamp: new Date().toISOString(),
        tcmPatterns: [
          {
            pattern: '肝郁气滞',
            confidence: 0.85,
            relatedSymptoms: ['头痛', '情绪波动', '胸胁胀痛']
          },
          {
            pattern: '脾虚湿困',
            confidence: 0.65,
            relatedSymptoms: ['疲劳', '食欲不振', '腹胀']
          }
        ],
        mainSymptoms: allSymptoms.map(s => s.name),
        secondarySymptoms: [],
        constitution: {
          primary: '气郁质',
          secondary: ['痰湿质'],
          deviationLevel: 3
        },
        recommendations: {
          diet: [
            '宜清淡易消化食物',
            '多食用疏肝理气的食材，如柑橘、薄荷、玫瑰花茶',
            '少食辛辣、油腻、烧烤食物'
          ],
          lifestyle: [
            '保持情绪舒畅，避免过度紧张和焦虑',
            '适当增加户外活动，促进气血运行',
            '保持良好的作息，避免熬夜'
          ],
          remedies: [
            '可考虑使用舒肝和胃的中药调理',
            '按摩太冲穴、期门穴等疏肝理气穴位'
          ]
        },
        precautions: [
          '避免情绪剧烈波动',
          '避免过度疲劳'
        ],
        followUpQuestions: [
          '是否有胃部不适的症状？',
          '情绪变化和症状之间是否有明显关联？'
        ]
      };
      
      // 更新会话中的诊断结果
      await this.inquirySessionRepository.updateDiagnosis(session.sessionId, diagnosis);
      
      // 上报诊断结果给四诊协调服务
      this.coordinatorService.reportInquiryDiagnosis(session.sessionId, diagnosis)
        .then(success => {
          if (success) {
            this.logger.info(`问诊诊断结果上报成功，会话ID: ${session.sessionId}`);
          } else {
            this.logger.warn(`问诊诊断结果上报失败，会话ID: ${session.sessionId}`);
          }
        })
        .catch(error => {
          this.logger.error(`问诊诊断结果上报错误: ${error.message}`, { 
            sessionId: session.sessionId, 
            diagnosisId: diagnosis.diagnosisId, 
            error 
          });
        });
      
      return diagnosis;
    } catch (error) {
      this.logger.error(`生成诊断失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 生成后续问题
   * @param session 当前会话
   * @returns 后续问题数组
   */
  private generateFollowUpQuestions(session: InquirySession): string[] {
    // 根据会话内容生成有针对性的后续问题
    const questions = [
      '这些症状持续多久了？',
      '是否有特定的时间或情况会加重或减轻症状？',
      '您最近的饮食和睡眠情况如何？',
      '您有服用任何药物吗？'
    ];
    
    // 如果会话中已经有某些信息，避免重复询问
    // 这里简化处理，实际应用中应该有更复杂的逻辑
    return questions;
  }
}