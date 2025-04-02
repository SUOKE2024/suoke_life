/**
 * 环境健康数据接口定义
 */
import { Document } from 'mongoose';

export interface EnvironmentalHealthData extends Document {
  /**
   * 条目标题
   */
  title: string;
  
  /**
   * 简短描述
   */
  description: string;
  
  /**
   * 详细内容
   */
  content: string;
  
  /**
   * 环境类型（如空气、水、土壤、噪音等）
   */
  environmentType: string;
  
  /**
   * 污染物类型
   */
  pollutantType: string[];
  
  /**
   * 健康影响
   */
  healthImpacts: string[];
  
  /**
   * 风险级别（1-5，5表示最高风险）
   */
  riskLevel: number;
  
  /**
   * 易感人群
   */
  vulnerableGroups: string[];
  
  /**
   * 保护措施
   */
  protectiveMeasures: string[];
  
  /**
   * 预防建议
   */
  preventiveAdvice: string[];
  
  /**
   * 相关疾病
   */
  relatedDiseases: string[];
  
  /**
   * 地区特异性（如特定区域的环境问题）
   */
  regionSpecific: string[];
  
  /**
   * 季节性影响
   */
  seasonalEffects: string[];
  
  /**
   * 监测指标
   */
  monitoringIndicators: {
    name: string;
    unit: string;
    safeRange: string;
    description: string;
  }[];
  
  /**
   * 关键词
   */
  keywords: string[];
  
  /**
   * 引用来源
   */
  references: {
    author: string;
    title: string;
    source: string;
    year: number;
    url?: string;
  }[];
  
  /**
   * 相关政策法规
   */
  relatedPolicies: {
    name: string;
    issuer: string;
    year: number;
    description: string;
    url?: string;
  }[];
  
  /**
   * 相关知识关联
   */
  relatedKnowledge: (string | Document)[];
  
  /**
   * 标签
   */
  tags: (string | Document)[];
  
  /**
   * 分类
   */
  categories: (string | Document)[];
  
  /**
   * 创建时间
   */
  createdAt: Date;
  
  /**
   * 更新时间
   */
  updatedAt: Date;
  
  /**
   * 创建者ID
   */
  createdBy?: string;
  
  /**
   * 版本
   */
  version: number;
}