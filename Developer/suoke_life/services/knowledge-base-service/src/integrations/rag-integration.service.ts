/**
 * RAG集成服务
 * 负责将知识库数据同步到RAG服务
 */
import axios from 'axios';
import config from '../config';
import logger from '../utils/logger';
import { EnvironmentalHealthData } from '../interfaces/environmental-health.interface';
import { MentalHealthData } from '../interfaces/mental-health.interface';

export class RagIntegrationService {
  private apiUrl: string;
  private apiKey: string;

  constructor() {
    this.apiUrl = config.ragService.url;
    this.apiKey = config.ragService.apiKey;
  }

  /**
   * 获取API请求配置
   * @returns axios请求配置
   */
  private getRequestConfig() {
    return {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey
      }
    };
  }

  /**
   * 同步环境健康知识到RAG服务
   * @param data 环境健康数据
   */
  async syncEnvironmentalHealth(data: EnvironmentalHealthData): Promise<void> {
    try {
      logger.info('同步环境健康知识到RAG服务', { id: data._id });
      
      // 准备RAG文档数据
      const documentData = {
        id: data._id.toString(),
        collection: 'environmentalHealth',
        content: data.content,
        metadata: {
          title: data.title,
          description: data.description,
          environmentType: data.environmentType,
          pollutantType: data.pollutantType.join(', '),
          healthImpacts: data.healthImpacts.join(', '),
          riskLevel: data.riskLevel,
          vulnerableGroups: data.vulnerableGroups.join(', '),
          keywords: data.keywords.join(', '),
          regionSpecific: data.regionSpecific.join(', '),
          updatedAt: data.updatedAt.toISOString(),
          version: data.version
        }
      };
      
      // 同步到RAG服务
      await axios.post(
        `${this.apiUrl}/documents`,
        documentData,
        this.getRequestConfig()
      );
      
      logger.info('成功同步环境健康知识到RAG服务', { id: data._id });
    } catch (error) {
      logger.error('同步环境健康知识到RAG服务失败', { 
        error: (error as Error).message, 
        id: data._id 
      });
      
      // 不抛出异常，允许操作继续
      return;
    }
  }

  /**
   * 同步心理健康知识到RAG服务
   * @param data 心理健康数据
   */
  async syncMentalHealth(data: MentalHealthData): Promise<void> {
    try {
      logger.info('同步心理健康知识到RAG服务', { id: data._id });
      
      // 准备RAG文档数据
      const documentData = {
        id: data._id.toString(),
        collection: 'mentalHealth',
        content: data.content,
        metadata: {
          title: data.title,
          description: data.description,
          issueType: data.issueType,
          symptoms: data.symptoms.join(', '),
          interventionMethods: data.interventionMethods.join(', '),
          treatmentMethods: data.treatmentMethods.join(', '),
          selfHelpMeasures: data.selfHelpMeasures.join(', '),
          targetAgeGroups: data.targetAgeGroups.join(', '),
          keywords: data.keywords.join(', '),
          updatedAt: data.updatedAt.toISOString(),
          version: data.version
        }
      };
      
      // 同步到RAG服务
      await axios.post(
        `${this.apiUrl}/documents`,
        documentData,
        this.getRequestConfig()
      );
      
      logger.info('成功同步心理健康知识到RAG服务', { id: data._id });
    } catch (error) {
      logger.error('同步心理健康知识到RAG服务失败', { 
        error: (error as Error).message, 
        id: data._id 
      });
      
      // 不抛出异常，允许操作继续
      return;
    }
  }

  /**
   * 从RAG服务中删除环境健康知识
   * @param id 环境健康知识ID
   */
  async deleteEnvironmentalHealth(id: string): Promise<void> {
    try {
      logger.info('从RAG服务删除环境健康知识', { id });
      
      // 删除文档
      await axios.delete(
        `${this.apiUrl}/documents/${id}?collection=environmentalHealth`,
        this.getRequestConfig()
      );
      
      logger.info('成功从RAG服务删除环境健康知识', { id });
    } catch (error) {
      logger.error('从RAG服务删除环境健康知识失败', { 
        error: (error as Error).message, 
        id 
      });
      
      // 不抛出异常，允许操作继续
      return;
    }
  }

  /**
   * 从RAG服务中删除心理健康知识
   * @param id 心理健康知识ID
   */
  async deleteMentalHealth(id: string): Promise<void> {
    try {
      logger.info('从RAG服务删除心理健康知识', { id });
      
      // 删除文档
      await axios.delete(
        `${this.apiUrl}/documents/${id}?collection=mentalHealth`,
        this.getRequestConfig()
      );
      
      logger.info('成功从RAG服务删除心理健康知识', { id });
    } catch (error) {
      logger.error('从RAG服务删除心理健康知识失败', { 
        error: (error as Error).message, 
        id 
      });
      
      // 不抛出异常，允许操作继续
      return;
    }
  }
}