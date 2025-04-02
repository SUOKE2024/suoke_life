/**
 * 多模态健康数据服务
 * 处理图像、声音、可穿戴设备等多模态健康数据相关知识
 */

import { injectable, inject } from 'inversify';
import mongoose, { Model } from 'mongoose';
import { Logger } from '../utils/logger';
import { TYPES } from '../types';
import { 
  IMultimodalHealthKnowledge, 
  IHealthPattern,
  MultimodalQueryOptions,
  HealthPatternQueryOptions,
  PaginatedResult
} from '../interfaces';
import { HealthDataIntegrationService } from '../integrations/health-data-integration.service';
import { KnowledgeService } from './knowledge.service';

@injectable()
export class MultimodalHealthService {
  private logger = new Logger('MultimodalHealthService');
  private multimodalHealthModel: Model<IMultimodalHealthKnowledge>;
  private healthPatternModel: Model<IHealthPattern>;

  constructor(
    @inject(TYPES.KnowledgeService) private knowledgeService: KnowledgeService,
    @inject(TYPES.HealthDataIntegrationService) private healthDataIntegrationService: HealthDataIntegrationService,
    @inject(TYPES.Database) private database: mongoose.Connection
  ) {
    this.multimodalHealthModel = this.database.model<IMultimodalHealthKnowledge>('MultimodalHealthKnowledge');
    this.healthPatternModel = this.database.model<IHealthPattern>('HealthPattern');
  }

  /**
   * 创建多模态健康知识
   * @param data 多模态健康知识数据
   */
  async createMultimodalHealthKnowledge(data: Partial<IMultimodalHealthKnowledge>): Promise<IMultimodalHealthKnowledge> {
    try {
      this.logger.info('Creating new multimodal health knowledge');
      
      // 使用知识服务创建基础知识记录
      const baseKnowledge = await this.knowledgeService.createKnowledge({
        title: data.title!,
        content: data.content!,
        summary: data.summary,
        categories: [...(data.categories || []), `multimodal-health/${data.modalityType || 'combined'}`],
        tags: data.tags,
        source: data.source,
        metadata: data.metadata
      });
      
      // 创建多模态健康知识
      const multimodalKnowledge = new this.multimodalHealthModel({
        ...baseKnowledge.toObject(),
        modalityType: data.modalityType,
        analysisMethod: data.analysisMethod,
        dataRequirements: data.dataRequirements,
        privacyConsiderations: data.privacyConsiderations,
        imageFeatures: data.imageFeatures,
        audioFeatures: data.audioFeatures,
        wearableMetrics: data.wearableMetrics,
        environmentalFactors: data.environmentalFactors,
        dataFusionTechniques: data.dataFusionTechniques,
        machineLearningSummary: data.machineLearningSummary,
        validationResults: data.validationResults,
        limitationsAndCaveats: data.limitationsAndCaveats
      });
      
      await multimodalKnowledge.save();
      return multimodalKnowledge;
    } catch (error) {
      this.logger.error('Failed to create multimodal health knowledge', error);
      throw new Error('Failed to create multimodal health knowledge');
    }
  }

  /**
   * 更新多模态健康知识
   * @param id 知识ID
   * @param data 更新数据
   */
  async updateMultimodalHealthKnowledge(id: string, data: Partial<IMultimodalHealthKnowledge>): Promise<IMultimodalHealthKnowledge | null> {
    try {
      this.logger.info(`Updating multimodal health knowledge: ${id}`);
      
      // 如果有基础知识字段需要更新，先更新基础知识
      if (data.title || data.content || data.summary || data.categories || data.tags || data.source || data.metadata) {
        await this.knowledgeService.updateKnowledge(id, {
          title: data.title,
          content: data.content,
          summary: data.summary,
          categories: data.categories,
          tags: data.tags,
          source: data.source,
          metadata: data.metadata
        });
      }
      
      // 更新多模态健康知识特有字段
      const updateData: any = {};
      
      if (data.modalityType) updateData.modalityType = data.modalityType;
      if (data.analysisMethod) updateData.analysisMethod = data.analysisMethod;
      if (data.dataRequirements) updateData.dataRequirements = data.dataRequirements;
      if (data.privacyConsiderations) updateData.privacyConsiderations = data.privacyConsiderations;
      if (data.imageFeatures) updateData.imageFeatures = data.imageFeatures;
      if (data.audioFeatures) updateData.audioFeatures = data.audioFeatures;
      if (data.wearableMetrics) updateData.wearableMetrics = data.wearableMetrics;
      if (data.environmentalFactors) updateData.environmentalFactors = data.environmentalFactors;
      if (data.dataFusionTechniques) updateData.dataFusionTechniques = data.dataFusionTechniques;
      if (data.machineLearningSummary) updateData.machineLearningSummary = data.machineLearningSummary;
      if (data.validationResults) updateData.validationResults = data.validationResults;
      if (data.limitationsAndCaveats) updateData.limitationsAndCaveats = data.limitationsAndCaveats;
      
      // 执行更新
      const updated = await this.multimodalHealthModel.findByIdAndUpdate(
        id,
        { $set: updateData },
        { new: true }
      );
      
      return updated;
    } catch (error) {
      this.logger.error(`Failed to update multimodal health knowledge: ${id}`, error);
      throw new Error('Failed to update multimodal health knowledge');
    }
  }

  /**
   * 获取多模态健康知识详情
   * @param id 知识ID
   * @param modalData 可选的多模态数据，用于内容增强
   */
  async getMultimodalHealthKnowledge(id: string, modalData?: any): Promise<IMultimodalHealthKnowledge | null> {
    try {
      this.logger.info(`Getting multimodal health knowledge: ${id}`);
      
      let knowledge = await this.multimodalHealthModel.findById(id);
      
      if (!knowledge) {
        return null;
      }
      
      // 如果提供了多模态数据，进行内容增强
      if (modalData && knowledge) {
        knowledge = await this.healthDataIntegrationService.enrichWithMultimodalData(knowledge, modalData);
      }
      
      return knowledge;
    } catch (error) {
      this.logger.error(`Failed to get multimodal health knowledge: ${id}`, error);
      throw new Error('Failed to get multimodal health knowledge');
    }
  }

  /**
   * 查询多模态健康知识列表
   * @param options 查询选项
   */
  async queryMultimodalHealthKnowledge(options: MultimodalQueryOptions): Promise<PaginatedResult<IMultimodalHealthKnowledge>> {
    try {
      this.logger.info('Querying multimodal health knowledge');
      
      const page = options.page || 1;
      const limit = options.limit || 20;
      const skip = (page - 1) * limit;
      
      // 构建查询条件
      const query: any = {};
      
      // 添加多模态健康知识特有的过滤条件
      if (options.modalityType) {
        query.modalityType = options.modalityType;
      }
      
      if (options.feature) {
        // 搜索不同类型的特征
        query.$or = [
          { 'imageFeatures.feature': { $regex: options.feature, $options: 'i' } },
          { 'audioFeatures.feature': { $regex: options.feature, $options: 'i' } },
          { 'wearableMetrics.metric': { $regex: options.feature, $options: 'i' } }
        ];
      }
      
      if (options.condition) {
        query['wearableMetrics.correlatedConditions'] = { $regex: options.condition, $options: 'i' };
      }
      
      if (options.environmentalFactor) {
        query['environmentalFactors.factor'] = { $regex: options.environmentalFactor, $options: 'i' };
      }
      
      if (options.pattern) {
        // 在全文内容中搜索模式
        query.$text = { $search: options.pattern };
      }
      
      // 执行查询
      const [items, total] = await Promise.all([
        this.multimodalHealthModel.find(query).skip(skip).limit(limit),
        this.multimodalHealthModel.countDocuments(query)
      ]);
      
      return {
        items,
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      };
    } catch (error) {
      this.logger.error('Failed to query multimodal health knowledge', error);
      throw new Error('Failed to query multimodal health knowledge');
    }
  }

  /**
   * 创建健康数据模式
   * @param data 健康数据模式数据
   */
  async createHealthPattern(data: Partial<IHealthPattern>): Promise<IHealthPattern> {
    try {
      this.logger.info('Creating new health pattern');
      
      const healthPattern = new this.healthPatternModel({
        name: data.name,
        description: data.description,
        modalityType: data.modalityType,
        patternFeatures: data.patternFeatures,
        normalVariations: data.normalVariations,
        abnormalVariations: data.abnormalVariations,
        detectionAlgorithm: data.detectionAlgorithm,
        relatedPatterns: data.relatedPatterns,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      
      await healthPattern.save();
      return healthPattern;
    } catch (error) {
      this.logger.error('Failed to create health pattern', error);
      throw new Error('Failed to create health pattern');
    }
  }

  /**
   * 获取健康数据模式
   * @param id 模式ID
   */
  async getHealthPattern(id: string): Promise<IHealthPattern | null> {
    try {
      this.logger.info(`Getting health pattern: ${id}`);
      return this.healthPatternModel.findById(id);
    } catch (error) {
      this.logger.error(`Failed to get health pattern: ${id}`, error);
      throw new Error('Failed to get health pattern');
    }
  }

  /**
   * 查询健康数据模式列表
   * @param options 查询选项
   */
  async queryHealthPatterns(options: HealthPatternQueryOptions): Promise<PaginatedResult<IHealthPattern>> {
    try {
      this.logger.info('Querying health patterns');
      
      const page = options.page || 1;
      const limit = options.limit || 20;
      const skip = (page - 1) * limit;
      
      // 构建查询条件
      const query: any = {};
      
      if (options.modalityType) {
        query.modalityType = options.modalityType;
      }
      
      if (options.abnormalVariation) {
        query['abnormalVariations.variation'] = { $regex: options.abnormalVariation, $options: 'i' };
      }
      
      if (options.severity) {
        query['abnormalVariations.severity'] = options.severity;
      }
      
      if (options.searchTerm) {
        query.$or = [
          { name: { $regex: options.searchTerm, $options: 'i' } },
          { description: { $regex: options.searchTerm, $options: 'i' } },
          { patternFeatures: { $elemMatch: { $regex: options.searchTerm, $options: 'i' } } }
        ];
      }
      
      // 执行查询
      const [items, total] = await Promise.all([
        this.healthPatternModel.find(query).skip(skip).limit(limit),
        this.healthPatternModel.countDocuments(query)
      ]);
      
      return {
        items,
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      };
    } catch (error) {
      this.logger.error('Failed to query health patterns', error);
      throw new Error('Failed to query health patterns');
    }
  }

  /**
   * 删除多模态健康知识
   * @param id 知识ID
   */
  async deleteMultimodalHealthKnowledge(id: string): Promise<boolean> {
    try {
      this.logger.info(`Deleting multimodal health knowledge: ${id}`);
      
      // 删除多模态健康知识
      const result = await this.multimodalHealthModel.findByIdAndDelete(id);
      
      if (result) {
        // 同时删除基础知识
        await this.knowledgeService.deleteKnowledge(id);
        return true;
      }
      
      return false;
    } catch (error) {
      this.logger.error(`Failed to delete multimodal health knowledge: ${id}`, error);
      throw new Error('Failed to delete multimodal health knowledge');
    }
  }

  /**
   * 根据模态类型获取所有相关知识
   * @param modalityType 模态类型
   */
  async getKnowledgeByModalityType(modalityType: string): Promise<IMultimodalHealthKnowledge[]> {
    try {
      this.logger.info(`Getting knowledge for modality type: ${modalityType}`);
      
      return this.multimodalHealthModel.find({
        modalityType
      });
    } catch (error) {
      this.logger.error(`Failed to get knowledge for modality type: ${modalityType}`, error);
      throw new Error('Failed to get knowledge by modality type');
    }
  }

  /**
   * 获取适用于特定条件的健康模式
   * @param condition 健康条件
   */
  async getPatternsByCondition(condition: string): Promise<IHealthPattern[]> {
    try {
      this.logger.info(`Getting patterns for condition: ${condition}`);
      
      // 查找与特定条件相关的异常变化
      return this.healthPatternModel.find({
        'abnormalVariations.possibleCauses': { $regex: condition, $options: 'i' }
      });
    } catch (error) {
      this.logger.error(`Failed to get patterns for condition: ${condition}`, error);
      throw new Error('Failed to get patterns by condition');
    }
  }
}