/**
 * 扩展知识相关接口定义
 * 针对中国传统文化和现代医学知识的特殊属性
 */

import { Document } from 'mongoose';
import { IKnowledge } from './knowledge.interface';

/**
 * 传统文化知识接口
 * 扩展基本知识接口，增加传统文化特有属性
 */
export interface ITraditionalCultureKnowledge extends IKnowledge {
  // 传统文化特有属性
  culturalSystem?: 'yijing' | 'taoism' | 'buddhism' | 'physiognomy' | 'fengshui' | 'classics' | 'other';
  historicalPeriod?: string; // 历史时期
  originalText?: string; // 原文内容
  interpretation?: string; // 注解与阐释
  practicalMethods?: string[]; // 实践方法
  modernSignificance?: string; // 现代意义
  culturalValue?: string; // 文化价值
  
  // 易经特有属性
  hexagramName?: string; // 卦名
  hexagramSymbol?: string; // 卦象
  hexagramNumber?: number; // 卦序
  yinYangAttributes?: Record<string, string>; // 阴阳属性
  fiveElements?: string[]; // 五行属性
  
  // 道医特有属性
  meridians?: string[]; // 相关经络
  energyPoints?: string[]; // 能量点
  qiCirculation?: string; // 气的循环
  
  // 佛医特有属性
  sutras?: string[]; // 相关经文
  meditationMethods?: string[]; // 禅修方法
  
  // 相学特有属性
  physiognomyType?: 'face' | 'palm' | 'body' | 'other'; // 相术类型
  physiognomyFeatures?: Record<string, string>; // 相学特征
  
  // 风水特有属性
  fengShuiOrientation?: string; // 方位
  fengShuiElements?: string[]; // 风水元素
  environmentalFactors?: string[]; // 环境因素
}

/**
 * 现代医学知识接口
 * 扩展基本知识接口，增加现代医学特有属性
 */
export interface IModernMedicineKnowledge extends IKnowledge {
  // 现代医学特有属性
  medicalSystem?: 'preventive' | 'sports' | 'psychology' | 'astrology' | 'integrative' | 'chronic' | 'other';
  scientificBasis?: string; // 科学依据
  researchReferences?: string[]; // 研究参考文献
  clinicalEvidence?: string; // 临床证据
  applicationScenarios?: string[]; // 应用场景
  
  // 预防医学特有属性
  preventionMethods?: string[]; // 预防方法
  riskFactors?: string[]; // 风险因素
  screeningGuidelines?: string; // 筛查指南
  
  // 运动医学特有属性
  exerciseTypes?: string[]; // 运动类型
  trainingMethods?: string[]; // 训练方法
  recoveryTechniques?: string[]; // 恢复技术
  
  // 心理学特有属性
  psychologicalTheories?: string[]; // 心理学理论
  behavioralPatterns?: string[]; // 行为模式
  mentalHealthStrategies?: string[]; // 心理健康策略
  
  // 星相学特有属性
  astrologicalSystems?: string[]; // 星相系统
  celestialInfluences?: Record<string, string>; // 天体影响
  cyclicalPatterns?: string[]; // 周期模式
  
  // 整合医学特有属性
  treatmentApproaches?: string[]; // 治疗方法
  holisticFactors?: string[]; // 整体因素
  
  // 慢性病相关属性
  diseaseManagement?: string; // 疾病管理
  lifestyleModifications?: string[]; // 生活方式调整
  monitoringParameters?: string[]; // 监测参数
}

/**
 * 扩展知识分类类型定义
 */
export type ExtendedKnowledgeType = 
  'traditional-culture/yijing' | 
  'traditional-culture/taoism' | 
  'traditional-culture/buddhism' | 
  'traditional-culture/physiognomy' | 
  'traditional-culture/fengshui' | 
  'traditional-culture/classics' |
  'modern-medicine/preventive' | 
  'modern-medicine/sports' | 
  'modern-medicine/psychology' | 
  'modern-medicine/astrology' | 
  'modern-medicine/integrative' | 
  'modern-medicine/chronic';