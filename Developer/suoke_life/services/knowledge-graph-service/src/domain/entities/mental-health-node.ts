/**
 * 心理健康知识节点实体
 * 用于存储现代心理学和精神健康相关的知识节点
 */

import { BaseNode } from './base-node';

export enum PsychologyDomain {
  COGNITIVE = 'cognitive',
  BEHAVIORAL = 'behavioral',
  EMOTIONAL = 'emotional',
  DEVELOPMENTAL = 'developmental',
  SOCIAL = 'social',
  POSITIVE = 'positive',
  CLINICAL = 'clinical',
  OTHER = 'other',
}

export interface ThoughtPattern {
  pattern: string;
  alternative: string;
  interventionStrategy: string;
}

export interface AssessmentTool {
  tool: string;
  purpose: string;
  validationInfo?: string;
  interpretationGuidelines?: string;
}

export class MentalHealthNode extends BaseNode {
  psychologyDomain: PsychologyDomain;
  theoreticalFramework?: string;
  applicableAgeGroups?: string[];
  culturalConsiderations?: string;
  cbtTechniques?: string[];
  thoughtPatterns?: ThoughtPattern[];
  emotionRegulationStrategies?: string[];
  triggerManagementTechniques?: string[];
  stressorsIdentified?: string[];
  copingMechanisms?: string[];
  resilienceBuildingPractices?: string[];
  assessmentTools?: AssessmentTool[];
  interventionApproaches?: string[];
  treatmentProtocols?: string;
  effectivenessData?: string;
  recommendedDuration?: string;
  followUpProcedures?: string;

  constructor(data: Partial<MentalHealthNode>) {
    super(data);
    this.psychologyDomain = data.psychologyDomain || PsychologyDomain.OTHER;
    this.theoreticalFramework = data.theoreticalFramework;
    this.applicableAgeGroups = data.applicableAgeGroups || [];
    this.culturalConsiderations = data.culturalConsiderations;
    this.cbtTechniques = data.cbtTechniques || [];
    this.thoughtPatterns = data.thoughtPatterns || [];
    this.emotionRegulationStrategies = data.emotionRegulationStrategies || [];
    this.triggerManagementTechniques = data.triggerManagementTechniques || [];
    this.stressorsIdentified = data.stressorsIdentified || [];
    this.copingMechanisms = data.copingMechanisms || [];
    this.resilienceBuildingPractices = data.resilienceBuildingPractices || [];
    this.assessmentTools = data.assessmentTools || [];
    this.interventionApproaches = data.interventionApproaches || [];
    this.treatmentProtocols = data.treatmentProtocols;
    this.effectivenessData = data.effectivenessData;
    this.recommendedDuration = data.recommendedDuration;
    this.followUpProcedures = data.followUpProcedures;
  }

  /**
   * 转换为Neo4j节点属性
   */
  toNeo4jProperties(): Record<string, any> {
    return {
      ...super.toNeo4jProperties(),
      psychologyDomain: this.psychologyDomain,
      theoreticalFramework: this.theoreticalFramework,
      applicableAgeGroups: JSON.stringify(this.applicableAgeGroups || []),
      culturalConsiderations: this.culturalConsiderations,
      cbtTechniques: JSON.stringify(this.cbtTechniques || []),
      thoughtPatterns: JSON.stringify(this.thoughtPatterns || []),
      emotionRegulationStrategies: JSON.stringify(this.emotionRegulationStrategies || []),
      triggerManagementTechniques: JSON.stringify(this.triggerManagementTechniques || []),
      stressorsIdentified: JSON.stringify(this.stressorsIdentified || []),
      copingMechanisms: JSON.stringify(this.copingMechanisms || []),
      resilienceBuildingPractices: JSON.stringify(this.resilienceBuildingPractices || []),
      assessmentTools: JSON.stringify(this.assessmentTools || []),
      interventionApproaches: JSON.stringify(this.interventionApproaches || []),
      treatmentProtocols: this.treatmentProtocols,
      effectivenessData: this.effectivenessData,
      recommendedDuration: this.recommendedDuration,
      followUpProcedures: this.followUpProcedures,
      nodeType: 'MentalHealth'
    };
  }

  /**
   * 从Neo4j节点创建实体
   */
  static fromNeo4jNode(node: Record<string, any>): MentalHealthNode {
    return new MentalHealthNode({
      ...BaseNode.fromNeo4jNodeBase(node),
      psychologyDomain: node.psychologyDomain,
      theoreticalFramework: node.theoreticalFramework,
      applicableAgeGroups: JSON.parse(node.applicableAgeGroups || '[]'),
      culturalConsiderations: node.culturalConsiderations,
      cbtTechniques: JSON.parse(node.cbtTechniques || '[]'),
      thoughtPatterns: JSON.parse(node.thoughtPatterns || '[]'),
      emotionRegulationStrategies: JSON.parse(node.emotionRegulationStrategies || '[]'),
      triggerManagementTechniques: JSON.parse(node.triggerManagementTechniques || '[]'),
      stressorsIdentified: JSON.parse(node.stressorsIdentified || '[]'),
      copingMechanisms: JSON.parse(node.copingMechanisms || '[]'),
      resilienceBuildingPractices: JSON.parse(node.resilienceBuildingPractices || '[]'),
      assessmentTools: JSON.parse(node.assessmentTools || '[]'),
      interventionApproaches: JSON.parse(node.interventionApproaches || '[]'),
      treatmentProtocols: node.treatmentProtocols,
      effectivenessData: node.effectivenessData,
      recommendedDuration: node.recommendedDuration,
      followUpProcedures: node.followUpProcedures
    });
  }

  /**
   * 获取向量化表示所需的文本
   */
  getTextForEmbedding(): string {
    let text = `${this.title}. ${this.content}`;
    
    // 添加心理学领域和理论框架
    text += ` 心理学领域: ${this.psychologyDomain}.`;
    if (this.theoreticalFramework) {
      text += ` 理论框架: ${this.theoreticalFramework}.`;
    }
    
    // 添加适用年龄组
    if (this.applicableAgeGroups && this.applicableAgeGroups.length > 0) {
      text += ` 适用年龄组: ${this.applicableAgeGroups.join(', ')}.`;
    }
    
    // 添加文化考虑因素
    if (this.culturalConsiderations) {
      text += ` 文化考虑因素: ${this.culturalConsiderations}.`;
    }
    
    // 添加认知行为技术
    if (this.cbtTechniques && this.cbtTechniques.length > 0) {
      text += ` 认知行为技术: ${this.cbtTechniques.join(', ')}.`;
    }
    
    // 添加思维模式
    if (this.thoughtPatterns && this.thoughtPatterns.length > 0) {
      text += ` 思维模式: ${this.thoughtPatterns.map(tp => 
        `${tp.pattern}→${tp.alternative}`).join(', ')}.`;
    }
    
    // 添加情绪调节策略
    if (this.emotionRegulationStrategies && this.emotionRegulationStrategies.length > 0) {
      text += ` 情绪调节策略: ${this.emotionRegulationStrategies.join(', ')}.`;
    }
    
    // 添加应对机制
    if (this.copingMechanisms && this.copingMechanisms.length > 0) {
      text += ` 应对机制: ${this.copingMechanisms.join(', ')}.`;
    }
    
    // 添加干预方法
    if (this.interventionApproaches && this.interventionApproaches.length > 0) {
      text += ` 干预方法: ${this.interventionApproaches.join(', ')}.`;
    }
    
    // 添加治疗方案
    if (this.treatmentProtocols) {
      text += ` 治疗方案: ${this.treatmentProtocols}.`;
    }
    
    return text;
  }
}