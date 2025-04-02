/**
 * 环境健康服务
 * 管理与环境健康相关的知识数据
 */
import mongoose from 'mongoose';
import { EnvironmentalHealthData } from '../interfaces/environmental-health.interface';
import EnvironmentalHealthModel from '../models/environmental-health.model';
import logger from '../utils/logger';
import { KnowledgeGraphIntegrationService } from '../integrations/knowledge-graph-integration.service';
import { RagIntegrationService } from '../integrations/rag-integration.service';

export class EnvironmentalHealthService {
  private knowledgeGraphService: KnowledgeGraphIntegrationService;
  private ragService: RagIntegrationService;

  constructor() {
    this.knowledgeGraphService = new KnowledgeGraphIntegrationService();
    this.ragService = new RagIntegrationService();
  }

  /**
   * 创建环境健康知识条目
   * @param data 环境健康数据
   * @returns 创建的环境健康知识对象
   */
  async createEnvironmentalHealth(data: EnvironmentalHealthData): Promise<EnvironmentalHealthData> {
    try {
      logger.info('创建环境健康知识条目', { title: data.title });
      
      // 创建新的环境健康知识条目
      const environmentalHealth = new EnvironmentalHealthModel({
        ...data,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      
      // 保存到数据库
      const savedData = await environmentalHealth.save();
      
      // 同步到知识图谱
      await this.knowledgeGraphService.syncEnvironmentalHealth(savedData);
      
      // 同步到RAG服务
      await this.ragService.syncEnvironmentalHealth(savedData);
      
      return savedData.toObject();
    } catch (error) {
      logger.error('创建环境健康知识条目失败', { error: (error as Error).message, data });
      throw error;
    }
  }

  /**
   * 更新环境健康知识条目
   * @param id 环境健康知识ID
   * @param data 环境健康数据
   * @returns 更新后的环境健康知识
   */
  async updateEnvironmentalHealth(id: string, data: Partial<EnvironmentalHealthData>): Promise<EnvironmentalHealthData | null> {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new Error('无效的环境健康知识ID');
      }
      
      logger.info('更新环境健康知识条目', { id });
      
      // 更新数据库中的记录
      const updatedData = await EnvironmentalHealthModel.findByIdAndUpdate(
        id,
        {
          ...data,
          updatedAt: new Date()
        },
        { new: true, runValidators: true }
      );
      
      if (!updatedData) {
        logger.warn('未找到要更新的环境健康知识条目', { id });
        return null;
      }
      
      // 同步更新到知识图谱
      await this.knowledgeGraphService.syncEnvironmentalHealth(updatedData);
      
      // 同步更新到RAG服务
      await this.ragService.syncEnvironmentalHealth(updatedData);
      
      return updatedData.toObject();
    } catch (error) {
      logger.error('更新环境健康知识条目失败', { error: (error as Error).message, id });
      throw error;
    }
  }

  /**
   * 获取环境健康知识条目
   * @param id 环境健康知识ID
   * @returns 环境健康知识条目
   */
  async getEnvironmentalHealth(id: string): Promise<EnvironmentalHealthData | null> {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new Error('无效的环境健康知识ID');
      }
      
      logger.info('获取环境健康知识条目', { id });
      
      const environmentalHealth = await EnvironmentalHealthModel.findById(id)
        .populate('relatedKnowledge')
        .populate('tags')
        .populate('categories');
      
      if (!environmentalHealth) {
        logger.warn('未找到环境健康知识条目', { id });
        return null;
      }
      
      return environmentalHealth.toObject();
    } catch (error) {
      logger.error('获取环境健康知识条目失败', { error: (error as Error).message, id });
      throw error;
    }
  }

  /**
   * 获取环境健康知识列表
   * @param filter 过滤条件
   * @param page 页码
   * @param limit 每页记录数
   * @returns 环境健康知识列表和分页信息
   */
  async getEnvironmentalHealthList(filter: any = {}, page: number = 1, limit: number = 20): Promise<{
    data: EnvironmentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('获取环境健康知识列表', { filter, page, limit });
      
      // 确保页码和限制是有效的数字
      const validPage = Math.max(1, page);
      const validLimit = Math.max(1, Math.min(100, limit)); // 限制最大为100
      
      // 计算跳过的文档数量
      const skip = (validPage - 1) * validLimit;
      
      // 查询数据库
      const [data, total] = await Promise.all([
        EnvironmentalHealthModel.find(filter)
          .populate('relatedKnowledge')
          .populate('tags')
          .populate('categories')
          .sort({ updatedAt: -1 })
          .skip(skip)
          .limit(validLimit),
        EnvironmentalHealthModel.countDocuments(filter)
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
      logger.error('获取环境健康知识列表失败', { error: (error as Error).message, filter });
      throw error;
    }
  }

  /**
   * 删除环境健康知识条目
   * @param id 环境健康知识ID
   * @returns 是否删除成功
   */
  async deleteEnvironmentalHealth(id: string): Promise<boolean> {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new Error('无效的环境健康知识ID');
      }
      
      logger.info('删除环境健康知识条目', { id });
      
      // 查找并删除记录
      const result = await EnvironmentalHealthModel.findByIdAndDelete(id);
      
      if (!result) {
        logger.warn('未找到要删除的环境健康知识条目', { id });
        return false;
      }
      
      // 从知识图谱中删除
      await this.knowledgeGraphService.deleteEnvironmentalHealth(id);
      
      // 从RAG服务中删除
      await this.ragService.deleteEnvironmentalHealth(id);
      
      return true;
    } catch (error) {
      logger.error('删除环境健康知识条目失败', { error: (error as Error).message, id });
      throw error;
    }
  }

  /**
   * 按环境类型获取知识
   * @param environmentType 环境类型
   * @param page 页码
   * @param limit 每页记录数
   * @returns 环境健康知识列表和分页信息
   */
  async getEnvironmentalHealthByType(environmentType: string, page: number = 1, limit: number = 20): Promise<{
    data: EnvironmentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('按环境类型获取知识', { environmentType, page, limit });
      
      return this.getEnvironmentalHealthList({ environmentType }, page, limit);
    } catch (error) {
      logger.error('按环境类型获取知识失败', { error: (error as Error).message, environmentType });
      throw error;
    }
  }

  /**
   * 按污染物类型获取环境健康知识
   * @param pollutantType 污染物类型
   * @param page 页码
   * @param limit 每页记录数
   * @returns 环境健康知识列表和分页信息
   */
  async getEnvironmentalHealthByPollutant(pollutantType: string, page: number = 1, limit: number = 20): Promise<{
    data: EnvironmentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('按污染物类型获取环境健康知识', { pollutantType, page, limit });
      
      return this.getEnvironmentalHealthList({ pollutantType }, page, limit);
    } catch (error) {
      logger.error('按污染物类型获取环境健康知识失败', { error: (error as Error).message, pollutantType });
      throw error;
    }
  }

  /**
   * 按健康影响获取环境健康知识
   * @param healthImpact 健康影响
   * @param page 页码
   * @param limit 每页记录数
   * @returns 环境健康知识列表和分页信息
   */
  async getEnvironmentalHealthByHealthImpact(healthImpact: string, page: number = 1, limit: number = 20): Promise<{
    data: EnvironmentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('按健康影响获取环境健康知识', { healthImpact, page, limit });
      
      return this.getEnvironmentalHealthList({ healthImpacts: healthImpact }, page, limit);
    } catch (error) {
      logger.error('按健康影响获取环境健康知识失败', { error: (error as Error).message, healthImpact });
      throw error;
    }
  }

  /**
   * 按地区获取环境健康知识
   * @param region 地区
   * @param page 页码
   * @param limit 每页记录数
   * @returns 环境健康知识列表和分页信息
   */
  async getEnvironmentalHealthByRegion(region: string, page: number = 1, limit: number = 20): Promise<{
    data: EnvironmentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('按地区获取环境健康知识', { region, page, limit });
      
      return this.getEnvironmentalHealthList({ regionSpecific: region }, page, limit);
    } catch (error) {
      logger.error('按地区获取环境健康知识失败', { error: (error as Error).message, region });
      throw error;
    }
  }

  /**
   * 按风险级别获取环境健康知识
   * @param riskLevel 风险级别
   * @param page 页码
   * @param limit 每页记录数
   * @returns 环境健康知识列表和分页信息
   */
  async getEnvironmentalHealthByRiskLevel(riskLevel: number, page: number = 1, limit: number = 20): Promise<{
    data: EnvironmentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('按风险级别获取环境健康知识', { riskLevel, page, limit });
      
      return this.getEnvironmentalHealthList({ riskLevel }, page, limit);
    } catch (error) {
      logger.error('按风险级别获取环境健康知识失败', { error: (error as Error).message, riskLevel });
      throw error;
    }
  }

  /**
   * 按关键词搜索环境健康知识
   * @param keyword 关键词
   * @param page 页码
   * @param limit 每页记录数
   * @returns 环境健康知识列表和分页信息
   */
  async searchEnvironmentalHealth(keyword: string, page: number = 1, limit: number = 20): Promise<{
    data: EnvironmentalHealthData[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('搜索环境健康知识', { keyword, page, limit });
      
      const searchRegex = new RegExp(keyword, 'i');
      
      const filter = {
        $or: [
          { title: searchRegex },
          { description: searchRegex },
          { content: searchRegex },
          { keywords: searchRegex },
          { healthImpacts: searchRegex },
          { pollutantType: searchRegex }
        ]
      };
      
      return this.getEnvironmentalHealthList(filter, page, limit);
    } catch (error) {
      logger.error('搜索环境健康知识失败', { error: (error as Error).message, keyword });
      throw error;
    }
  }
}

export default new EnvironmentalHealthService();