/**
 * 精准医学知识服务
 * 处理基因组学和个性化健康相关知识
 */

import { injectable, inject } from 'inversify';
import mongoose, { Model } from 'mongoose';
import { Logger } from '../utils/logger';
import { TYPES } from '../types';
import { 
  IPrecisionMedicineKnowledge, 
  IBiomarker,
  PrecisionMedicineQueryOptions,
  BiomarkerQueryOptions,
  PaginatedResult
} from '../interfaces';
import { HealthDataIntegrationService } from '../integrations/health-data-integration.service';
import { KnowledgeService } from './knowledge.service';

@injectable()
export class PrecisionMedicineService {
  private logger = new Logger('PrecisionMedicineService');
  private precisionMedicineModel: Model<IPrecisionMedicineKnowledge>;
  private biomarkerModel: Model<IBiomarker>;

  constructor(
    @inject(TYPES.KnowledgeService) private knowledgeService: KnowledgeService,
    @inject(TYPES.HealthDataIntegrationService) private healthDataIntegrationService: HealthDataIntegrationService,
    @inject(TYPES.Database) private database: mongoose.Connection
  ) {
    this.precisionMedicineModel = this.database.model<IPrecisionMedicineKnowledge>('PrecisionMedicineKnowledge');
    this.biomarkerModel = this.database.model<IBiomarker>('Biomarker');
  }

  /**
   * 创建新的精准医学知识
   * @param data 精准医学知识数据
   */
  async createPrecisionMedicineKnowledge(data: Partial<IPrecisionMedicineKnowledge>): Promise<IPrecisionMedicineKnowledge> {
    try {
      this.logger.info('Creating new precision medicine knowledge');
      
      // 使用知识服务创建基础知识记录
      const baseKnowledge = await this.knowledgeService.createKnowledge({
        title: data.title!,
        content: data.content!,
        summary: data.summary,
        categories: [...(data.categories || []), `precision-medicine/${data.studyType || 'genetic'}`],
        tags: data.tags,
        source: data.source,
        metadata: data.metadata
      });
      
      // 创建精准医学知识
      const precisionMedicineKnowledge = new this.precisionMedicineModel({
        ...baseKnowledge.toObject(),
        studyType: data.studyType,
        confidenceLevel: data.confidenceLevel,
        relevantGenes: data.relevantGenes,
        snpReferences: data.snpReferences,
        sampleSize: data.sampleSize,
        populationGroups: data.populationGroups,
        heritability: data.heritability,
        technicalPlatform: data.technicalPlatform,
        nutrientInteractions: data.nutrientInteractions,
        drugInteractions: data.drugInteractions,
        diseaseAssociations: data.diseaseAssociations,
        environmentalInteractions: data.environmentalInteractions,
        personalizationFactors: data.personalizationFactors,
        recommendationAlgorithm: data.recommendationAlgorithm,
        applicableBiomarkers: data.applicableBiomarkers
      });
      
      await precisionMedicineKnowledge.save();
      return precisionMedicineKnowledge;
    } catch (error) {
      this.logger.error('Failed to create precision medicine knowledge', error);
      throw new Error('Failed to create precision medicine knowledge');
    }
  }

  /**
   * 更新精准医学知识
   * @param id 知识ID
   * @param data 更新数据
   */
  async updatePrecisionMedicineKnowledge(id: string, data: Partial<IPrecisionMedicineKnowledge>): Promise<IPrecisionMedicineKnowledge | null> {
    try {
      this.logger.info(`Updating precision medicine knowledge: ${id}`);
      
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
      
      // 更新精准医学知识特有字段
      const updateData: any = {};
      
      if (data.studyType) updateData.studyType = data.studyType;
      if (data.confidenceLevel) updateData.confidenceLevel = data.confidenceLevel;
      if (data.relevantGenes) updateData.relevantGenes = data.relevantGenes;
      if (data.snpReferences) updateData.snpReferences = data.snpReferences;
      if (data.sampleSize) updateData.sampleSize = data.sampleSize;
      if (data.populationGroups) updateData.populationGroups = data.populationGroups;
      if (data.heritability) updateData.heritability = data.heritability;
      if (data.technicalPlatform) updateData.technicalPlatform = data.technicalPlatform;
      if (data.nutrientInteractions) updateData.nutrientInteractions = data.nutrientInteractions;
      if (data.drugInteractions) updateData.drugInteractions = data.drugInteractions;
      if (data.diseaseAssociations) updateData.diseaseAssociations = data.diseaseAssociations;
      if (data.environmentalInteractions) updateData.environmentalInteractions = data.environmentalInteractions;
      if (data.personalizationFactors) updateData.personalizationFactors = data.personalizationFactors;
      if (data.recommendationAlgorithm) updateData.recommendationAlgorithm = data.recommendationAlgorithm;
      if (data.applicableBiomarkers) updateData.applicableBiomarkers = data.applicableBiomarkers;
      
      // 执行更新
      const updated = await this.precisionMedicineModel.findByIdAndUpdate(
        id,
        { $set: updateData },
        { new: true }
      );
      
      return updated;
    } catch (error) {
      this.logger.error(`Failed to update precision medicine knowledge: ${id}`, error);
      throw new Error('Failed to update precision medicine knowledge');
    }
  }

  /**
   * 获取精准医学知识详情
   * @param id 知识ID
   * @param userId 可选用户ID，用于个性化内容
   */
  async getPrecisionMedicineKnowledge(id: string, userId?: string): Promise<IPrecisionMedicineKnowledge | null> {
    try {
      this.logger.info(`Getting precision medicine knowledge: ${id}`);
      
      let knowledge = await this.precisionMedicineModel.findById(id);
      
      if (!knowledge) {
        return null;
      }
      
      // 如果提供了用户ID，进行个性化处理
      if (userId && knowledge) {
        knowledge = await this.healthDataIntegrationService.enrichWithPersonalizedData(knowledge, userId);
      }
      
      return knowledge;
    } catch (error) {
      this.logger.error(`Failed to get precision medicine knowledge: ${id}`, error);
      throw new Error('Failed to get precision medicine knowledge');
    }
  }

  /**
   * 查询精准医学知识列表
   * @param options 查询选项
   */
  async queryPrecisionMedicineKnowledge(options: PrecisionMedicineQueryOptions): Promise<PaginatedResult<IPrecisionMedicineKnowledge>> {
    try {
      this.logger.info('Querying precision medicine knowledge');
      
      const page = options.page || 1;
      const limit = options.limit || 20;
      const skip = (page - 1) * limit;
      
      // 构建查询条件
      const query: any = {};
      
      // 添加精准医学知识特有的过滤条件
      if (options.studyType) {
        query.studyType = options.studyType;
      }
      
      if (options.confidenceLevel) {
        query.confidenceLevel = options.confidenceLevel;
      }
      
      if (options.genes && options.genes.length > 0) {
        query.relevantGenes = { $in: options.genes };
      }
      
      if (options.disease) {
        query['diseaseAssociations.disease'] = { $regex: options.disease, $options: 'i' };
      }
      
      if (options.nutrient) {
        query['nutrientInteractions.nutrient'] = { $regex: options.nutrient, $options: 'i' };
      }
      
      if (options.drug) {
        query['drugInteractions.drug'] = { $regex: options.drug, $options: 'i' };
      }
      
      if (options.environmentalFactor) {
        query['environmentalInteractions.factor'] = { $regex: options.environmentalFactor, $options: 'i' };
      }
      
      if (options.populationGroup) {
        query.populationGroups = { $regex: options.populationGroup, $options: 'i' };
      }
      
      // 执行查询
      const [items, total] = await Promise.all([
        this.precisionMedicineModel.find(query).skip(skip).limit(limit),
        this.precisionMedicineModel.countDocuments(query)
      ]);
      
      return {
        items,
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      };
    } catch (error) {
      this.logger.error('Failed to query precision medicine knowledge', error);
      throw new Error('Failed to query precision medicine knowledge');
    }
  }

  /**
   * 创建生物标记物
   * @param data 生物标记物数据
   */
  async createBiomarker(data: Partial<IBiomarker>): Promise<IBiomarker> {
    try {
      this.logger.info('Creating new biomarker');
      
      const biomarker = new this.biomarkerModel({
        name: data.name,
        category: data.category,
        description: data.description,
        unit: data.unit,
        normalRange: data.normalRange,
        interpretationGuidelines: data.interpretationGuidelines,
        relatedConditions: data.relatedConditions,
        monitoringFrequency: data.monitoringFrequency,
        sampleRequirements: data.sampleRequirements,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      
      await biomarker.save();
      return biomarker;
    } catch (error) {
      this.logger.error('Failed to create biomarker', error);
      throw new Error('Failed to create biomarker');
    }
  }

  /**
   * 获取生物标记物
   * @param id 生物标记物ID
   */
  async getBiomarker(id: string): Promise<IBiomarker | null> {
    try {
      this.logger.info(`Getting biomarker: ${id}`);
      return this.biomarkerModel.findById(id);
    } catch (error) {
      this.logger.error(`Failed to get biomarker: ${id}`, error);
      throw new Error('Failed to get biomarker');
    }
  }

  /**
   * 查询生物标记物列表
   * @param options 查询选项
   */
  async queryBiomarkers(options: BiomarkerQueryOptions): Promise<PaginatedResult<IBiomarker>> {
    try {
      this.logger.info('Querying biomarkers');
      
      const page = options.page || 1;
      const limit = options.limit || 20;
      const skip = (page - 1) * limit;
      
      // 构建查询条件
      const query: any = {};
      
      if (options.category) {
        query.category = options.category;
      }
      
      if (options.condition) {
        query.relatedConditions = { $regex: options.condition, $options: 'i' };
      }
      
      if (options.searchTerm) {
        query.$or = [
          { name: { $regex: options.searchTerm, $options: 'i' } },
          { description: { $regex: options.searchTerm, $options: 'i' } }
        ];
      }
      
      // 执行查询
      const [items, total] = await Promise.all([
        this.biomarkerModel.find(query).skip(skip).limit(limit),
        this.biomarkerModel.countDocuments(query)
      ]);
      
      return {
        items,
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      };
    } catch (error) {
      this.logger.error('Failed to query biomarkers', error);
      throw new Error('Failed to query biomarkers');
    }
  }

  /**
   * 删除精准医学知识
   * @param id 知识ID
   */
  async deletePrecisionMedicineKnowledge(id: string): Promise<boolean> {
    try {
      this.logger.info(`Deleting precision medicine knowledge: ${id}`);
      
      // 删除精准医学知识
      const result = await this.precisionMedicineModel.findByIdAndDelete(id);
      
      if (result) {
        // 同时删除基础知识
        await this.knowledgeService.deleteKnowledge(id);
        return true;
      }
      
      return false;
    } catch (error) {
      this.logger.error(`Failed to delete precision medicine knowledge: ${id}`, error);
      throw new Error('Failed to delete precision medicine knowledge');
    }
  }

  /**
   * 获取特定基因相关的所有知识
   * @param gene 基因名称
   */
  async getKnowledgeByGene(gene: string): Promise<IPrecisionMedicineKnowledge[]> {
    try {
      this.logger.info(`Getting knowledge for gene: ${gene}`);
      
      return this.precisionMedicineModel.find({
        relevantGenes: gene
      });
    } catch (error) {
      this.logger.error(`Failed to get knowledge for gene: ${gene}`, error);
      throw new Error('Failed to get knowledge by gene');
    }
  }

  /**
   * 获取特定疾病相关的所有知识
   * @param disease 疾病名称
   */
  async getKnowledgeByDisease(disease: string): Promise<IPrecisionMedicineKnowledge[]> {
    try {
      this.logger.info(`Getting knowledge for disease: ${disease}`);
      
      return this.precisionMedicineModel.find({
        'diseaseAssociations.disease': { $regex: disease, $options: 'i' }
      });
    } catch (error) {
      this.logger.error(`Failed to get knowledge for disease: ${disease}`, error);
      throw new Error('Failed to get knowledge by disease');
    }
  }
}