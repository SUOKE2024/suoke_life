/**
 * 心理健康服务
 * 管理与心理健康相关的知识数据
 */
import mongoose from 'mongoose';
import { MentalHealthData } from '../interfaces/mental-health.interface';
import PsychologicalHealthModel from '../models/psychological-health.model';
import logger from '../utils/logger';
import { KnowledgeGraphIntegrationService } from '../integrations/knowledge-graph-integration.service';
import { RagIntegrationService } from '../integrations/rag-integration.service';

export class MentalHealthService {
  private knowledgeGraphService: KnowledgeGraphIntegrationService;
  private ragService: RagIntegrationService;

  constructor() {
    this.knowledgeGraphService = new KnowledgeGraphIntegrationService();
    this.ragService = new RagIntegrationService();
  }

  /**
   * 创建心理健康知识条目
   * @param data 心理健康数据
   * @returns 创建的心理健康知识对象
   */
  async createMentalHealth(data: MentalHealthData): Promise<MentalHealthData> {
    try {
      logger.info('创建心理健康知识条目', { title: data.title });
      
      // 创建新的心理健康知识条目
      const mentalHealth = new PsychologicalHealthModel({
        ...data,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      
      // 保存到数据库
      const savedData = await mentalHealth.save();
      
      // 同步到知识图谱
      await this.knowledgeGraphService.syncMentalHealth(savedData);
      
      // 同步到RAG服务
      await this.ragService.syncMentalHealth(savedData);
      
      return savedData.toObject();
    } catch (error) {
      logger.error('创建心理健康知识条目失败', { error: (error as Error).message, data });
      throw error;
    }
  }

  /**
   * 更新心理健康知识条目
   * @param id 心理健康知识ID
   * @param data 心理健康数据
   * @returns 更新后的心理健康知识
   */
  async updateMentalHealth(id: string, data: Partial<MentalHealthData>): Promise<MentalHealthData | null> {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new Error('无效的心理健康知识ID');
      }
      
      logger.info('更新心理健康知识条目', { id });
      
      // 更新数据库中的记录
      const updatedData = await PsychologicalHealthModel.findByIdAndUpdate(
        id,
        {
          ...data,
          updatedAt: new Date()
        },
        { new: true, runValidators: true }
      );
      
      if (!updatedData) {
        logger.warn('未找到要更新的心理健康知识条目', { id });
        return null;
      }
      
      // 同步更新到知识图谱
      await this.knowledgeGraphService.syncMentalHealth(updatedData);
      
      // 同步更新到RAG服务
      await this.ragService.syncMentalHealth(updatedData);
      
      return updatedData.toObject();
    } catch (error) {
      logger.error('更新心理健康知识条目失败', { error: (error as Error).message, id });
      throw error;
    }
  }

  /**
   * 获取心理健康知识条目
   * @param id 心理健康知识ID
   * @returns 心理健康知识条目
   */
  async getMentalHealth(id: string): Promise<MentalHealthData | null> {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new Error('无效的心理健康知识ID');
      }
      
      logger.info('获取心理健康知识条目', { id });
      
      const mentalHealth = await PsychologicalHealthModel.findById(id)
        .populate('relatedKnowledge')
        .populate('tags')
        .populate('categories');
      
      if (!mentalHealth) {
        logger.warn('未找到心理健康知识条目', { id });
        return null;
      }
      
      return mentalHealth.toObject();
    } catch (error) {
      logger.error('获取心理健康知识条目失败', { error: (error as Error).message, id });
      throw error;
    }
  }

  /**
   * 获取心理健康知识列表
   * @param filter 过滤条件
   * @param page 页码
   * @param limit 每页记录数
   * @returns 心理健康知识列表和分页信息
   */
  async getMentalHealthList(filter: any = {}, page: number = 1, limit: number = 20): Promise<{
    data: MentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('获取心理健康知识列表', { filter, page, limit });
      
      // 确保页码和限制是有效的数字
      const validPage = Math.max(1, page);
      const validLimit = Math.max(1, Math.min(100, limit)); // 限制最大为100
      
      // 计算跳过的文档数量
      const skip = (validPage - 1) * validLimit;
      
      // 查询数据库
      const [data, total] = await Promise.all([
        PsychologicalHealthModel.find(filter)
          .populate('relatedKnowledge')
          .populate('tags')
          .populate('categories')
          .sort({ updatedAt: -1 })
          .skip(skip)
          .limit(validLimit),
        PsychologicalHealthModel.countDocuments(filter)
      ]);
      
      // 计算总页数
      const totalPages = Math.ceil(total / validLimit);
      
      return {
        data: data.map(item => item.toObject()),
        total,
        page: validPage,
        limit: validLimit,
        totalPages
      };
    } catch (error) {
      logger.error('获取心理健康知识列表失败', { error: (error as Error).message, filter });
      throw error;
    }
  }

  /**
   * 删除心理健康知识条目
   * @param id 心理健康知识ID
   * @returns 是否删除成功
   */
  async deleteMentalHealth(id: string): Promise<boolean> {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new Error('无效的心理健康知识ID');
      }
      
      logger.info('删除心理健康知识条目', { id });
      
      // 查找并删除记录
      const result = await PsychologicalHealthModel.findByIdAndDelete(id);
      
      if (!result) {
        logger.warn('未找到要删除的心理健康知识条目', { id });
        return false;
      }
      
      // 从知识图谱中删除
      await this.knowledgeGraphService.deleteMentalHealth(id);
      
      // 从RAG服务中删除
      await this.ragService.deleteMentalHealth(id);
      
      return true;
    } catch (error) {
      logger.error('删除心理健康知识条目失败', { error: (error as Error).message, id });
      throw error;
    }
  }

  /**
   * 按心理问题类型获取知识
   * @param issueType 心理问题类型
   * @param page 页码
   * @param limit 每页记录数
   * @returns 心理健康知识列表和分页信息
   */
  async getMentalHealthByIssueType(issueType: string, page: number = 1, limit: number = 20): Promise<{
    data: MentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('按心理问题类型获取知识', { issueType, page, limit });
      
      return this.getMentalHealthList({ issueType }, page, limit);
    } catch (error) {
      logger.error('按心理问题类型获取知识失败', { error: (error as Error).message, issueType });
      throw error;
    }
  }

  /**
   * 按年龄组获取心理健康知识
   * @param ageGroup 年龄组
   * @param page 页码
   * @param limit 每页记录数
   * @returns 心理健康知识列表和分页信息
   */
  async getMentalHealthByAgeGroup(ageGroup: string, page: number = 1, limit: number = 20): Promise<{
    data: MentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('按年龄组获取心理健康知识', { ageGroup, page, limit });
      
      return this.getMentalHealthList({ targetAgeGroups: ageGroup }, page, limit);
    } catch (error) {
      logger.error('按年龄组获取心理健康知识失败', { error: (error as Error).message, ageGroup });
      throw error;
    }
  }

  /**
   * 按干预方法获取心理健康知识
   * @param interventionMethod 干预方法
   * @param page 页码
   * @param limit 每页记录数
   * @returns 心理健康知识列表和分页信息
   */
  async getMentalHealthByInterventionMethod(interventionMethod: string, page: number = 1, limit: number = 20): Promise<{
    data: MentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('按干预方法获取心理健康知识', { interventionMethod, page, limit });
      
      return this.getMentalHealthList({ interventionMethods: interventionMethod }, page, limit);
    } catch (error) {
      logger.error('按干预方法获取心理健康知识失败', { error: (error as Error).message, interventionMethod });
      throw error;
    }
  }

  /**
   * 按关键词搜索心理健康知识
   * @param keyword 关键词
   * @param page 页码
   * @param limit 每页记录数
   * @returns 心理健康知识列表和分页信息
   */
  async searchMentalHealth(keyword: string, page: number = 1, limit: number = 20): Promise<{
    data: MentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('搜索心理健康知识', { keyword, page, limit });
      
      const searchRegex = new RegExp(keyword, 'i');
      
      const filter = {
        $or: [
          { title: searchRegex },
          { description: searchRegex },
          { content: searchRegex },
          { keywords: searchRegex },
          { symptoms: searchRegex },
          { treatmentMethods: searchRegex }
        ]
      };
      
      return this.getMentalHealthList(filter, page, limit);
    } catch (error) {
      logger.error('搜索心理健康知识失败', { error: (error as Error).message, keyword });
      throw error;
    }
  }
}

export default new MentalHealthService();