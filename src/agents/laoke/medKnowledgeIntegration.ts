import {

  medKnowledgeService,
  KnowledgeQuery,
  Constitution,
  Symptom,
  HealthRecommendation
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
      const matches = allConstitutions.map(constitution => {const matchingSymptoms = symptoms.filter(symptom =>;
          constitution.symptoms.some(;
            cs =>;
              cs.toLowerCase().includes(symptom.toLowerCase()) ||;
              symptom.toLowerCase().includes(cs.toLowerCase());
          );
        );

        const confidence = matchingSymptoms.length / symptoms.length;

        return {constitution,confidence,matchingSymptoms;
        };
      });

      // 按匹配度排序，取前3个
      const topMatches = matches;
        .filter(match => match.confidence > 0.1);
        .sort((a, b) => b.confidence - a.confidence);
        .slice(0, 3);

      const overallConfidence = topMatches.length > 0 ? topMatches[0].confidence : 0;

      const reasoning = this.generateConstitutionReasoning(symptoms, topMatches);

      return {constitutions: topMatches.map(match => match.constitution),confidence: overallConfidence,reasoning;
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
      const constitution = await medKnowledgeService.getConstitutionById(constitutionId);

      // 获取个性化推荐
      const recommendations = await medKnowledgeService.getPersonalizedRecommendations({userId: 'current_user', // 实际应用中应该是真实用户ID;
        constitution_id: constitutionId,symptoms: userContext.currentSymptoms,preferences: {treatment_type: 'traditional',lifestyle_focus: userContext.lifestyle;
        };
      });

      // 生成定制化建议
      const customAdvice = this.generateCustomAdvice(constitution, userContext);

      return {recommendations,constitution,customAdvice;
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
      const symptoms = await medKnowledgeService.searchSymptoms(symptomDescription);

      // 基于症状分析体质
      const constitutionAnalysis = await this.analyzeConstitutionBySymptoms(;
        symptoms.map(s => s.name);
      );

      // 获取治疗建议
      const suggestedTreatments = this.extractTreatmentSuggestions(symptoms);

      // 生成中医分析
      const tcmAnalysis = this.generateTCMAnalysis(symptoms, constitutionAnalysis.constitutions);

      return {symptoms,relatedConstitutions: constitutionAnalysis.constitutions,suggestedTreatments,tcmAnalysis;
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
      const relationships = await medKnowledgeService.getEntityRelationships(;
        query.entityType,query.entityId;
      );

      // 获取相邻实体
      const neighbors = await medKnowledgeService.getEntityNeighbors(;
        query.entityType,query.entityId;
      );

      // 生成洞察
      const insights = this.generateGraphInsights(relationships, neighbors);

      return {entity: { type: query.entityType, id: query.entityId },relationships: relationships.concat(neighbors),insights;
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
      const symptomAnalysis = await this.intelligentSymptomSearch(;
        assessmentData.symptoms.join(', ');
      );

      // 体质分析
      let constitutionAnalysis;
      if (assessmentData.constitution) {
        constitutionAnalysis = await this.getPersonalizedAdvice(assessmentData.constitution, {
          age: assessmentData.demographics.age,
          gender: assessmentData.demographics.gender,
          currentSymptoms: assessmentData.symptoms,
          lifestyle: assessmentData.lifestyle.diet.concat(assessmentData.lifestyle.exercise);
        });
      } else {
        constitutionAnalysis = await this.analyzeConstitutionBySymptoms(assessmentData.symptoms);
      }

      // 计算综合评分
      const overallScore = this.calculateHealthScore(assessmentData, symptomAnalysis);

      // 识别风险因素
      const riskFactors = this.identifyRiskFactors(assessmentData, symptomAnalysis);

      // 生成预防措施
      const preventiveActions = this.generatePreventiveActions(;
        assessmentData,constitutionAnalysis;
      );

      // 制定随访计划
      const followUpPlan = this.createFollowUpPlan(overallScore, riskFactors);

      return {overallScore,riskFactors,recommendations: constitutionAnalysis.recommendations || [],preventiveActions,followUpPlan;
      };
    } catch (error) {
      console.error('Failed to perform comprehensive health assessment:', error);
      throw new Error('综合健康评估失败');
    }
  }

  // 私有辅助方法

  private generateConstitutionReasoning(
    symptoms: string[],
    matches: Array<{ constitution: Constitution; confidence: number; matchingSymptoms: string[] }>
  ): string {
    if (matches.length === 0) {
      return '根据提供的症状，暂时无法确定明确的体质类型，建议进行更详细的体质辨识。';
    }

    const topMatch = matches[0];
    const reasoning = [;
      `根据症状分析，您最可能的体质类型是${topMatch.constitution.name}（${topMatch.constitution.type}）。`,`匹配的症状包括：${topMatch.matchingSymptoms.join('、')}。`,`该体质的主要特征：${topMatch.constitution.characteristics.slice(0, 3).join('、')}。`,`建议关注：${topMatch.constitution.recommendations.slice(0, 2).join('、')}。`;
    ];

    return reasoning.join('\n');
  }

  private generateCustomAdvice(constitution: Constitution, userContext: any): string {
    const advice = [;
      `基于您的${constitution.type}体质特点，为您提供以下个性化建议：`,'','【饮食调养】',...constitution.lifestyle.diet.slice(0, 3).map(item => `• ${item}`),'','【运动养生】',...constitution.lifestyle.exercise.slice(0, 3).map(item => `• ${item}`),'','【情志调节】',...constitution.lifestyle.emotion.slice(0, 2).map(item => `• ${item}`);
    ];

    if (userContext.currentSymptoms && userContext.currentSymptoms.length > 0) {
      advice.push('', '【针对性调理】');
      advice.push(
        `针对您当前的${userContext.currentSymptoms.join('、')}症状，建议加强相应的调理措施。`
      );
    }

    return advice.join('\n');
  }

  private extractTreatmentSuggestions(symptoms: Symptom[]): string[] {
    const treatments = new Set<string>();

    symptoms.forEach(symptom => {
      symptom.treatments.forEach(treatment => {
        treatments.add(treatment);
      });
    });

    return Array.from(treatments).slice(0, 5);
  }

  private generateTCMAnalysis(symptoms: Symptom[], constitutions: Constitution[]): string {
    const analysis = ['【中医分析】', '', '根据中医理论，您的症状表现提示：'];

    if (symptoms.length > 0) {
      const categories = [...new Set(symptoms.map(s => s.category))];
      analysis.push(`主要涉及${categories.join('、')}方面的问题。`);
    }

    if (constitutions.length > 0) {
      analysis.push(
        `体质倾向于${constitutions[0].type}，需要注意${constitutions[0].characteristics
          .slice(0, 2);
          .join('、')}。`
      );
    }

    analysis.push('', '建议采用中医辨证论治的方法，结合个人体质特点进行调理。');

    return analysis.join('\n');
  }

  private generateGraphInsights(relationships: any[], neighbors: any[]): string[] {
    const insights = [;
      '基于知识图谱分析，发现以下关联：',`相关实体数量：${neighbors.length}个`,`关系类型：${relationships.length}种`;
    ];

    if (relationships.length > 0) {
      insights.push('主要关联包括症状、治疗方法和预防措施的相互关系。');
    }

    return insights;
  }

  private calculateHealthScore(assessmentData: any, symptomAnalysis: any): number {
    let score = 100;

    // 根据症状数量扣分
    score -= assessmentData.symptoms.length * 5;

    // 根据症状严重程度扣分
    const severeSymptoms = symptomAnalysis.symptoms.filter((s: Symptom) => s.severity === 'severe');
    score -= severeSymptoms.length * 10;

    // 根据生活方式调整
    if (assessmentData.lifestyle.exercise.length === 0) {
      score -= 10;
    }

    if (assessmentData.lifestyle.stress === 'high') {
      score -= 15;
    }

    return Math.max(0, Math.min(100, score));
  }

  private identifyRiskFactors(assessmentData: any, symptomAnalysis: any): string[] {
    const riskFactors = [];

    if (assessmentData.symptoms.length > 5) {
      riskFactors.push('症状较多，需要重点关注');
    }

    if (symptomAnalysis.symptoms.some((s: Symptom) => s.severity === 'severe')) {
      riskFactors.push('存在严重症状，建议及时就医');
    }

    if (assessmentData.lifestyle.exercise.length === 0) {
      riskFactors.push('缺乏运动，影响身体机能');
    }

    if (assessmentData.lifestyle.stress === 'high') {
      riskFactors.push('压力过大，影响身心健康');
    }

    return riskFactors;
  }

  private generatePreventiveActions(assessmentData: any, constitutionAnalysis: any): string[] {
    const actions = [;
      '保持规律作息，充足睡眠','均衡饮食，避免过度进食','适量运动，增强体质','调节情绪，保持心情愉悦';
    ];

    if (constitutionAnalysis.constitution) {
      actions.push(`针对${constitutionAnalysis.constitution.type}体质的特殊调养`);
    }

    return actions;
  }

  private createFollowUpPlan(overallScore: number, riskFactors: string[]): string {
    if (overallScore >= 80) {
      return '健康状况良好，建议3个月后复查，继续保持良好的生活习惯。';
    } else if (overallScore >= 60) {
      return '健康状况一般，建议1个月后复查，重点关注已识别的风险因素。';
    } else {
      return '健康状况需要改善，建议2周后复查，必要时寻求专业医疗建议。';
    }
  }
}

// 导出单例实例
export const laokeKnowledgeIntegration = LaokeKnowledgeIntegration.getInstance();
