import {
  Constitution,
  HealthRecommendation,
  medKnowledgeService,
  Symptom,
} from '../../services/medKnowledgeService';

/**
 * 老克智能体医疗知识集成模块
 * 负责将医疗知识服务与老克的中医诊断能力结合
 */
export class LaokeKnowledgeIntegration {
  private static instance: LaokeKnowledgeIntegration;

  private constructor() {}

  public static getInstance(): LaokeKnowledgeIntegration {
    if (!LaokeKnowledgeIntegration.instance) {
      LaokeKnowledgeIntegration.instance = new LaokeKnowledgeIntegration();
    }
    return LaokeKnowledgeIntegration.instance;
  }

  /**
   * 基于症状分析推荐相关体质
   */
  async analyzeConstitutionBySymptoms(symptoms: string[]): Promise<{
    constitutions: Constitution[];
    confidence: number;
    reasoning: string;
  }> {
    try {
      // 获取所有体质信息
      const allConstitutions = await medKnowledgeService.getConstitutions();

      // 分析症状与体质的匹配度
      const matches = allConstitutions.map((constitution) => {
        const matchingSymptoms = symptoms.filter((symptom) =>
          constitution.symptoms.some(
            (cs) =>
              cs.toLowerCase().includes(symptom.toLowerCase()) ||
              symptom.toLowerCase().includes(cs.toLowerCase())
          )
        );

        const confidence = matchingSymptoms.length / symptoms.length;
        return {
          constitution,
          confidence,
          matchingSymptoms,
        };
      });

      // 按匹配度排序，取前3个
      const topMatches = matches
        .filter((match) => match.confidence > 0.1)
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, 3);

      const overallConfidence =
        topMatches.length > 0 ? topMatches[0].confidence : 0;
      const reasoning = this.generateConstitutionReasoning(
        symptoms,
        topMatches
      );

      return {
        constitutions: topMatches.map((match) => match.constitution),
        confidence: overallConfidence,
        reasoning,
      };
    } catch (error) {
      console.error('Failed to analyze constitution by symptoms:', error);
      throw new Error('体质分析失败');
    }
  }

  /**
   * 基于体质获取个性化健康建议
   */
  async getPersonalizedAdvice(
    constitutionId: string,
    userContext: {
      age?: number;
      gender?: string;
      currentSymptoms?: string[];
      lifestyle?: string[];
    }
  ): Promise<{
    recommendations: HealthRecommendation[];
    constitution: Constitution;
    customAdvice: string;
  }> {
    try {
      // 获取体质详情
      const constitution =
        await medKnowledgeService.getConstitutionById(constitutionId);

      // 获取个性化推荐
      const recommendations =
        await medKnowledgeService.getPersonalizedRecommendations({
          userId: 'current_user', // 实际应用中应该是真实用户ID
          constitution_id: constitutionId,
          symptoms: userContext.currentSymptoms,
          preferences: {
            treatment_type: 'traditional',
            lifestyle_focus: userContext.lifestyle,
          },
        });

      // 生成定制化建议
      const customAdvice = this.generateCustomAdvice(constitution, userContext);

      return {
        recommendations,
        constitution,
        customAdvice,
      };
    } catch (error) {
      console.error('Failed to get personalized advice:', error);
      throw new Error('获取个性化建议失败');
    }
  }

  /**
   * 智能症状搜索和分析
   */
  async intelligentSymptomSearch(symptomDescription: string): Promise<{
    symptoms: Symptom[];
    relatedConstitutions: Constitution[];
    suggestedTreatments: string[];
    tcmAnalysis: string;
  }> {
    try {
      // 搜索相关症状
      const symptoms =
        await medKnowledgeService.searchSymptoms(symptomDescription);

      // 基于症状分析体质
      const constitutionAnalysis = await this.analyzeConstitutionBySymptoms(
        symptoms.map((s) => s.name)
      );

      // 获取治疗建议
      const suggestedTreatments = this.extractTreatmentSuggestions(symptoms);

      // 生成中医分析
      const tcmAnalysis = this.generateTCMAnalysis(
        symptoms,
        constitutionAnalysis.constitutions
      );

      return {
        symptoms,
        relatedConstitutions: constitutionAnalysis.constitutions,
        suggestedTreatments,
        tcmAnalysis,
      };
    } catch (error) {
      console.error('Failed to perform intelligent symptom search:', error);
      throw new Error('智能症状搜索失败');
    }
  }

  /**
   * 知识图谱查询和推理
   */
  async queryKnowledgeGraph(query: {
    entityType: string;
    entityId: string;
    relationshipType?: string;
    depth?: number;
  }): Promise<{
    entity: any;
    relationships: any[];
    insights: string[];
  }> {
    try {
      // 获取实体关系
      const relationships = await medKnowledgeService.getEntityRelationships(
        query.entityType,
        query.entityId
      );

      // 获取相邻实体
      const neighbors = await medKnowledgeService.getEntityNeighbors(
        query.entityType,
        query.entityId
      );

      // 生成洞察
      const insights = this.generateGraphInsights(relationships, neighbors);

      return {
        entity: { type: query.entityType, id: query.entityId },
        relationships: relationships.concat(neighbors),
        insights,
      };
    } catch (error) {
      console.error('Failed to query knowledge graph:', error);
      throw new Error('知识图谱查询失败');
    }
  }

  /**
   * 综合健康评估
   */
  async comprehensiveHealthAssessment(assessmentData: {
    symptoms: string[];
    constitution?: string;
    lifestyle: {
      diet: string[];
      exercise: string[];
      sleep: string;
      stress: string;
    };
    demographics: {
      age: number;
      gender: string;
    };
  }): Promise<{
    overallScore: number;
    riskFactors: string[];
    recommendations: HealthRecommendation[];
    preventiveActions: string[];
    followUpPlan: string;
  }> {
    try {
      // 分析症状
      const symptomAnalysis = await this.intelligentSymptomSearch(
        assessmentData.symptoms.join(', ')
      );

      // 体质分析
      let constitutionAnalysis;
      if (assessmentData.constitution) {
        constitutionAnalysis = await this.getPersonalizedAdvice(
          assessmentData.constitution,
          {
            age: assessmentData.demographics.age,
            gender: assessmentData.demographics.gender,
            currentSymptoms: assessmentData.symptoms,
            lifestyle: assessmentData.lifestyle.diet.concat(
              assessmentData.lifestyle.exercise
            ),
          }
        );
      } else {
        constitutionAnalysis = await this.analyzeConstitutionBySymptoms(
          assessmentData.symptoms
        );
      }

      // 计算综合评分
      const overallScore = this.calculateHealthScore(
        assessmentData,
        symptomAnalysis
      );

      // 识别风险因素
      const riskFactors = this.identifyRiskFactors(
        assessmentData,
        symptomAnalysis
      );

      // 生成预防措施
      const preventiveActions = this.generatePreventiveActions(
        assessmentData,
        constitutionAnalysis
      );

      // 制定随访计划
      const followUpPlan = this.createFollowUpPlan(overallScore, riskFactors);

      return {
        overallScore,
        riskFactors,
        recommendations: constitutionAnalysis.recommendations || [],
        preventiveActions,
        followUpPlan,
      };
    } catch (error) {
      console.error(
        'Failed to perform comprehensive health assessment:',
        error
      );
      throw new Error('综合健康评估失败');
    }
  }

  // 私有辅助方法
  private generateConstitutionReasoning(
    symptoms: string[],
    matches: any[]
  ): string {
    if (matches.length === 0) {
      return '基于提供的症状，暂时无法确定明确的体质类型，建议进一步详细问诊。';
    }

    const topMatch = matches[0];
    return `基于症状分析，您可能属于${topMatch.constitution.name}体质，匹配度为${(topMatch.confidence * 100).toFixed(1)}%。主要依据是您的症状与该体质的典型表现相符。`;
  }

  private generateCustomAdvice(
    constitution: Constitution,
    userContext: any
  ): string {
    return `根据您的${constitution.name}体质特点，建议您在日常生活中注意调理，保持身心平衡。`;
  }

  private extractTreatmentSuggestions(symptoms: Symptom[]): string[] {
    return symptoms.flatMap((symptom) => symptom.treatments || []).slice(0, 5);
  }

  private generateTCMAnalysis(
    symptoms: Symptom[],
    constitutions: Constitution[]
  ): string {
    return `从中医角度分析，您的症状表现符合${constitutions.map((c) => c.name).join('、')}的特征，建议采用相应的调理方法。`;
  }

  private generateGraphInsights(
    relationships: any[],
    neighbors: any[]
  ): string[] {
    return [
      '基于知识图谱分析，发现了相关的医学概念关联',
      '建议关注相关的健康指标变化',
      '可以考虑相关的预防措施',
    ];
  }

  private calculateHealthScore(
    assessmentData: any,
    symptomAnalysis: any
  ): number {
    // 简化的健康评分算法
    let score = 100;

    // 根据症状数量扣分
    score -= assessmentData.symptoms.length * 5;

    // 根据生活方式调整
    if (assessmentData.lifestyle.exercise.length > 0) {
      score += 10;
    }

    return Math.max(0, Math.min(100, score));
  }

  private identifyRiskFactors(
    assessmentData: any,
    symptomAnalysis: any
  ): string[] {
    const riskFactors: string[] = [];

    if (assessmentData.symptoms.length > 3) {
      riskFactors.push('症状较多，需要关注');
    }

    if (assessmentData.lifestyle.stress === 'high') {
      riskFactors.push('压力水平较高');
    }

    return riskFactors;
  }

  private generatePreventiveActions(
    assessmentData: any,
    constitutionAnalysis: any
  ): string[] {
    return ['保持规律作息', '适当运动锻炼', '均衡饮食营养', '定期健康检查'];
  }

  private createFollowUpPlan(
    overallScore: number,
    riskFactors: string[]
  ): string {
    if (overallScore >= 80) {
      return '建议3个月后复查，继续保持良好的生活习惯。';
    } else if (overallScore >= 60) {
      return '建议1个月后复查，注意改善生活方式。';
    } else {
      return '建议2周后复查，必要时寻求专业医疗建议。';
    }
  }
}

// 导出单例实例
export const laokeKnowledgeIntegration =
  LaokeKnowledgeIntegration.getInstance();
