import axios from 'axios';
import { Service } from 'typedi';
import { Logger } from '../utils/logger';
import { AIServiceError } from '../utils/error-handler';
import config from '../config';

/**
 * NLP服务集成类
 * 负责与自然语言处理服务通信，处理症状提取等任务
 */
@Service()
export class NLPService {
  private logger: Logger;
  private apiUrl: string;
  
  constructor() {
    this.logger = new Logger('NLPService');
    this.apiUrl = config.serviceUrls.nlpService || 'http://localhost:3002/api/nlp';
  }
  
  /**
   * 从文本中提取症状
   * @param text 文本内容
   * @param context 上下文信息
   * @returns 提取的症状数组
   */
  async extractSymptoms(text: string, context?: any): Promise<any[]> {
    try {
      this.logger.info('从文本中提取症状');
      
      const response = await axios.post(`${this.apiUrl}/extract-symptoms`, {
        text,
        context
      }, {
        timeout: 5000 // 5秒超时
      });
      
      return response.data.symptoms;
    } catch (error) {
      this.logger.error(`NLP症状提取服务调用失败: ${error.message}`, { error });
      throw new AIServiceError('NLP症状提取服务暂时不可用，请稍后再试');
    }
  }
  
  /**
   * 分析文本情感
   * @param text 文本内容
   * @returns 情感分析结果
   */
  async analyzeSentiment(text: string): Promise<{
    sentiment: 'positive' | 'negative' | 'neutral',
    score: number
  }> {
    try {
      this.logger.info('分析文本情感');
      
      const response = await axios.post(`${this.apiUrl}/sentiment`, {
        text
      }, {
        timeout: 3000 // 3秒超时
      });
      
      return response.data.result;
    } catch (error) {
      this.logger.error(`情感分析服务调用失败: ${error.message}`, { error });
      // 返回默认值而不是抛出错误，确保业务流程可以继续
      return {
        sentiment: 'neutral',
        score: 0.5
      };
    }
  }
  
  /**
   * 分析文本关键词
   * @param text 文本内容
   * @param limit 关键词数量限制
   * @returns 关键词数组
   */
  async extractKeywords(text: string, limit: number = 5): Promise<string[]> {
    try {
      this.logger.info('提取文本关键词');
      
      const response = await axios.post(`${this.apiUrl}/keywords`, {
        text,
        limit
      }, {
        timeout: 3000 // 3秒超时
      });
      
      return response.data.keywords;
    } catch (error) {
      this.logger.error(`关键词提取服务调用失败: ${error.message}`, { error });
      // 简单分词代替，确保业务流程可以继续
      return text.split(/\s+/).slice(0, limit);
    }
  }
  
  /**
   * 对两段文本进行相似度计算
   * @param text1 文本1
   * @param text2 文本2
   * @returns 相似度分数(0-1)
   */
  async calculateSimilarity(text1: string, text2: string): Promise<number> {
    try {
      this.logger.info('计算文本相似度');
      
      const response = await axios.post(`${this.apiUrl}/similarity`, {
        text1,
        text2
      }, {
        timeout: 3000 // 3秒超时
      });
      
      return response.data.similarity;
    } catch (error) {
      this.logger.error(`相似度计算服务调用失败: ${error.message}`, { error });
      // 返回默认值而不是抛出错误
      return 0.5;
    }
  }
}