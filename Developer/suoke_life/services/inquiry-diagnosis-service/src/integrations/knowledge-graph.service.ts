import axios from 'axios';
import { Service } from 'typedi';
import { Logger } from '../utils/logger';
import { AIServiceError } from '../utils/error-handler';
import config from '../config';

/**
 * 知识图谱服务集成类
 * 负责与知识图谱服务通信
 */
@Service()
export class KnowledgeGraphService {
  private logger: Logger;
  private apiUrl: string;
  
  constructor() {
    this.logger = new Logger('KnowledgeGraphService');
    this.apiUrl = config.serviceUrls.knowledgeGraphService || 'http://localhost:3003/api/knowledge-graph';
  }
  
  /**
   * 查询症状相关知识
   * @param symptom 症状名称
   * @returns 症状相关知识
   */
  async querySymptomKnowledge(symptom: string): Promise<any> {
    try {
      this.logger.info(`查询症状相关知识: ${symptom}`);
      
      const response = await axios.get(`${this.apiUrl}/symptoms`, {
        params: { query: symptom },
        timeout: 5000 // 5秒超时
      });
      
      return response.data.results;
    } catch (error) {
      this.logger.error(`知识图谱服务调用失败: ${error.message}`, { error });
      throw new AIServiceError('知识图谱服务暂时不可用，请稍后再试');
    }
  }
  
  /**
   * 查询证型相关知识
   * @param pattern 证型名称
   * @returns 证型相关知识
   */
  async queryPatternKnowledge(pattern: string): Promise<any> {
    try {
      this.logger.info(`查询证型相关知识: ${pattern}`);
      
      const response = await axios.get(`${this.apiUrl}/patterns`, {
        params: { query: pattern },
        timeout: 5000 // 5秒超时
      });
      
      return response.data.results;
    } catch (error) {
      this.logger.error(`知识图谱服务调用失败: ${error.message}`, { error });
      throw new AIServiceError('知识图谱服务暂时不可用，请稍后再试');
    }
  }
  
  /**
   * 查询症状-证型关系
   * @param symptoms 症状数组
   * @returns 证型关系数据
   */
  async querySymptomPatternRelations(symptoms: string[]): Promise<any> {
    try {
      this.logger.info(`查询症状-证型关系，症状数量: ${symptoms.length}`);
      
      const response = await axios.post(`${this.apiUrl}/relations/symptom-pattern`, {
        symptoms
      }, {
        timeout: 5000 // 5秒超时
      });
      
      return response.data.relations;
    } catch (error) {
      this.logger.error(`知识图谱关系查询失败: ${error.message}`, { error });
      throw new AIServiceError('知识图谱关系查询服务暂时不可用，请稍后再试');
    }
  }
  
  /**
   * 获取证型对应推荐
   * @param patterns 证型数组
   * @returns 推荐数据
   */
  async getPatternRecommendations(patterns: string[]): Promise<any> {
    try {
      this.logger.info(`获取证型推荐，证型数量: ${patterns.length}`);
      
      const response = await axios.post(`${this.apiUrl}/recommendations`, {
        patterns
      }, {
        timeout: 5000 // 5秒超时
      });
      
      return response.data.recommendations;
    } catch (error) {
      this.logger.error(`推荐服务调用失败: ${error.message}`, { error });
      throw new AIServiceError('推荐服务暂时不可用，请稍后再试');
    }
  }
}