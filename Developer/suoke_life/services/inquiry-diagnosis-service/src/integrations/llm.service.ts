import axios from 'axios';
import { Service } from 'typedi';
import { Logger } from '../utils/logger';
import { AIServiceError } from '../utils/error-handler';
import config from '../config';

/**
 * LLM服务集成类
 * 负责与大语言模型服务通信
 */
@Service()
export class LLMService {
  private logger: Logger;
  private apiUrl: string;
  
  constructor() {
    this.logger = new Logger('LLMService');
    this.apiUrl = config.serviceUrls.llmService || 'http://localhost:3001/api/llm';
  }
  
  /**
   * 生成回答
   * @param prompt 提示文本
   * @param context 上下文信息
   * @returns 生成的回答
   */
  async generateAnswer(prompt: string, context?: any): Promise<string> {
    try {
      this.logger.info('调用LLM服务生成回答');
      
      const response = await axios.post(`${this.apiUrl}/generate`, {
        prompt,
        context,
        options: {
          temperature: 0.7,
          maxTokens: 500
        }
      }, {
        timeout: 10000 // 10秒超时
      });
      
      return response.data.result;
    } catch (error) {
      this.logger.error(`LLM服务调用失败: ${error.message}`, { error });
      throw new AIServiceError('LLM服务暂时不可用，请稍后再试');
    }
  }
  
  /**
   * 生成多项选择结果
   * @param options 选项数组
   * @param context 上下文信息
   * @param criteria 选择标准
   * @returns 评分后的选项数组
   */
  async rankOptions(
    options: string[], 
    context: any, 
    criteria: string
  ): Promise<Array<{option: string, score: number}>> {
    try {
      this.logger.info('调用LLM服务对选项进行排序');
      
      const response = await axios.post(`${this.apiUrl}/rank`, {
        options,
        context,
        criteria
      }, {
        timeout: 10000 // 10秒超时
      });
      
      return response.data.results;
    } catch (error) {
      this.logger.error(`LLM排序服务调用失败: ${error.message}`, { error });
      throw new AIServiceError('LLM排序服务暂时不可用，请稍后再试');
    }
  }
  
  /**
   * 总结文本内容
   * @param text 待总结文本
   * @param maxLength 最大长度
   * @returns 总结内容
   */
  async summarizeText(text: string, maxLength: number = 200): Promise<string> {
    try {
      this.logger.info('调用LLM服务总结文本');
      
      const response = await axios.post(`${this.apiUrl}/summarize`, {
        text,
        maxLength
      }, {
        timeout: 8000 // 8秒超时
      });
      
      return response.data.summary;
    } catch (error) {
      this.logger.error(`LLM总结服务调用失败: ${error.message}`, { error });
      throw new AIServiceError('LLM总结服务暂时不可用，请稍后再试');
    }
  }
}