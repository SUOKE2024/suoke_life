/**
 * 心理健康数据接口定义
 */
import { Document } from 'mongoose';

export interface MentalHealthData extends Document {
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
   * 心理问题类型（如焦虑、抑郁、强迫症等）
   */
  issueType: string;
  
  /**
   * 相关症状
   */
  symptoms: string[];
  
  /**
   * 可能的原因
   */
  possibleCauses: string[];
  
  /**
   * 干预方法
   */
  interventionMethods: string[];
  
  /**
   * 治疗方法
   */
  treatmentMethods: string[];
  
  /**
   * 推荐的自助措施
   */
  selfHelpMeasures: string[];
  
  /**
   * 目标年龄组
   */
  targetAgeGroups: string[];
  
  /**
   * 相关资源（如书籍、网站、应用等）
   */
  resources: {
    type: string;
    name: string;
    description: string;
    url?: string;
  }[];
  
  /**
   * 适用的场景
   */
  applicableScenarios: string[];
  
  /**
   * 预期效果
   */
  expectedOutcomes: string[];
  
  /**
   * 专家建议
   */
  expertAdvice: string;
  
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