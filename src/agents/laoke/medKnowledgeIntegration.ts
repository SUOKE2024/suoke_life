import {Constitution} fromealthRecommendation,
medKnowledgeService,
}
  Symptom,};
} from "../../services/medKnowledgeService";
/* 合 */
 */
export class LaokeKnowledgeIntegration {private static instance: LaokeKnowledgeIntegration;
}
}
}
  private constructor() {}
  const public = static getInstance(): LaokeKnowledgeIntegration {if (!LaokeKnowledgeIntegration.instance) {}
      LaokeKnowledgeIntegration.instance = new LaokeKnowledgeIntegration()}
    }
    return LaokeKnowledgeIntegration.instance;
  }
  /* 质 */
   *//,/g,/;
  async: analyzeConstitutionBySymptoms(symptoms: string[]): Promise<{constitutions: Constitution[],
confidence: number,
}
    const reasoning = string}
  }> {try {}      // 获取所有体质信息
const allConstitutions = await medKnowledgeService.getConstitutions();
      // 分析症状与体质的匹配度
const  matches = useMemo(() => allConstitutions.map((constitution) => {const  matchingSymptoms = symptoms.filter((symptom) =>constitution.symptoms.some();
            (cs) =>;
cs.toLowerCase().includes(symptom.toLowerCase()) ||;
symptom.toLowerCase().includes(cs.toLowerCase());
          );
        ), []);
const confidence = matchingSymptoms.length / symptoms.length;
return {constitution}confidence,
}
          matchingSymptoms,}
        };
      });
      // 按匹配度排序，取前3个
const  topMatches = matches;
        .filter((match) => match.confidence > 0.1);
        .sort((a, b) => b.confidence - a.confidence);
        .slice(0, 3);
const  overallConfidence =;
topMatches.length > 0 ? topMatches[0].confidence : 0;
  const: reasoning = this.generateConstitutionReasoning(symptoms,);
topMatches);
      );
return {constitutions: topMatches.map((match) => match.constitution)}const confidence = overallConfidence;
}
        reasoning,}
      };
    } catch (error) {'console.error('Failed to analyze constitution by symptoms:', error);
}
}
    }
  }
  /* 议 */
   *//,/g,/;
  async: getPersonalizedAdvice(constitutionId: string,,)const userContext = {age?: numbergender?: string;
currentSymptoms?: string[];);
}
      lifestyle?: string[];)}
    });
  ): Promise<{recommendations: HealthRecommendation[]}constitution: Constitution,
}
    const customAdvice = string}
  }> {try {}      // 获取体质详情
const  constitution =;
const await = medKnowledgeService.getConstitutionById(constitutionId);
      // 获取个性化推荐
const  recommendations ='
const await = medKnowledgeService.getPersonalizedRecommendations({',)userId: 'current_user', // 实际应用中应该是真实用户ID'/constitution_id: constitutionId,,'/g,'/;
  symptoms: userContext.currentSymptoms,'
preferences: {,'treatment_type: 'traditional,)'
}
            const lifestyle_focus = userContext.lifestyle;)}
          },);
        });
      // 生成定制化建议/,/g,/;
  customAdvice: this.generateCustomAdvice(constitution, userContext);
return {recommendations}constitution,
}
        customAdvice,}
      };
    } catch (error) {'console.error('Failed to get personalized advice:', error);
}
}
    }
  }
  /* 析 */
   *//,/g,/;
  async: intelligentSymptomSearch(symptomDescription: string): Promise<{symptoms: Symptom[],
relatedConstitutions: Constitution[],
suggestedTreatments: string[],
}
    const tcmAnalysis = string}
  }> {try {}      // 搜索相关症状
const  symptoms =;
const await = medKnowledgeService.searchSymptoms(symptomDescription);
      // 基于症状分析体质
const  constitutionAnalysis = await this.analyzeConstitutionBySymptoms();
symptoms.map((s) => s.name);
      );
      // 获取治疗建议
const suggestedTreatments = this.extractTreatmentSuggestions(symptoms);
      // 生成中医分析/,/g,/;
  const: tcmAnalysis = this.generateTCMAnalysis(symptoms,);
constitutionAnalysis.constitutions);
      );
return {symptoms}const relatedConstitutions = constitutionAnalysis.constitutions;
suggestedTreatments,
}
        tcmAnalysis,}
      };
    } catch (error) {'console.error('Failed to perform intelligent symptom search:', error);
}
}
    }
  }
  /* 理 */
   *//,/g,/;
  async: queryKnowledgeGraph(query: {)}entityType: string,
const entityId = string;);
relationshipType?: string;);
}
    depth?: number;)}
  }): Promise<{entity: any}relationships: any[],
}
    const insights = string[]}
  }> {try {}      // 获取实体关系/,/g,/;
  const: relationships = await medKnowledgeService.getEntityRelationships(query.entityType,);
query.entityId);
      );
      // 获取相邻实体/,/g,/;
  const: neighbors = await medKnowledgeService.getEntityNeighbors(query.entityType,);
query.entityId);
      );
      // 生成洞察/,/g,/;
  insights: this.generateGraphInsights(relationships, neighbors);
}
      return {}
        entity: { type: query.entityType, id: query.entityId }
const relationships = relationships.concat(neighbors);
insights,
      };
    } catch (error) {'console.error('Failed to query knowledge graph:', error);
}
}
    }
  }
  /* 估 */
   *//,/g,/;
  async: comprehensiveHealthAssessment(assessmentData: {)}const symptoms = string[];
constitution?: string;
  lifestyle: {diet: string[],
exercise: string[],
sleep: string,
}
      const stress = string}
    };
demographics: {age: number,);
}
      const gender = string;)}
    };);
  }): Promise<{overallScore: number}riskFactors: string[],
recommendations: HealthRecommendation[],
preventiveActions: string[],
}
    const followUpPlan = string}
  }> {try {}      // 分析症状'/,'/g'/;
const  symptomAnalysis = await this.intelligentSymptomSearch(')'
assessmentData.symptoms.join(', ')
      );
      // 体质分析
const let = constitutionAnalysis;
if (assessmentData.constitution) {constitutionAnalysis = await this.getPersonalizedAdvice(assessmentData.constitution,)          {}            age: assessmentData.demographics.age,
gender: assessmentData.demographics.gender,
currentSymptoms: assessmentData.symptoms,);
const lifestyle = assessmentData.lifestyle.diet.concat();
assessmentData.lifestyle.exercise);
}
            )}
          }
        );
      } else {constitutionAnalysis = await this.analyzeConstitutionBySymptoms(assessmentData.symptoms)}
        )}
      }
      // 计算综合评分/,/g,/;
  const: overallScore = this.calculateHealthScore(assessmentData,);
symptomAnalysis);
      );
      // 识别风险因素/,/g,/;
  const: riskFactors = this.identifyRiskFactors(assessmentData,);
symptomAnalysis);
      );
      // 生成预防措施/,/g,/;
  const: preventiveActions = this.generatePreventiveActions(assessmentData,);
constitutionAnalysis);
      );
      // 制定随访计划/,/g,/;
  followUpPlan: this.createFollowUpPlan(overallScore, riskFactors);
return {overallScore}riskFactors,
const recommendations = constitutionAnalysis.recommendations || [];
preventiveActions,
}
        followUpPlan,}
      };
    } catch (error) {'console.error('Failed to perform comprehensive health assessment: )'';
error);
      );
}
}
    }
  }
  // 私有辅助方法
private generateConstitutionReasoning(symptoms: string[],);
const matches = any[]);
  ): string {if (matches.length === 0) {}
}
    }
    const topMatch = matches[0];
return `基于症状分析，您可能属于${topMatch.constitution.name}体质，匹配度为${(topMatch.confidence * 100).toFixed(1)}%。主要依据是您的症状与该体质的典型表现相符。`;````;```;
  }
  private generateCustomAdvice(constitution: Constitution,);
const userContext = any);
  ): string {}
}
  }
  private extractTreatmentSuggestions(symptoms: Symptom[]): string[] {}
    return symptoms.flatMap((symptom) => symptom.treatments || []).slice(0, 5)}
  }
  private generateTCMAnalysis(symptoms: Symptom[],);
const constitutions = Constitution[]);
  ): string {}
}
  }
  private generateGraphInsights(relationships: any[],);
const neighbors = any[]);
  ): string[] {}return [;]}
];
    ]}
  }
  private calculateHealthScore(assessmentData: any,);
const symptomAnalysis = any);
  ): number {// 简化的健康评分算法/let score = 100;/g/;
    // 根据症状数量扣分
score -= assessmentData.symptoms.length * 5;
    // 根据生活方式调整
if (assessmentData.lifestyle.exercise.length > 0) {}
      score += 10}
    }
    return Math.max(0, Math.min(100, score));
  }
  private identifyRiskFactors(assessmentData: any,);
const symptomAnalysis = any);
  ): string[] {const riskFactors: string[] = []if (assessmentData.symptoms.length > 3) {}
}
    }
if (assessmentData.lifestyle.stress === 'high') {';}}'';
}
    }
    return riskFactors;
  }
  private generatePreventiveActions(assessmentData: any,);
const constitutionAnalysis = any);
  ): string[] {}
}
  }
  private createFollowUpPlan(overallScore: number,);
const riskFactors = string[]);
  ): string {if (overallScore >= 80) {}
}
    ;} else if (overallScore >= 60) {}
}
    } else {}
}
    }
  }
}
// 导出单例实例
export const laokeKnowledgeIntegration =;
LaokeKnowledgeIntegration.getInstance();
''
