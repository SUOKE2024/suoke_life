/**
 * 多模态健康数据相关接口定义
 * 针对图像、语音、可穿戴设备等多种数据源的健康分析
 */

import { Document } from 'mongoose';
import { IKnowledge } from './knowledge.interface';

/**
 * 多模态健康知识接口
 * 扩展基本知识接口，增加多模态数据特有属性
 */
export interface IMultimodalHealthKnowledge extends IKnowledge {
  // 基本属性
  modalityType: 'image' | 'audio' | 'wearable' | 'environmental' | 'combined' | 'other';
  analysisMethod: string; // 分析方法
  dataRequirements?: string[]; // 数据要求
  privacyConsiderations?: string; // 隐私考虑事项
  
  // 图像相关属性
  imageFeatures?: Array<{
    feature: string;
    significance: string;
    detectionMethod: string;
    visualRepresentation?: string; // 参考图像URL或描述
  }>;
  
  // 音频相关属性
  audioFeatures?: Array<{
    feature: string;
    significance: string;
    frequencyRange?: string;
    exampleSounds?: string[]; // 参考音频URL或描述
  }>;
  
  // 可穿戴设备相关属性
  wearableMetrics?: Array<{
    metric: string;
    normalRanges?: string;
    abnormalPatterns?: string[];
    correlatedConditions?: string[];
    dataCollectionProtocol?: string;
  }>;
  
  // 环境数据相关属性
  environmentalFactors?: Array<{
    factor: string;
    healthImpact: string;
    measurementMethod: string;
    mitigationStrategies?: string[];
  }>;
  
  // 数据融合和分析
  dataFusionTechniques?: string[]; // 数据融合技术
  machineLearningSummary?: string; // 机器学习方法概述
  validationResults?: string; // 验证结果
  limitationsAndCaveats?: string; // 局限性和注意事项
}

/**
 * 健康数据模式接口
 * 描述健康数据的模式和异常情况
 */
export interface IHealthPattern extends Document {
  name: string;
  description: string;
  modalityType: 'image' | 'audio' | 'wearable' | 'environmental' | 'combined' | 'other';
  patternFeatures: string[];
  normalVariations?: string[];
  abnormalVariations?: Array<{
    variation: string;
    possibleCauses: string[];
    severity: 'low' | 'moderate' | 'high';
    recommendations?: string[];
  }>;
  detectionAlgorithm?: string;
  relatedPatterns?: string[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 多模态查询选项
 */
export interface MultimodalQueryOptions {
  modalityType?: 'image' | 'audio' | 'wearable' | 'environmental' | 'combined' | 'other';
  feature?: string;
  condition?: string;
  environmentalFactor?: string;
  pattern?: string;
  page?: number;
  limit?: number;
}

/**
 * 健康模式查询选项
 */
export interface HealthPatternQueryOptions {
  modalityType?: 'image' | 'audio' | 'wearable' | 'environmental' | 'combined' | 'other';
  searchTerm?: string;
  abnormalVariation?: string;
  severity?: 'low' | 'moderate' | 'high';
  page?: number;
  limit?: number;
}

/**
 * 多模态健康知识类型
 */
export type MultimodalHealthKnowledgeType = 
  'multimodal-health/image' | 
  'multimodal-health/audio' | 
  'multimodal-health/wearable' | 
  'multimodal-health/environmental' | 
  'multimodal-health/combined';