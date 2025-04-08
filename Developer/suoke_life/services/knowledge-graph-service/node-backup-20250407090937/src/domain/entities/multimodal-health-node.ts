/**
 * 多模态健康数据节点实体
 * 用于存储图像、音频、可穿戴设备等多模态健康数据相关的知识节点
 */

import { BaseNode } from './base-node';

export enum ModalityType {
  IMAGE = 'image',
  AUDIO = 'audio',
  WEARABLE = 'wearable',
  ENVIRONMENTAL = 'environmental',
  COMBINED = 'combined',
  OTHER = 'other',
}

export interface ImageFeature {
  feature: string;
  significance: string;
  detectionMethod: string;
  visualRepresentation?: string; // 参考图像URL或描述
}

export interface AudioFeature {
  feature: string;
  significance: string;
  frequencyRange?: string;
  exampleSounds?: string[]; // 参考音频URL或描述
}

export interface WearableMetric {
  metric: string;
  normalRanges?: string;
  abnormalPatterns?: string[];
  correlatedConditions?: string[];
  dataCollectionProtocol?: string;
}

export interface EnvironmentalFactor {
  factor: string;
  healthImpact: string;
  measurementMethod: string;
  mitigationStrategies?: string[];
}

export class MultimodalHealthNode extends BaseNode {
  modalityType: ModalityType;
  analysisMethod: string;
  dataRequirements?: string[];
  privacyConsiderations?: string;
  imageFeatures?: ImageFeature[];
  audioFeatures?: AudioFeature[];
  wearableMetrics?: WearableMetric[];
  environmentalFactors?: EnvironmentalFactor[];
  dataFusionTechniques?: string[];
  machineLearningSummary?: string;
  validationResults?: string;
  limitationsAndCaveats?: string;

  constructor(data: Partial<MultimodalHealthNode>) {
    super(data);
    this.modalityType = data.modalityType || ModalityType.OTHER;
    this.analysisMethod = data.analysisMethod || '';
    this.dataRequirements = data.dataRequirements || [];
    this.privacyConsiderations = data.privacyConsiderations;
    this.imageFeatures = data.imageFeatures || [];
    this.audioFeatures = data.audioFeatures || [];
    this.wearableMetrics = data.wearableMetrics || [];
    this.environmentalFactors = data.environmentalFactors || [];
    this.dataFusionTechniques = data.dataFusionTechniques || [];
    this.machineLearningSummary = data.machineLearningSummary;
    this.validationResults = data.validationResults;
    this.limitationsAndCaveats = data.limitationsAndCaveats;
  }

  /**
   * 转换为Neo4j节点属性
   */
  toNeo4jProperties(): Record<string, any> {
    return {
      ...super.toNeo4jProperties(),
      modalityType: this.modalityType,
      analysisMethod: this.analysisMethod,
      dataRequirements: JSON.stringify(this.dataRequirements || []),
      privacyConsiderations: this.privacyConsiderations,
      imageFeatures: JSON.stringify(this.imageFeatures || []),
      audioFeatures: JSON.stringify(this.audioFeatures || []),
      wearableMetrics: JSON.stringify(this.wearableMetrics || []),
      environmentalFactors: JSON.stringify(this.environmentalFactors || []),
      dataFusionTechniques: JSON.stringify(this.dataFusionTechniques || []),
      machineLearningSummary: this.machineLearningSummary,
      validationResults: this.validationResults,
      limitationsAndCaveats: this.limitationsAndCaveats,
      nodeType: 'MultimodalHealth'
    };
  }

  /**
   * 从Neo4j节点创建实体
   */
  static fromNeo4jNode(node: Record<string, any>): MultimodalHealthNode {
    return new MultimodalHealthNode({
      ...BaseNode.fromNeo4jNodeBase(node),
      modalityType: node.modalityType,
      analysisMethod: node.analysisMethod,
      dataRequirements: JSON.parse(node.dataRequirements || '[]'),
      privacyConsiderations: node.privacyConsiderations,
      imageFeatures: JSON.parse(node.imageFeatures || '[]'),
      audioFeatures: JSON.parse(node.audioFeatures || '[]'),
      wearableMetrics: JSON.parse(node.wearableMetrics || '[]'),
      environmentalFactors: JSON.parse(node.environmentalFactors || '[]'),
      dataFusionTechniques: JSON.parse(node.dataFusionTechniques || '[]'),
      machineLearningSummary: node.machineLearningSummary,
      validationResults: node.validationResults,
      limitationsAndCaveats: node.limitationsAndCaveats
    });
  }

  /**
   * 获取向量化表示所需的文本
   */
  getTextForEmbedding(): string {
    let text = `${this.title}. ${this.content}`;
    
    // 添加模态类型和分析方法
    text += ` 数据模态: ${this.modalityType}. 分析方法: ${this.analysisMethod}.`;
    
    // 添加数据要求
    if (this.dataRequirements && this.dataRequirements.length > 0) {
      text += ` 数据要求: ${this.dataRequirements.join(', ')}.`;
    }
    
    // 添加图像特征
    if (this.imageFeatures && this.imageFeatures.length > 0) {
      text += ` 图像特征: ${this.imageFeatures.map(feature => 
        `${feature.feature}(${feature.significance})`).join(', ')}.`;
    }
    
    // 添加音频特征
    if (this.audioFeatures && this.audioFeatures.length > 0) {
      text += ` 音频特征: ${this.audioFeatures.map(feature => 
        `${feature.feature}(${feature.significance})`).join(', ')}.`;
    }
    
    // 添加可穿戴设备指标
    if (this.wearableMetrics && this.wearableMetrics.length > 0) {
      text += ` 可穿戴设备指标: ${this.wearableMetrics.map(metric => 
        `${metric.metric}(${metric.correlatedConditions?.join('、') || ''})`).join(', ')}.`;
    }
    
    // 添加环境因素
    if (this.environmentalFactors && this.environmentalFactors.length > 0) {
      text += ` 环境因素: ${this.environmentalFactors.map(factor => 
        `${factor.factor}(${factor.healthImpact})`).join(', ')}.`;
    }
    
    // 添加机器学习摘要
    if (this.machineLearningSummary) {
      text += ` 机器学习方法: ${this.machineLearningSummary}.`;
    }
    
    return text;
  }
}