/**
 * 传统文化知识服务
 * 处理传统文化知识的业务逻辑
 */
import { KnowledgeService } from './knowledge.service';
import { TraditionalCultureKnowledgeModel, TraditionalCultureKnowledge, TraditionalCultureKnowledgeDocument } from '../models/traditional-culture-knowledge.model';
import { VectorDBService } from './vector-db.service';
import { logger } from '../utils/logger';
import mongoose from 'mongoose';

export class TraditionalCultureKnowledgeService extends KnowledgeService {
  constructor() {
    super(TraditionalCultureKnowledgeModel);
  }

  /**
   * 创建传统文化知识
   * @param knowledgeData 知识数据
   * @returns 创建的知识对象
   */
  async createTraditionalCultureKnowledge(knowledgeData: TraditionalCultureKnowledge): Promise<TraditionalCultureKnowledgeDocument> {
    try {
      // 创建知识条目
      const knowledge = await this.createKnowledgeEntry(knowledgeData);
      
      // 向量化知识内容（异步进行）
      this.vectorizeKnowledge(knowledge).catch(err => {
        logger.error(`向量化传统文化知识失败: ${err.message}`, { id: knowledge._id });
      });
      
      return knowledge;
    } catch (error) {
      logger.error('创建传统文化知识失败', error);
      throw error;
    }
  }

  /**
   * 更新传统文化知识
   * @param id 知识ID
   * @param knowledgeData 知识数据
   * @returns 更新后的知识对象
   */
  async updateTraditionalCultureKnowledge(id: string, knowledgeData: Partial<TraditionalCultureKnowledge>): Promise<TraditionalCultureKnowledgeDocument | null> {
    try {
      // 更新知识条目
      const knowledge = await this.updateKnowledgeEntry(id, knowledgeData);
      
      if (knowledge) {
        // 如果内容变更，重新向量化知识内容（异步进行）
        if (knowledgeData.content || knowledgeData.title || knowledgeData.summary) {
          knowledge.vectorized = false;
          await knowledge.save();
          
          this.vectorizeKnowledge(knowledge).catch(err => {
            logger.error(`重新向量化传统文化知识失败: ${err.message}`, { id: knowledge._id });
          });
        }
      }
      
      return knowledge;
    } catch (error) {
      logger.error(`更新传统文化知识失败, ID: ${id}`, error);
      throw error;
    }
  }

  /**
   * 获取传统文化知识详情
   * @param id 知识ID
   * @returns 知识对象
   */
  async getTraditionalCultureKnowledgeById(id: string): Promise<TraditionalCultureKnowledgeDocument | null> {
    try {
      return await TraditionalCultureKnowledgeModel.findById(id)
        .populate('categories')
        .populate('tags')
        .exec();
    } catch (error) {
      logger.error(`获取传统文化知识详情失败, ID: ${id}`, error);
      throw error;
    }
  }

  /**
   * 获取传统文化知识列表
   * @param page 页码
   * @param limit 每页数量
   * @param filter 过滤条件
   * @param sort 排序条件
   * @returns 知识列表及分页信息
   */
  async listTraditionalCultureKnowledge(
    page: number = 1,
    limit: number = 20,
    filter: any = {},
    sort: any = { createdAt: -1 }
  ) {
    try {
      const skip = (page - 1) * limit;
      const countPromise = TraditionalCultureKnowledgeModel.countDocuments(filter);
      const knowledgePromise = TraditionalCultureKnowledgeModel.find(filter)
        .populate('categories')
        .populate('tags')
        .sort(sort)
        .skip(skip)
        .limit(limit);
      
      const [total, data] = await Promise.all([countPromise, knowledgePromise]);
      
      return {
        data,
        pagination: {
          total,
          page,
          limit,
          pages: Math.ceil(total / limit)
        }
      };
    } catch (error) {
      logger.error('获取传统文化知识列表失败', error);
      throw error;
    }
  }

  /**
   * 删除传统文化知识
   * @param id 知识ID
   * @returns 删除结果
   */
  async deleteTraditionalCultureKnowledge(id: string): Promise<boolean> {
    try {
      const knowledge = await TraditionalCultureKnowledgeModel.findByIdAndDelete(id);
      
      if (knowledge) {
        // 删除向量数据库中的向量
        try {
          const vectorDBService = new VectorDBService();
          await vectorDBService.deleteVector(id);
        } catch (vectorError) {
          logger.error(`删除传统文化知识向量失败, ID: ${id}`, vectorError);
          // 向量删除失败不影响主流程
        }
        
        return true;
      }
      
      return false;
    } catch (error) {
      logger.error(`删除传统文化知识失败, ID: ${id}`, error);
      throw error;
    }
  }

  /**
   * 根据文化体系获取知识
   * @param culturalSystem 文化体系
   * @param page 页码
   * @param limit 每页数量
   * @returns 知识列表及分页信息
   */
  async getKnowledgeByCulturalSystem(
    culturalSystem: string,
    page: number = 1,
    limit: number = 20
  ) {
    try {
      return await this.listTraditionalCultureKnowledge(
        page,
        limit,
        { culturalSystem },
        { createdAt: -1 }
      );
    } catch (error) {
      logger.error(`根据文化体系获取知识失败, 体系: ${culturalSystem}`, error);
      throw error;
    }
  }

  /**
   * 获取易经卦象知识
   * @param name 卦名（可选）
   * @returns 卦象知识列表
   */
  async getHexagramKnowledge(name?: string) {
    try {
      const filter: any = { culturalSystem: 'yijing' };
      
      if (name) {
        filter.$or = [
          { title: { $regex: name, $options: 'i' } },
          { 'attributes.hexagramName': { $regex: name, $options: 'i' } }
        ];
      }
      
      const knowledge = await TraditionalCultureKnowledgeModel.find(filter)
        .populate('categories')
        .populate('tags')
        .sort({ title: 1 });
      
      return knowledge;
    } catch (error) {
      logger.error('获取易经卦象知识失败', error);
      throw error;
    }
  }

  /**
   * 根据历史时期获取知识
   * @param historicalPeriod 历史时期
   * @param page 页码
   * @param limit 每页数量
   * @returns 知识列表及分页信息
   */
  async getKnowledgeByHistoricalPeriod(
    historicalPeriod: string,
    page: number = 1,
    limit: number = 20
  ) {
    try {
      return await this.listTraditionalCultureKnowledge(
        page,
        limit,
        { historicalPeriod },
        { createdAt: -1 }
      );
    } catch (error) {
      logger.error(`根据历史时期获取知识失败, 时期: ${historicalPeriod}`, error);
      throw error;
    }
  }

  /**
   * 向量化知识
   * @param knowledge 知识对象
   */
  private async vectorizeKnowledge(knowledge: TraditionalCultureKnowledgeDocument): Promise<void> {
    try {
      // 检查是否已向量化
      if (knowledge.vectorized) {
        return;
      }
      
      // 准备向量化文本
      const text = [
        knowledge.title,
        knowledge.summary,
        knowledge.content,
        knowledge.originalText,
        knowledge.interpretation
      ].filter(Boolean).join('\n');
      
      // 向量化
      const vectorDBService = new VectorDBService();
      await vectorDBService.storeVector(knowledge._id.toString(), text, {
        type: 'traditional-culture',
        culturalSystem: knowledge.culturalSystem,
        historicalPeriod: knowledge.historicalPeriod,
        title: knowledge.title
      });
      
      // 更新向量化状态
      knowledge.vectorized = true;
      await knowledge.save();
      
      logger.info(`传统文化知识向量化成功, ID: ${knowledge._id}`);
    } catch (error) {
      logger.error(`传统文化知识向量化失败, ID: ${knowledge._id}`, error);
      throw error;
    }
  }
}