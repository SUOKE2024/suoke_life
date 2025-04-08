/**
 * 精准医学知识节点实体
 * 用于存储基因组学和个性化健康相关的知识节点
 */

import { BaseNode } from './base-node';

export enum PrecisionMedicineType {
  GENETIC = 'genetic',
  METABOLOMIC = 'metabolomic',
  MICROBIOME = 'microbiome',
  EPIGENETIC = 'epigenetic',
  PHARMACOGENOMIC = 'pharmacogenomic',
  OTHER = 'other',
}

export enum ConfidenceLevel {
  HIGH = 'high',
  MODERATE = 'moderate',
  LOW = 'low',
  PRELIMINARY = 'preliminary',
}

export interface NutrientInteraction {
  nutrient: string;
  effect: string;
  recommendation?: string;
  evidenceStrength: 'strong' | 'moderate' | 'weak';
}

export interface DrugInteraction {
  drug: string;
  effect: string;
  dosageAdjustment?: string;
  adverseReactions?: string[];
  evidenceStrength: 'strong' | 'moderate' | 'weak';
}

export interface DiseaseAssociation {
  disease: string;
  riskFactor: number; // 相对风险
  prevalence?: number; // 普通人群患病率
  preventionStrategies?: string[];
  evidenceStrength: 'strong' | 'moderate' | 'weak';
}

export interface EnvironmentalInteraction {
  factor: string;
  effect: string;
  mitigation?: string;
  evidenceStrength: 'strong' | 'moderate' | 'weak';
}

export class PrecisionMedicineNode extends BaseNode {
  studyType: PrecisionMedicineType;
  confidenceLevel: ConfidenceLevel;
  relevantGenes?: string[];
  snpReferences?: string[];
  sampleSize?: number;
  populationGroups?: string[];
  heritability?: number;
  technicalPlatform?: string;
  nutrientInteractions?: NutrientInteraction[];
  drugInteractions?: DrugInteraction[];
  diseaseAssociations?: DiseaseAssociation[];
  environmentalInteractions?: EnvironmentalInteraction[];
  personalizationFactors?: string[];
  recommendationAlgorithm?: string;
  applicableBiomarkers?: string[];

  constructor(data: Partial<PrecisionMedicineNode>) {
    super(data);
    this.studyType = data.studyType || PrecisionMedicineType.OTHER;
    this.confidenceLevel = data.confidenceLevel || ConfidenceLevel.PRELIMINARY;
    this.relevantGenes = data.relevantGenes || [];
    this.snpReferences = data.snpReferences || [];
    this.sampleSize = data.sampleSize;
    this.populationGroups = data.populationGroups || [];
    this.heritability = data.heritability;
    this.technicalPlatform = data.technicalPlatform;
    this.nutrientInteractions = data.nutrientInteractions || [];
    this.drugInteractions = data.drugInteractions || [];
    this.diseaseAssociations = data.diseaseAssociations || [];
    this.environmentalInteractions = data.environmentalInteractions || [];
    this.personalizationFactors = data.personalizationFactors || [];
    this.recommendationAlgorithm = data.recommendationAlgorithm;
    this.applicableBiomarkers = data.applicableBiomarkers || [];
  }

  /**
   * 转换为Neo4j节点属性
   */
  toNeo4jProperties(): Record<string, any> {
    return {
      ...super.toNeo4jProperties(),
      studyType: this.studyType,
      confidenceLevel: this.confidenceLevel,
      relevantGenes: JSON.stringify(this.relevantGenes || []),
      snpReferences: JSON.stringify(this.snpReferences || []),
      sampleSize: this.sampleSize,
      populationGroups: JSON.stringify(this.populationGroups || []),
      heritability: this.heritability,
      technicalPlatform: this.technicalPlatform,
      nutrientInteractions: JSON.stringify(this.nutrientInteractions || []),
      drugInteractions: JSON.stringify(this.drugInteractions || []),
      diseaseAssociations: JSON.stringify(this.diseaseAssociations || []),
      environmentalInteractions: JSON.stringify(this.environmentalInteractions || []),
      personalizationFactors: JSON.stringify(this.personalizationFactors || []),
      recommendationAlgorithm: this.recommendationAlgorithm,
      applicableBiomarkers: JSON.stringify(this.applicableBiomarkers || []),
      nodeType: 'PrecisionMedicine'
    };
  }

  /**
   * 从Neo4j节点创建实体
   */
  static fromNeo4jNode(node: Record<string, any>): PrecisionMedicineNode {
    return new PrecisionMedicineNode({
      ...BaseNode.fromNeo4jNodeBase(node),
      studyType: node.studyType,
      confidenceLevel: node.confidenceLevel,
      relevantGenes: JSON.parse(node.relevantGenes || '[]'),
      snpReferences: JSON.parse(node.snpReferences || '[]'),
      sampleSize: node.sampleSize,
      populationGroups: JSON.parse(node.populationGroups || '[]'),
      heritability: node.heritability,
      technicalPlatform: node.technicalPlatform,
      nutrientInteractions: JSON.parse(node.nutrientInteractions || '[]'),
      drugInteractions: JSON.parse(node.drugInteractions || '[]'),
      diseaseAssociations: JSON.parse(node.diseaseAssociations || '[]'),
      environmentalInteractions: JSON.parse(node.environmentalInteractions || '[]'),
      personalizationFactors: JSON.parse(node.personalizationFactors || '[]'),
      recommendationAlgorithm: node.recommendationAlgorithm,
      applicableBiomarkers: JSON.parse(node.applicableBiomarkers || '[]')
    });
  }

  /**
   * 获取向量化表示所需的文本
   */
  getTextForEmbedding(): string {
    let text = `${this.title}. ${this.content}`;
    
    // 添加基因信息
    if (this.relevantGenes && this.relevantGenes.length > 0) {
      text += ` 相关基因: ${this.relevantGenes.join(', ')}.`;
    }
    
    // 添加疾病关联
    if (this.diseaseAssociations && this.diseaseAssociations.length > 0) {
      text += ` 疾病关联: ${this.diseaseAssociations.map(da => 
        `${da.disease}(风险因子:${da.riskFactor})`).join(', ')}.`;
    }
    
    // 添加营养素相互作用
    if (this.nutrientInteractions && this.nutrientInteractions.length > 0) {
      text += ` 营养素相互作用: ${this.nutrientInteractions.map(ni => 
        `${ni.nutrient}(${ni.effect})`).join(', ')}.`;
    }
    
    // 添加药物相互作用
    if (this.drugInteractions && this.drugInteractions.length > 0) {
      text += ` 药物相互作用: ${this.drugInteractions.map(di => 
        `${di.drug}(${di.effect})`).join(', ')}.`;
    }
    
    return text;
  }
}