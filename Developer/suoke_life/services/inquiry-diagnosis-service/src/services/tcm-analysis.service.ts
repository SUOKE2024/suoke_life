import { Service } from 'typedi';
import { 
  ITCMPattern, 
  ICategorizedSymptom, 
  IConstitutionAnalysis,
  IHealthRecommendation
} from '../interfaces/diagnosis.interface';
import { KnowledgeGraphService } from '../integrations/knowledge-graph.service';
import { HealthProfileService } from '../integrations/health-profile.service';
import { logger } from '../utils/logger';

/**
 * 中医分析服务
 * 提供中医辨证、症状分类、体质分析等功能
 */
@Service()
export class TCMAnalysisService {
  constructor(
    private knowledgeGraphService: KnowledgeGraphService,
    private healthProfileService: HealthProfileService
  ) {}
  
  /**
   * 中医辨证分析
   * @param symptoms 症状数组
   * @param userId 用户ID (可选)
   * @returns 辨证结果
   */
  async performPatternDifferentiation(
    symptoms: string[], 
    userId?: string
  ): Promise<ITCMPattern[]> {
    try {
      logger.info('开始中医辨证分析', { symptoms, userId });
      
      // 利用知识图谱服务查询相关模式
      const patterns = await this.knowledgeGraphService.findTCMPatternsForSymptoms(symptoms);
      
      // 如果提供了用户ID，尝试从健康画像获取用户体质信息辅助辨证
      let userConstitution = null;
      if (userId) {
        try {
          userConstitution = await this.healthProfileService.getUserConstitution(userId);
        } catch (error) {
          logger.warn('获取用户体质信息失败，将使用症状进行辨证', { userId, error: error.message });
        }
      }
      
      // 根据用户体质信息调整辨证结果的可信度
      if (userConstitution) {
        // 调整算法实现...
      }
      
      // 确保结果格式统一
      const formattedPatterns = patterns.map(p => ({
        name: p.name,
        confidence: p.confidence,
        description: p.description || '',
        symptoms: p.relatedSymptoms || []
      }));
      
      // 按可信度排序
      return formattedPatterns.sort((a, b) => b.confidence - a.confidence);
    } catch (error) {
      logger.error('中医辨证分析失败', { error: error.message, symptoms });
      return [];
    }
  }
  
  /**
   * 症状分类
   * @param symptoms 症状数组
   * @returns 分类后的症状
   */
  async categorizeSymptoms(symptoms: string[]): Promise<ICategorizedSymptom[]> {
    try {
      logger.info('开始症状分类', { symptoms });
      
      // 中医症状分类类别
      const categories = [
        '头面', '眼', '耳', '鼻', '口咽', '颈项', '胸', '腹', '腰背', 
        '四肢', '皮肤', '睡眠', '情志', '饮食', '二便', '女性', '其他'
      ];
      
      // 初始化分类结果
      const categorized: Record<string, string[]> = {};
      categories.forEach(category => {
        categorized[category] = [];
      });
      
      // 对每个症状进行分类
      for (const symptom of symptoms) {
        // 使用知识图谱服务查询症状类别
        const category = await this.knowledgeGraphService.findSymptomCategory(symptom);
        if (category && categorized[category]) {
          categorized[category].push(symptom);
        } else {
          categorized['其他'].push(symptom);
        }
      }
      
      // 转换成接口要求的格式并过滤空类别
      return Object.entries(categorized)
        .filter(([_, symptoms]) => symptoms.length > 0)
        .map(([category, symptoms]) => ({
          category,
          symptoms
        }));
    } catch (error) {
      logger.error('症状分类失败', { error: error.message, symptoms });
      return [{ category: '其他', symptoms }];
    }
  }
  
  /**
   * 体质分析
   * @param symptoms 症状数组
   * @param patientInfo 患者信息
   * @param userId 用户ID (可选)
   * @returns 体质分析结果
   */
  async analyzeConstitution(
    symptoms: string[], 
    patientInfo: any,
    userId?: string
  ): Promise<IConstitutionAnalysis> {
    try {
      logger.info('开始体质分析', { symptoms, userId });
      
      // 中医九种体质
      const constitutions = [
        '平和质', '气虚质', '阳虚质', '阴虚质', 
        '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质'
      ];
      
      // 尝试从健康画像获取用户历史体质信息
      let historicalConstitution = null;
      if (userId) {
        try {
          historicalConstitution = await this.healthProfileService.getUserConstitution(userId);
        } catch (error) {
          logger.warn('获取用户历史体质信息失败', { userId, error: error.message });
        }
      }
      
      // 计算各体质得分
      const scores: Record<string, number> = {};
      constitutions.forEach(c => scores[c] = 0);
      
      // 结合症状和历史体质进行评分
      await Promise.all(symptoms.map(async (symptom) => {
        const relatedConstitutions = await this.knowledgeGraphService.findConstitutionsForSymptom(symptom);
        relatedConstitutions.forEach(rc => {
          scores[rc.name] = (scores[rc.name] || 0) + rc.weight;
        });
      }));
      
      // 如果有历史体质信息，增加权重
      if (historicalConstitution && historicalConstitution.primaryType) {
        scores[historicalConstitution.primaryType] += 0.2;
        historicalConstitution.secondaryTypes?.forEach(type => {
          scores[type] += 0.1;
        });
      }
      
      // 根据患者信息调整体质评分
      this.adjustScoresByPatientInfo(scores, patientInfo);
      
      // 找出主要体质和次要体质
      const sortedConstitutions = Object.entries(scores)
        .sort(([_, scoreA], [__, scoreB]) => scoreB - scoreA);
      
      const primaryType = sortedConstitutions[0][0];
      const secondaryTypes = sortedConstitutions
        .slice(1, 3)
        .filter(([_, score]) => score > 0)
        .map(([name]) => name);
      
      // 获取体质描述
      const description = await this.knowledgeGraphService.getConstitutionDescription(primaryType);
      
      return {
        primaryType,
        secondaryTypes,
        description,
        constitutionScore: scores
      };
    } catch (error) {
      logger.error('体质分析失败', { error: error.message, symptoms });
      // 返回默认体质分析结果
      return {
        primaryType: '气虚质',
        secondaryTypes: [],
        description: '无法完成体质分析',
        constitutionScore: { '气虚质': 1 }
      };
    }
  }
  
  /**
   * 根据体质生成健康调理建议
   * @param constitutionAnalysis 体质分析结果
   * @param preferredCategories 偏好的建议类别
   * @returns 健康调理建议
   */
  async generateRecommendations(
    constitutionAnalysis: IConstitutionAnalysis,
    preferredCategories?: string[]
  ): Promise<IHealthRecommendation[]> {
    try {
      logger.info('开始生成健康调理建议', { 
        constitution: constitutionAnalysis.primaryType,
        preferredCategories 
      });
      
      // 所有可能的建议类别
      const allCategories = ['diet', 'lifestyle', 'exercise', 'herbs', 'acupuncture', 'general'];
      
      // 确定需要查询的类别
      const categoriesToQuery = preferredCategories?.includes('all') || !preferredCategories 
        ? allCategories 
        : preferredCategories.filter(c => allCategories.includes(c));
      
      // 查询建议
      const recommendations: IHealthRecommendation[] = [];
      
      for (const category of categoriesToQuery) {
        const categoryRecs = await this.knowledgeGraphService.getRecommendationsForConstitution(
          constitutionAnalysis.primaryType,
          category as any
        );
        
        recommendations.push(...categoryRecs);
      }
      
      // 如果结果为空，添加一个通用建议
      if (recommendations.length === 0) {
        recommendations.push({
          category: 'general',
          content: '根据体质特点，建议保持规律作息，均衡饮食，适当运动。',
          importance: 'medium'
        });
      }
      
      return recommendations;
    } catch (error) {
      logger.error('生成健康调理建议失败', { 
        error: error.message, 
        constitution: constitutionAnalysis.primaryType 
      });
      
      // 返回默认建议
      return [{
        category: 'general',
        content: '建议保持规律作息，均衡饮食，适当运动。',
        importance: 'medium'
      }];
    }
  }
  
  /**
   * 根据患者信息调整体质评分
   * @param scores 体质评分
   * @param patientInfo 患者信息
   */
  private adjustScoresByPatientInfo(scores: Record<string, number>, patientInfo: any): void {
    if (!patientInfo) return;
    
    // 年龄因素
    if (patientInfo.age) {
      const age = patientInfo.age;
      if (age > 60) {
        scores['气虚质'] += 0.1;
        scores['阳虚质'] += 0.1;
      } else if (age < 18) {
        scores['平和质'] += 0.1;
      }
    }
    
    // 性别因素
    if (patientInfo.gender) {
      if (patientInfo.gender === 'female') {
        scores['血瘀质'] += 0.05;
        scores['阴虚质'] += 0.05;
      }
    }
    
    // 其他调整因素...
  }
} 