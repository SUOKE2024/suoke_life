/**
 * 现代医学知识服务
 * 处理现代医学知识的业务逻辑
 */
import { KnowledgeService } from './knowledge.service';
import { ModernMedicineKnowledgeModel, ModernMedicineKnowledge, ModernMedicineKnowledgeDocument } from '../models/modern-medicine-knowledge.model';
import { VectorDBService } from './vector-db.service';
import { logger } from '../utils/logger';
import mongoose from 'mongoose';

export class ModernMedicineKnowledgeService extends KnowledgeService {
  constructor() {
    super(ModernMedicineKnowledgeModel);
  }

  /**
   * 创建现代医学知识
   * @param knowledgeData 知识数据
   * @returns 创建的知识对象
   */
  async createModernMedicineKnowledge(knowledgeData: ModernMedicineKnowledge): Promise<ModernMedicineKnowledgeDocument> {
    try {
      // 创建知识条目
      const knowledge = await this.createKnowledgeEntry(knowledgeData);
      
      // 向量化知识内容（异步进行）
      this.vectorizeKnowledge(knowledge).catch(err => {
        logger.error(`向量化现代医学知识失败: ${err.message}`, { id: knowledge._id });
      });
      
      return knowledge;
    } catch (error) {
      logger.error('创建现代医学知识失败', error);
      throw error;
    }
  }

  /**
   * 更新现代医学知识
   * @param id 知识ID
   * @param knowledgeData 知识数据
   * @returns 更新后的知识对象
   */
  async updateModernMedicineKnowledge(id: string, knowledgeData: Partial<ModernMedicineKnowledge>): Promise<ModernMedicineKnowledgeDocument | null> {
    try {
      // 更新知识条目
      const knowledge = await this.updateKnowledgeEntry(id, knowledgeData);
      
      if (knowledge) {
        // 如果内容变更，重新向量化知识内容（异步进行）
        if (knowledgeData.content || knowledgeData.title || knowledgeData.summary) {
          knowledge.vectorized = false;
          await knowledge.save();
          
          this.vectorizeKnowledge(knowledge).catch(err => {
            logger.error(`重新向量化现代医学知识失败: ${err.message}`, { id: knowledge._id });
          });
        }
      }
      
      return knowledge;
    } catch (error) {
      logger.error(`更新现代医学知识失败, ID: ${id}`, error);
      throw error;
    }
  }

  /**
   * 获取现代医学知识详情
   * @param id 知识ID
   * @returns 知识对象
   */
  async getModernMedicineKnowledgeById(id: string): Promise<ModernMedicineKnowledgeDocument | null> {
    try {
      return await ModernMedicineKnowledgeModel.findById(id)
        .populate('categories')
        .populate('tags')
        .exec();
    } catch (error) {
      logger.error(`获取现代医学知识详情失败, ID: ${id}`, error);
      throw error;
    }
  }

  /**
   * 获取现代医学知识列表
   * @param page 页码
   * @param limit 每页数量
   * @param filter 过滤条件
   * @param sort 排序条件
   * @returns 知识列表及分页信息
   */
  async listModernMedicineKnowledge(
    page: number = 1,
    limit: number = 20,
    filter: any = {},
    sort: any = { createdAt: -1 }
  ) {
    try {
      const skip = (page - 1) * limit;
      const countPromise = ModernMedicineKnowledgeModel.countDocuments(filter);
      const knowledgePromise = ModernMedicineKnowledgeModel.find(filter)
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
      logger.error('获取现代医学知识列表失败', error);
      throw error;
    }
  }

  /**
   * 删除现代医学知识
   * @param id 知识ID
   * @returns 删除结果
   */
  async deleteModernMedicineKnowledge(id: string): Promise<boolean> {
    try {
      const knowledge = await ModernMedicineKnowledgeModel.findByIdAndDelete(id);
      
      if (knowledge) {
        // 删除向量数据库中的向量
        try {
          const vectorDBService = new VectorDBService();
          await vectorDBService.deleteVector(id);
        } catch (vectorError) {
          logger.error(`删除现代医学知识向量失败, ID: ${id}`, vectorError);
          // 向量删除失败不影响主流程
        }
        
        return true;
      }
      
      return false;
    } catch (error) {
      logger.error(`删除现代医学知识失败, ID: ${id}`, error);
      throw error;
    }
  }

  /**
   * 根据医学体系获取知识
   * @param medicalSystem 医学体系
   * @param page 页码
   * @param limit 每页数量
   * @returns 知识列表及分页信息
   */
  async getKnowledgeByMedicalSystem(
    medicalSystem: string,
    page: number = 1,
    limit: number = 20
  ) {
    try {
      return await this.listModernMedicineKnowledge(
        page,
        limit,
        { medicalSystem },
        { createdAt: -1 }
      );
    } catch (error) {
      logger.error(`根据医学体系获取知识失败, 体系: ${medicalSystem}`, error);
      throw error;
    }
  }

  /**
   * 根据研究支持程度获取知识
   * @param level 研究支持程度
   * @param page 页码
   * @param limit 每页数量
   * @returns 知识列表及分页信息
   */
  async getKnowledgeByResearchSupport(
    level: string,
    page: number = 1,
    limit: number = 20
  ) {
    try {
      return await this.listModernMedicineKnowledge(
        page,
        limit,
        { researchSupport: level },
        { createdAt: -1 }
      );
    } catch (error) {
      logger.error(`根据研究支持程度获取知识失败, 程度: ${level}`, error);
      throw error;
    }
  }

  /**
   * 向量化知识
   * @param knowledge 知识对象
   */
  private async vectorizeKnowledge(knowledge: ModernMedicineKnowledgeDocument): Promise<void> {
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
        ...knowledge.references || []
      ].filter(Boolean).join('\n');
      
      // 向量化
      const vectorDBService = new VectorDBService();
      await vectorDBService.storeVector(knowledge._id.toString(), text, {
        type: 'modern-medicine',
        medicalSystem: knowledge.medicalSystem,
        researchSupport: knowledge.researchSupport,
        title: knowledge.title
      });
      
      // 更新向量化状态
      knowledge.vectorized = true;
      await knowledge.save();
      
      logger.info(`现代医学知识向量化成功, ID: ${knowledge._id}`);
    } catch (error) {
      logger.error(`现代医学知识向量化失败, ID: ${knowledge._id}`, error);
      throw error;
    }
  }
}