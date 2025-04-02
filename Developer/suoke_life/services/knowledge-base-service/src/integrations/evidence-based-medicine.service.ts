/**
 * 循证医学服务
 * 提供医学研究证据的等级分类和评估系统
 */

import { injectable, inject } from 'inversify';
import axios from 'axios';
import { Logger } from '../utils/logger';
import { ConfigService } from '../utils/config.service';
import { TYPES } from '../types';

/**
 * 证据等级定义
 */
export enum EvidenceLevel {
  LEVEL_1A = '1a', // 系统综述和多个随机对照实验的荟萃分析
  LEVEL_1B = '1b', // 单个高质量随机对照实验
  LEVEL_2A = '2a', // 系统综述和多个队列研究
  LEVEL_2B = '2b', // 单个队列研究或低质量随机对照实验
  LEVEL_3A = '3a', // 系统综述和多个病例对照研究
  LEVEL_3B = '3b', // 单个病例对照研究
  LEVEL_4 = '4',   // 病例系列或低质量队列或病例对照研究
  LEVEL_5 = '5'    // 专家意见或基于病理生理学的推理
}

/**
 * 推荐强度定义
 */
export enum RecommendationStrength {
  STRONG_FOR = 'A',    // 强烈推荐使用
  CONDITIONAL_FOR = 'B', // 有条件推荐使用
  CONDITIONAL_AGAINST = 'C', // 有条件推荐不使用
  STRONG_AGAINST = 'D'  // 强烈推荐不使用
}

/**
 * 证据评估结果
 */
export interface EvidenceAssessment {
  evidenceLevel: EvidenceLevel;
  recommendationStrength: RecommendationStrength;
  confidenceScore: number; // 0-100
  consistency: 'high' | 'moderate' | 'low';
  applicability: 'direct' | 'moderate' | 'indirect';
  imprecision: 'precise' | 'moderate' | 'imprecise';
  publicationBias: 'unlikely' | 'possible' | 'likely';
  comments?: string;
}

/**
 * 研究引用接口
 */
export interface ResearchCitation {
  id: string;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  doi?: string;
  pmid?: string;
  url?: string;
  studyType: string;
  sampleSize?: number;
  evidenceLevel: EvidenceLevel;
  keyFindings: string;
}

@injectable()
export class EvidenceBasedMedicineService {
  private logger = new Logger('EvidenceBasedMedicineService');
  private webSearchServiceUrl: string;
  private ragServiceUrl: string;

  constructor(
    @inject(TYPES.ConfigService) private configService: ConfigService
  ) {
    this.webSearchServiceUrl = this.configService.get('services.webSearchService');
    this.ragServiceUrl = this.configService.get('services.ragService');
  }

  /**
   * 评估医学证据
   * @param citations 研究引用列表
   */
  async assessEvidence(citations: ResearchCitation[]): Promise<EvidenceAssessment> {
    try {
      this.logger.info('Assessing medical evidence');
      
      if (!citations || citations.length === 0) {
        throw new Error('No citations provided for assessment');
      }
      
      // 确定证据等级
      const evidenceLevel = this.determineEvidenceLevel(citations);
      
      // 计算置信度
      const confidenceScore = this.calculateConfidenceScore(citations);
      
      // 确定推荐强度
      const recommendationStrength = this.determineRecommendationStrength(evidenceLevel, confidenceScore);
      
      // 评估一致性
      const consistency = this.evaluateConsistency(citations);
      
      // 评估适用性
      const applicability = this.evaluateApplicability(citations);
      
      // 评估不精确性
      const imprecision = this.evaluateImprecision(citations);
      
      // 评估发表偏倚
      const publicationBias = this.evaluatePublicationBias(citations);
      
      return {
        evidenceLevel,
        recommendationStrength,
        confidenceScore,
        consistency,
        applicability,
        imprecision,
        publicationBias
      };
    } catch (error) {
      this.logger.error('Failed to assess evidence', error);
      throw new Error('Failed to assess evidence');
    }
  }

  /**
   * 搜索最新医学研究
   * @param topic 主题
   * @param limit 结果数量限制
   */
  async searchLatestResearch(topic: string, limit: number = 10): Promise<ResearchCitation[]> {
    try {
      this.logger.info(`Searching latest research for topic: ${topic}`);
      
      const response = await axios.get(`${this.webSearchServiceUrl}/api/research`, {
        params: {
          topic,
          limit
        }
      });
      
      return response.data.map((item: any) => ({
        id: item.id,
        title: item.title,
        authors: item.authors,
        journal: item.journal,
        year: item.year,
        doi: item.doi,
        pmid: item.pmid,
        url: item.url,
        studyType: item.studyType,
        sampleSize: item.sampleSize,
        evidenceLevel: this.mapExternalEvidenceLevel(item.evidenceLevel),
        keyFindings: item.keyFindings
      }));
    } catch (error) {
      this.logger.error(`Failed to search latest research for topic: ${topic}`, error);
      throw new Error('Failed to search latest research');
    }
  }

  /**
   * 获取医学指南
   * @param condition 健康状况
   */
  async getMedicalGuidelines(condition: string): Promise<any> {
    try {
      this.logger.info(`Getting medical guidelines for: ${condition}`);
      
      const response = await axios.get(`${this.webSearchServiceUrl}/api/guidelines`, {
        params: {
          condition
        }
      });
      
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get medical guidelines for: ${condition}`, error);
      throw new Error('Failed to get medical guidelines');
    }
  }

  /**
   * 使用RAG服务分析和解释医学研究
   * @param researchText 研究文本
   */
  async analyzeResearchWithRAG(researchText: string): Promise<any> {
    try {
      this.logger.info('Analyzing research with RAG');
      
      const response = await axios.post(`${this.ragServiceUrl}/api/analyze/research`, {
        researchText
      });
      
      return response.data;
    } catch (error) {
      this.logger.error('Failed to analyze research with RAG', error);
      throw new Error('Failed to analyze research with RAG');
    }
  }

  /**
   * 确定证据等级
   * @param citations 研究引用列表
   */
  private determineEvidenceLevel(citations: ResearchCitation[]): EvidenceLevel {
    // 找出最高级别的证据
    const levels = citations.map(c => c.evidenceLevel);
    
    if (levels.includes(EvidenceLevel.LEVEL_1A)) {
      return EvidenceLevel.LEVEL_1A;
    } else if (levels.includes(EvidenceLevel.LEVEL_1B)) {
      return EvidenceLevel.LEVEL_1B;
    } else if (levels.includes(EvidenceLevel.LEVEL_2A)) {
      return EvidenceLevel.LEVEL_2A;
    } else if (levels.includes(EvidenceLevel.LEVEL_2B)) {
      return EvidenceLevel.LEVEL_2B;
    } else if (levels.includes(EvidenceLevel.LEVEL_3A)) {
      return EvidenceLevel.LEVEL_3A;
    } else if (levels.includes(EvidenceLevel.LEVEL_3B)) {
      return EvidenceLevel.LEVEL_3B;
    } else if (levels.includes(EvidenceLevel.LEVEL_4)) {
      return EvidenceLevel.LEVEL_4;
    } else {
      return EvidenceLevel.LEVEL_5;
    }
  }

  /**
   * 计算置信度得分
   * @param citations 研究引用列表
   */
  private calculateConfidenceScore(citations: ResearchCitation[]): number {
    // 基于研究类型、样本量和证据等级计算置信度
    let totalScore = 0;
    
    for (const citation of citations) {
      let citationScore = 0;
      
      // 基于证据等级的得分
      switch (citation.evidenceLevel) {
        case EvidenceLevel.LEVEL_1A:
          citationScore += 50;
          break;
        case EvidenceLevel.LEVEL_1B:
          citationScore += 40;
          break;
        case EvidenceLevel.LEVEL_2A:
          citationScore += 30;
          break;
        case EvidenceLevel.LEVEL_2B:
          citationScore += 25;
          break;
        case EvidenceLevel.LEVEL_3A:
          citationScore += 20;
          break;
        case EvidenceLevel.LEVEL_3B:
          citationScore += 15;
          break;
        case EvidenceLevel.LEVEL_4:
          citationScore += 10;
          break;
        case EvidenceLevel.LEVEL_5:
          citationScore += 5;
          break;
      }
      
      // 基于样本量的额外得分
      if (citation.sampleSize) {
        if (citation.sampleSize > 10000) {
          citationScore += 20;
        } else if (citation.sampleSize > 1000) {
          citationScore += 15;
        } else if (citation.sampleSize > 100) {
          citationScore += 10;
        } else if (citation.sampleSize > 10) {
          citationScore += 5;
        }
      }
      
      // 近期研究加分
      const currentYear = new Date().getFullYear();
      if (citation.year >= currentYear - 1) {
        citationScore += 10;
      } else if (citation.year >= currentYear - 3) {
        citationScore += 5;
      } else if (citation.year >= currentYear - 5) {
        citationScore += 2;
      }
      
      totalScore += citationScore;
    }
    
    // 归一化到0-100
    const normalizedScore = Math.min(100, Math.round(totalScore / citations.length));
    return normalizedScore;
  }

  /**
   * 确定推荐强度
   * @param evidenceLevel 证据等级
   * @param confidenceScore 置信度得分
   */
  private determineRecommendationStrength(evidenceLevel: EvidenceLevel, confidenceScore: number): RecommendationStrength {
    // 根据证据等级和置信度确定推荐强度
    if ((evidenceLevel === EvidenceLevel.LEVEL_1A || evidenceLevel === EvidenceLevel.LEVEL_1B) && confidenceScore >= 80) {
      return RecommendationStrength.STRONG_FOR;
    } else if ((evidenceLevel === EvidenceLevel.LEVEL_1A || evidenceLevel === EvidenceLevel.LEVEL_1B || 
               evidenceLevel === EvidenceLevel.LEVEL_2A || evidenceLevel === EvidenceLevel.LEVEL_2B) && 
               confidenceScore >= 60) {
      return RecommendationStrength.CONDITIONAL_FOR;
    } else if (confidenceScore < 40) {
      return RecommendationStrength.STRONG_AGAINST;
    } else {
      return RecommendationStrength.CONDITIONAL_AGAINST;
    }
  }

  /**
   * 评估研究一致性
   * @param citations 研究引用列表
   */
  private evaluateConsistency(citations: ResearchCitation[]): 'high' | 'moderate' | 'low' {
    // 简化实现，实际上需要分析研究结果的一致性
    if (citations.length <= 2) {
      return 'low';
    } else if (citations.length <= 5) {
      return 'moderate';
    } else {
      return 'high';
    }
  }

  /**
   * 评估研究适用性
   * @param citations 研究引用列表
   */
  private evaluateApplicability(citations: ResearchCitation[]): 'direct' | 'moderate' | 'indirect' {
    // 简化实现，实际上需要分析研究人群与目标人群的相似性
    return 'moderate';
  }

  /**
   * 评估研究精确性
   * @param citations 研究引用列表
   */
  private evaluateImprecision(citations: ResearchCitation[]): 'precise' | 'moderate' | 'imprecise' {
    // 简化实现，实际上需要分析样本量和置信区间
    let hasLargeSample = false;
    
    for (const citation of citations) {
      if (citation.sampleSize && citation.sampleSize > 1000) {
        hasLargeSample = true;
        break;
      }
    }
    
    if (hasLargeSample) {
      return 'precise';
    } else if (citations.length > 3) {
      return 'moderate';
    } else {
      return 'imprecise';
    }
  }

  /**
   * 评估发表偏倚
   * @param citations 研究引用列表
   */
  private evaluatePublicationBias(citations: ResearchCitation[]): 'unlikely' | 'possible' | 'likely' {
    // 简化实现，实际上需要分析漏斗图等
    if (citations.length > 10) {
      return 'unlikely';
    } else if (citations.length > 5) {
      return 'possible';
    } else {
      return 'likely';
    }
  }

  /**
   * 映射外部证据等级到内部等级
   * @param externalLevel 外部证据等级
   */
  private mapExternalEvidenceLevel(externalLevel: string): EvidenceLevel {
    // 映射外部API的证据等级到内部定义
    const mapping: Record<string, EvidenceLevel> = {
      'I-A': EvidenceLevel.LEVEL_1A,
      'I-B': EvidenceLevel.LEVEL_1B,
      'II-A': EvidenceLevel.LEVEL_2A,
      'II-B': EvidenceLevel.LEVEL_2B,
      'III-A': EvidenceLevel.LEVEL_3A,
      'III-B': EvidenceLevel.LEVEL_3B,
      'IV': EvidenceLevel.LEVEL_4,
      'V': EvidenceLevel.LEVEL_5,
      'Meta-analysis': EvidenceLevel.LEVEL_1A,
      'RCT': EvidenceLevel.LEVEL_1B,
      'Cohort': EvidenceLevel.LEVEL_2B,
      'Case-control': EvidenceLevel.LEVEL_3B,
      'Case series': EvidenceLevel.LEVEL_4,
      'Expert opinion': EvidenceLevel.LEVEL_5
    };
    
    return mapping[externalLevel] || EvidenceLevel.LEVEL_5;
  }
}