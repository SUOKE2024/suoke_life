/**
 * 知识图谱集成服务
 * 负责将知识库数据同步到知识图谱服务
 */
import axios from 'axios';
import config from '../config';
import logger from '../utils/logger';
import { EnvironmentalHealthData } from '../interfaces/environmental-health.interface';
import { MentalHealthData } from '../interfaces/mental-health.interface';

export class KnowledgeGraphIntegrationService {
  private apiUrl: string;
  private apiKey: string;

  constructor() {
    this.apiUrl = config.knowledgeGraphService.url;
    this.apiKey = config.knowledgeGraphService.apiKey;
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
   * 同步环境健康知识到知识图谱
   * @param data 环境健康数据
   */
  async syncEnvironmentalHealth(data: EnvironmentalHealthData): Promise<void> {
    try {
      logger.info('同步环境健康知识到知识图谱', { id: data._id });
      
      // 准备知识图谱节点数据
      const nodeData = {
        id: data._id.toString(),
        type: 'EnvironmentalHealth',
        properties: {
          title: data.title,
          description: data.description,
          environmentType: data.environmentType,
          pollutantType: data.pollutantType,
          healthImpacts: data.healthImpacts,
          riskLevel: data.riskLevel,
          keywords: data.keywords,
          updatedAt: data.updatedAt,
          version: data.version
        }
      };
      
      // 同步到知识图谱
      await axios.post(
        `${this.apiUrl}/nodes`,
        nodeData,
        this.getRequestConfig()
      );
      
      // 创建关系
      if (data.relatedKnowledge && data.relatedKnowledge.length > 0) {
        for (const relatedId of data.relatedKnowledge) {
          // 只处理字符串ID，忽略已填充的文档
          if (typeof relatedId === 'string') {
            const relationData = {
              fromId: data._id.toString(),
              toId: relatedId,
              type: 'RELATED_TO',
              properties: {
                createdAt: new Date()
              }
            };
            
            await axios.post(
              `${this.apiUrl}/relationships`,
              relationData,
              this.getRequestConfig()
            );
          }
        }
      }
      
      logger.info('成功同步环境健康知识到知识图谱', { id: data._id });
    } catch (error) {
      logger.error('同步环境健康知识到知识图谱失败', { 
        error: (error as Error).message, 
        id: data._id 
      });
      
      // 不抛出异常，允许操作继续
      return;
    }
  }

  /**
   * 同步心理健康知识到知识图谱
   * @param data 心理健康数据
   */
  async syncMentalHealth(data: MentalHealthData): Promise<void> {
    try {
      logger.info('同步心理健康知识到知识图谱', { id: data._id });
      
      // 准备知识图谱节点数据
      const nodeData = {
        id: data._id.toString(),
        type: 'MentalHealth',
        properties: {
          title: data.title,
          description: data.description,
          issueType: data.issueType,
          symptoms: data.symptoms,
          interventionMethods: data.interventionMethods,
          treatmentMethods: data.treatmentMethods,
          keywords: data.keywords,
          targetAgeGroups: data.targetAgeGroups,
          updatedAt: data.updatedAt,
          version: data.version
        }
      };
      
      // 同步到知识图谱
      await axios.post(
        `${this.apiUrl}/nodes`,
        nodeData,
        this.getRequestConfig()
      );
      
      // 创建关系
      if (data.relatedKnowledge && data.relatedKnowledge.length > 0) {
        for (const relatedId of data.relatedKnowledge) {
          // 只处理字符串ID，忽略已填充的文档
          if (typeof relatedId === 'string') {
            const relationData = {
              fromId: data._id.toString(),
              toId: relatedId,
              type: 'RELATED_TO',
              properties: {
                createdAt: new Date()
              }
            };
            
            await axios.post(
              `${this.apiUrl}/relationships`,
              relationData,
              this.getRequestConfig()
            );
          }
        }
      }
      
      logger.info('成功同步心理健康知识到知识图谱', { id: data._id });
    } catch (error) {
      logger.error('同步心理健康知识到知识图谱失败', { 
        error: (error as Error).message, 
        id: data._id 
      });
      
      // 不抛出异常，允许操作继续
      return;
    }
  }

  /**
   * 从知识图谱中删除环境健康知识
   * @param id 环境健康知识ID
   */
  async deleteEnvironmentalHealth(id: string): Promise<void> {
    try {
      logger.info('从知识图谱删除环境健康知识', { id });
      
      // 删除节点（这将自动删除相关的边）
      await axios.delete(
        `${this.apiUrl}/nodes/${id}`,
        this.getRequestConfig()
      );
      
      logger.info('成功从知识图谱删除环境健康知识', { id });
    } catch (error) {
      logger.error('从知识图谱删除环境健康知识失败', { 
        error: (error as Error).message, 
        id 
      });
      
      // 不抛出异常，允许操作继续
      return;
    }
  }

  /**
   * 从知识图谱中删除心理健康知识
   * @param id 心理健康知识ID
   */
  async deleteMentalHealth(id: string): Promise<void> {
    try {
      logger.info('从知识图谱删除心理健康知识', { id });
      
      // 删除节点（这将自动删除相关的边）
      await axios.delete(
        `${this.apiUrl}/nodes/${id}`,
        this.getRequestConfig()
      );
      
      logger.info('成功从知识图谱删除心理健康知识', { id });
    } catch (error) {
      logger.error('从知识图谱删除心理健康知识失败', { 
        error: (error as Error).message, 
        id 
      });
      
      // 不抛出异常，允许操作继续
      return;
    }
  }
}