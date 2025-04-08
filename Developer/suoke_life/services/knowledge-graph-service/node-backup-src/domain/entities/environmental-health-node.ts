/**
 * 环境健康知识节点实体
 * 用于存储环境因素与健康关系的相关知识节点
 */

import { BaseNode } from './base-node';

export enum EnvironmentalFactorType {
  AIR = 'air',
  WATER = 'water',
  SOIL = 'soil',
  NOISE = 'noise',
  LIGHT = 'light',
  RADIATION = 'radiation',
  CLIMATE = 'climate',
  OTHER = 'other',
}

export enum ExposureRoute {
  INHALATION = 'inhalation',
  INGESTION = 'ingestion',
  DERMAL = 'dermal',
  OTHER = 'other',
}

export enum SpatialScale {
  LOCAL = 'local',
  REGIONAL = 'regional',
  GLOBAL = 'global',
  MULTIPLE = 'multiple',
}

export enum TemporalPattern {
  ACUTE = 'acute',
  CHRONIC = 'chronic',
  SEASONAL = 'seasonal',
  DIURNAL = 'diurnal',
  MULTIPLE = 'multiple',
}

export enum EvidenceStrength {
  STRONG = 'strong',
  MODERATE = 'moderate',
  LIMITED = 'limited',
  INADEQUATE = 'inadequate',
}

export interface HealthEffect {
  effect: string;
  targetSystem: string; // 靶器官/系统
  latencyPeriod?: string; // 潜伏期
  doseResponse?: string; // 剂量-反应关系
  vulnerableGroups?: string[]; // 易感人群
  evidenceStrength: EvidenceStrength;
}

export interface SafetyStandard {
  organization: string;
  limit: string;
  unit: string;
  context?: string;
}

export class EnvironmentalHealthNode extends BaseNode {
  environmentalFactor: string;
  factorType: EnvironmentalFactorType;
  exposureRoutes: ExposureRoute[];
  spatialScale: SpatialScale;
  temporalPattern: TemporalPattern;
  healthEffects: HealthEffect[];
  measurementMethods?: string[];
  monitoringGuidelines?: string;
  safetyStandards?: SafetyStandard[];
  preventionStrategies?: string[];
  remedialActions?: string[];
  policyRecommendations?: string[];
  seasonalVariations?: string;
  weatherDependence?: string;
  climateChangeImplications?: string;

  constructor(data: Partial<EnvironmentalHealthNode>) {
    super(data);
    this.environmentalFactor = data.environmentalFactor || '';
    this.factorType = data.factorType || EnvironmentalFactorType.OTHER;
    this.exposureRoutes = data.exposureRoutes || [ExposureRoute.OTHER];
    this.spatialScale = data.spatialScale || SpatialScale.LOCAL;
    this.temporalPattern = data.temporalPattern || TemporalPattern.ACUTE;
    this.healthEffects = data.healthEffects || [];
    this.measurementMethods = data.measurementMethods || [];
    this.monitoringGuidelines = data.monitoringGuidelines;
    this.safetyStandards = data.safetyStandards || [];
    this.preventionStrategies = data.preventionStrategies || [];
    this.remedialActions = data.remedialActions || [];
    this.policyRecommendations = data.policyRecommendations || [];
    this.seasonalVariations = data.seasonalVariations;
    this.weatherDependence = data.weatherDependence;
    this.climateChangeImplications = data.climateChangeImplications;
  }

  /**
   * 转换为Neo4j节点属性
   */
  toNeo4jProperties(): Record<string, any> {
    return {
      ...super.toNeo4jProperties(),
      environmentalFactor: this.environmentalFactor,
      factorType: this.factorType,
      exposureRoutes: JSON.stringify(this.exposureRoutes),
      spatialScale: this.spatialScale,
      temporalPattern: this.temporalPattern,
      healthEffects: JSON.stringify(this.healthEffects),
      measurementMethods: JSON.stringify(this.measurementMethods || []),
      monitoringGuidelines: this.monitoringGuidelines,
      safetyStandards: JSON.stringify(this.safetyStandards || []),
      preventionStrategies: JSON.stringify(this.preventionStrategies || []),
      remedialActions: JSON.stringify(this.remedialActions || []),
      policyRecommendations: JSON.stringify(this.policyRecommendations || []),
      seasonalVariations: this.seasonalVariations,
      weatherDependence: this.weatherDependence,
      climateChangeImplications: this.climateChangeImplications,
      nodeType: 'EnvironmentalHealth'
    };
  }

  /**
   * 从Neo4j节点创建实体
   */
  static fromNeo4jNode(node: Record<string, any>): EnvironmentalHealthNode {
    return new EnvironmentalHealthNode({
      ...BaseNode.fromNeo4jNodeBase(node),
      environmentalFactor: node.environmentalFactor,
      factorType: node.factorType,
      exposureRoutes: JSON.parse(node.exposureRoutes),
      spatialScale: node.spatialScale,
      temporalPattern: node.temporalPattern,
      healthEffects: JSON.parse(node.healthEffects),
      measurementMethods: JSON.parse(node.measurementMethods || '[]'),
      monitoringGuidelines: node.monitoringGuidelines,
      safetyStandards: JSON.parse(node.safetyStandards || '[]'),
      preventionStrategies: JSON.parse(node.preventionStrategies || '[]'),
      remedialActions: JSON.parse(node.remedialActions || '[]'),
      policyRecommendations: JSON.parse(node.policyRecommendations || '[]'),
      seasonalVariations: node.seasonalVariations,
      weatherDependence: node.weatherDependence,
      climateChangeImplications: node.climateChangeImplications
    });
  }

  /**
   * 获取向量化表示所需的文本
   */
  getTextForEmbedding(): string {
    let text = `${this.title}. ${this.content}`;
    
    // 添加环境因素信息
    text += ` 环境因素: ${this.environmentalFactor}, 类型: ${this.factorType}.`;
    
    // 添加暴露途径
    if (this.exposureRoutes && this.exposureRoutes.length > 0) {
      text += ` 暴露途径: ${this.exposureRoutes.join(', ')}.`;
    }
    
    // 添加健康影响
    if (this.healthEffects && this.healthEffects.length > 0) {
      text += ` 健康影响: ${this.healthEffects.map(effect => 
        `${effect.effect}(靶系统:${effect.targetSystem})`).join(', ')}.`;
    }
    
    // 添加易感人群
    const vulnerableGroups = this.healthEffects
      ?.flatMap(effect => effect.vulnerableGroups || [])
      .filter((value, index, self) => self.indexOf(value) === index);
    if (vulnerableGroups && vulnerableGroups.length > 0) {
      text += ` 易感人群: ${vulnerableGroups.join(', ')}.`;
    }
    
    // 添加预防策略
    if (this.preventionStrategies && this.preventionStrategies.length > 0) {
      text += ` 预防策略: ${this.preventionStrategies.join(', ')}.`;
    }
    
    // 添加季节性变化
    if (this.seasonalVariations) {
      text += ` 季节性变化: ${this.seasonalVariations}.`;
    }
    
    // 添加气候变化影响
    if (this.climateChangeImplications) {
      text += ` 气候变化影响: ${this.climateChangeImplications}.`;
    }
    
    return text;
  }
}