/**
 * 精准医学相关接口定义
 * 针对基因组学数据和个性化健康的特殊属性
 */

import { Document } from 'mongoose';
import { IKnowledge } from './knowledge.interface';

/**
 * 基因组学知识接口
 * 扩展基本知识接口，增加基因组学特有属性
 */
export interface IPrecisionMedicineKnowledge extends IKnowledge {
  // 精准医学基本属性
  studyType?: 'genetic' | 'metabolomic' | 'microbiome' | 'epigenetic' | 'pharmacogenomic' | 'other';
  confidenceLevel?: 'high' | 'moderate' | 'low' | 'preliminary'; // 研究置信度
  relevantGenes?: string[]; // 相关基因
  snpReferences?: string[]; // SNP参考编号
  sampleSize?: number; // 研究样本大小
  populationGroups?: string[]; // 研究人群
  heritability?: number; // 遗传率
  technicalPlatform?: string; // 使用的技术平台
  
  // 基因-营养相关属性
  nutrientInteractions?: Array<{
    nutrient: string;
    effect: string;
    recommendation?: string;
    evidenceStrength: 'strong' | 'moderate' | 'weak';
  }>;
  
  // 基因-药物相关属性
  drugInteractions?: Array<{
    drug: string;
    effect: string;
    dosageAdjustment?: string;
    adverseReactions?: string[];
    evidenceStrength: 'strong' | 'moderate' | 'weak';
  }>;
  
  // 基因-疾病相关属性
  diseaseAssociations?: Array<{
    disease: string;
    riskFactor: number; // 相对风险
    prevalence?: number; // 普通人群患病率
    preventionStrategies?: string[];
    evidenceStrength: 'strong' | 'moderate' | 'weak';
  }>;
  
  // 基因-环境相关属性
  environmentalInteractions?: Array<{
    factor: string;
    effect: string;
    mitigation?: string;
    evidenceStrength: 'strong' | 'moderate' | 'weak';
  }>;
  
  // 个性化建议
  personalizationFactors?: string[]; // 个性化因素
  recommendationAlgorithm?: string; // 建议生成算法
  applicableBiomarkers?: string[]; // 适用生物标记物
}

/**
 * 生物标记物接口
 */
export interface IBiomarker extends Document {
  name: string;
  category: 'genetic' | 'blood' | 'urine' | 'saliva' | 'microbiome' | 'imaging' | 'other';
  description: string;
  unit?: string;
  normalRange?: {
    min?: number;
    max?: number;
    description?: string;
  };
  interpretationGuidelines?: string;
  relatedConditions?: string[];
  monitoringFrequency?: string;
  sampleRequirements?: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 精准医学知识查询选项
 */
export interface PrecisionMedicineQueryOptions {
  studyType?: 'genetic' | 'metabolomic' | 'microbiome' | 'epigenetic' | 'pharmacogenomic' | 'other';
  confidenceLevel?: 'high' | 'moderate' | 'low' | 'preliminary';
  genes?: string[];
  disease?: string;
  nutrient?: string;
  drug?: string;
  environmentalFactor?: string;
  populationGroup?: string;
  page?: number;
  limit?: number;
}

/**
 * 生物标记物查询选项
 */
export interface BiomarkerQueryOptions {
  category?: string;
  condition?: string;
  searchTerm?: string;
  page?: number;
  limit?: number;
}

/**
 * 精准医学知识类型
 */
export type PrecisionMedicineKnowledgeType = 
  'precision-medicine/genetic' | 
  'precision-medicine/metabolomic' | 
  'precision-medicine/microbiome' | 
  'precision-medicine/epigenetic' | 
  'precision-medicine/pharmacogenomic';