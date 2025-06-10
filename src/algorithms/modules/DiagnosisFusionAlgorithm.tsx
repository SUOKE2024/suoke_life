;/import { TCMKnowledgeBase } from "../knowledge/    TCMKnowledgeBase;""/;"/g"/;
";,"";
export interface FusionInput {;,}lookingResult?: unknown;
listeningResult?: unknown;
inquiryResult?: unknown;
palpationResult?: unknown;
calculationResult?: unknown;
userProfile?: UserProfile;
}
}
sessionContext?: SessionContext;}
}
export interface UserProfile {";,}age: number,";,"";
gender: "male" | "female" | "other";",";
height: number,;
weight: number,;
occupation: string,;
medicalHistory: string[],allergies: string[],medications: string[];
}
}
  constitution?: string;}
}
export interface SessionContext {sessionId: string}timestamp: number,;
environment: {temperature: number,;}}
}
  humidity: number,season: string,timeOfDay: string;}
};
previousSessions?: string[];
}
export interface FusionResult {confidence: number}overallAssessment: string,;
primarySyndromes: SyndromeResult[],;
secondarySyndromes: SyndromeResult[],;
constitutionAnalysis: ConstitutionResult,;
riskFactors: RiskFactor[],;
recommendations: Recommendation[],;
followUpAdvice: string[],;
}
}
  const dataQuality = DataQualityReport;}
}
export interface SyndromeResult {id: string}name: string,;
confidence: number,";,"";
evidence: Evidence[],";,"";
severity: "mild" | "moderate" | "severe";",";
urgency: "low" | "medium" | "high";","";"";
}
}
  const description = string;}
}";,"";
export interface Evidence {";,}source: "looking" | "listening" | "inquiry" | "palpation" | "calculation";",";
type: string,;
value: unknown,;
weight: number,;
confidence: number,;
}
}
  const description = string;}
}
export interface ConstitutionResult {primaryType: string}secondaryTypes: string[],;
confidence: number,;
characteristics: string[],;
tendencies: string[],;
}
}
  const recommendations = string[];}
}
export interface RiskFactor {";,}type: string,";,"";
level: "low" | "medium" | "high";",";
description: string,;
}
}
  const prevention = string[];}
}";,"";
export interface Recommendation {";,}category: "treatment" | "lifestyle" | "diet" | "exercise" | "prevention";",";
priority: "high" | "medium" | "low",title: string,description: string;";,"";
duration?: string;
}
}
  contraindications?: string[];}
}
export interface DataQualityReport {completeness: number}consistency: number,;
}
}
  reliability: number,issues: string[],suggestions: string[];}
}
// 诊断融合算法类export class DiagnosisFusionAlgorithm {/;,}private config: FusionConfig;,/g/;
private knowledgeBase: TCMKnowledgeBase;
private weightMatrix: Map<string, number> = new Map();
private syndromePatterns: Map<string, any> = new Map();
constructor(config: FusionConfig, knowledgeBase: TCMKnowledgeBase) {this.config = config;,}this.knowledgeBase = knowledgeBase;
this.initializeWeights();
}
}
    this.initializeSyndromePatterns();}
  }";"";
  // 初始化权重矩阵  private initializeWeights(): void {/;}";,"/g"/;
this.weightMatrix.set("looking", 0.25);";,"";
this.weightMatrix.set("listening", 0.15);";,"";
this.weightMatrix.set("inquiry", 0.3);";,"";
this.weightMatrix.set("palpation", 0.2);";,"";
this.weightMatrix.set("calculation", 0.1);";"";
}
    if (this.config.weights) {}
      Object.entries(this.config.weights).forEach([key, value]) => {}));
this.weightMatrix.set(key, value);
      });
    }
  }";"";
  // 初始化证候模式  private initializeSyndromePatterns(): void {/;}";,"/g"/;
this.syndromePatterns.set("qi_deficiency", {";,)requiredEvidence: ["fatigue",shortness_of_breath"],"";,}supportingEvidence: ["pale_tongue",weak_pulse"],")";,"";
excludingEvidence: ["fever",red_tongue"],")"";"";
}
      const minConfidence = 0.6;)}";"";
    });";,"";
this.syndromePatterns.set("blood_stasis", {)";,}requiredEvidence: ["fixed_pain",dark_complexion"],";
supportingEvidence: ["purple_tongue",choppy_pulse"],")";,"";
excludingEvidence: ["floating_pulse"];",")"";"";
}
      const minConfidence = 0.7;)}
    });
  }
  ///    >  {/;,}if (!this.config.enabled) {}}/g/;
}
    }";,"";
try {"}";
this.emit("fusion:started", { sessionId: input.sessionContext?.sessionId;});";,"";
const dataQuality = await this.assessDataQuality(inp;u;t;);
const evidence = await this.extractEvidence(inp;u;t;);
const syndromes = await this.identifySyndromes(;);
evidence,input.userProf;i;l;e;);
const constitution = await this.analyzeConstitution(;);
evidence,input.userProf;i;l;e;);
const riskFactors = await this.assessRiskFactors(;);
syndromes,constitution,input.userProf;i;l;e;);
const recommendations = await this.generateRecommendations(;);
syndromes,constitution,riskFact;o;r;s;);
const confidence = this.calculateOverallConfidence(;);
evidence,syndromes,dataQualit;y;);
const overallAssessment = await this.generateOverallAssessment(;);
syndromes,constitution,evide;n;c;e;);
const followUpAdvice = await this.generateFollowUpAdvice(;);
syndromes,constitution,dataQual;i;t;y;);
const: result: FusionResult = {confidence}overallAssessment,;
primarySyndromes: syndromes.filter(s); => s.confidence > 0.7),;
secondarySyndromes: syndromes.filter(s); => s.confidence <= 0.7 && s.confidence > 0.4;
        ),;
const constitutionAnalysis = constitution;
riskFactors,;
recommendations,;
followUpAdvice,;
}
        dataQuality;}";"";
      }";,"";
this.emit("fusion:completed", { result ;});";,"";
return resu;l;t;";"";
    } catch (error) {"}";
this.emit("fusion:error", { error ;});";,"";
const throw = error;
    }
  }
  ///    >  {/;,}const availableData = ;[;];,/g/;
const issues = ;[;];
const suggestions = ;[;];";,"";
if (input.lookingResult) {";}}"";
      availableData.push("looking");"}"";"";
    } else {}}
}
    }";,"";
if (input.listeningResult) {";}}"";
      availableData.push("listening");"}"";"";
    } else {}}
}
    }";,"";
if (input.inquiryResult) {";}}"";
      availableData.push("inquiry");"}"";"";
    } else {}}
}
    }";,"";
if (input.palpationResult) {";}}"";
      availableData.push("palpation");"}"";"";
    } else {}}
}
    }";,"";
if (input.calculationResult) {";}}"";
      availableData.push("calculation");"}"";"";
    } else {}}
}
    }
    const completeness = availableData.length ;/ ;5; 检查数据一致性 // let consistency = 1.;0;/;,/g/;
if (availableData.length >= 2) {}}
      consistency = await this.checkDataConsistency(inpu;t;);}
    }
    const reliability = await this.checkDataReliability(inp;u;t;);
if (completeness < 0.6) {}}
}
    }
    if (consistency < 0.7) {}}
}
    }
    if (reliability < 0.8) {}}
}
    }
    return {completeness,consistency,reliability,issues,suggestion;s;};
  }
  ///    >  {/;,}const evidence: Evidence[] = [];,/g/;
if (input.lookingResult) {}}
      evidence.push(...this.extractLookingEvidence(input.lookingResult));}
    }
    if (input.listeningResult) {}}
      evidence.push(...this.extractListeningEvidence(input.listeningResult));}
    }
    if (input.inquiryResult) {}}
      evidence.push(...this.extractInquiryEvidence(input.inquiryResult));}
    }
    if (input.palpationResult) {}}
      evidence.push(...this.extractPalpationEvidence(input.palpationResult));}
    }
    if (input.calculationResult) {evidence.push();}        ...this.extractCalculationEvidence(input.calculationResult);
}
      );}
    }
    return eviden;c;e;
  }
  // 识别证候  private async identifySyndromes(evidence: Evidence[],)/;,/g/;
userProfile?: UserProfile;
  ): Promise<SyndromeResult[] /    >  {/;,}const syndromes: SyndromeResult[] = [];,/g/;
for (const [syndromeId, pattern] of Array.from());
this.syndromePatterns.entries();
    )) {confidence: this.calculateSyndromeConfidence(evidence, patter;n;);,}if (confidence > pattern.minConfidence) {const syndrome = await this.knowledgeBase.getSyndrome(syndrom;e;I;d;);,}if (syndrome) {syndromes.push({)            id: syndromeId,);,}const name = syndrome.name;);
confidence,);
evidence: this.getRelevantEvidence(evidence, pattern),;
severity: this.assessSeverity(evidence, pattern),;
urgency: this.assessUrgency(evidence, pattern),;
}
            const description = syndrome.description;}
          });
        }
      }
    }
    return syndromes.sort(a,b;); => b.confidence - a.confidence);
  }
  // 分析体质  private async analyzeConstitution(evidence: Evidence[],)/;,/g/;
userProfile?: UserProfile;
  ): Promise<ConstitutionResult /    >  {/;,}constitutionScores: new Map<string, number>(;)";,"/g"/;
const constitutionTypes = [;];";"";
];
      "balanced",qi_deficiency","yang_deficiency",yin_deficiency","phlegm_dampness"];";,"";
for (const type of constitutionTypes) {;,}const score = this.calculateConstitutionScore(;);
evidence,;
type,userProfil;e;);
}
      constitutionScores.set(type, score);}
    }
    const sortedTypes = Array.from(constitutionScores.entries).sort(;);
      (a, b) => b[1] - a[1];
    );
const primaryType = sortedTypes[0][0];
secondaryTypes: sortedTypes.slice(1, 3).map([type;];); => type);
const constitution = await this.knowledgeBase.getConstitution(primaryT;y;p;e;);
return {primaryType,secondaryTypes,confidence: sortedTypes[0][1],characteristics: constitution?.characteristics.physical || [],tendencies: constitution?.characteristics.pathological || [],recommendations: constitution?.recommendations.lifestyle || [;]}
    ;};
  }
  // 评估风险因素  private async assessRiskFactors(syndromes: SyndromeResult[],)/;,/g/;
const constitution = ConstitutionResult;
userProfile?: UserProfile;
  ): Promise<RiskFactor[] /    >  {/;,}const riskFactors: RiskFactor[] = [];";,"/g"/;
for (const syndrome of syndromes) {";,}if (syndrome.confidence > 0.8 && syndrome.severity === "severe") {";,}riskFactors.push({";,)type: "syndrome_risk";","";,}const level = "high";")"";"";
);
}
)}
        });
      }";"";
    }";,"";
if (constitution.primaryType !== "balanced") {";,}riskFactors.push({";,)type: "constitution_risk";","";,}level: "medium";",)"";"";
);
}
        const prevention = constitution.recommendations;)}
      });
    }
    if (userProfile && userProfile.age > 60) {";,}riskFactors.push({";,)type: "age_risk";","";,}const level = "medium";")"";"";
);
}
)}
      });
    }
    return riskFacto;r;s;
  }
  // 生成建议  private async generateRecommendations(syndromes: SyndromeResult[],)/;,/g,/;
  constitution: ConstitutionResult,;
const riskFactors = RiskFactor[]);: Promise<Recommendation[] /    >  {/;,}const recommendations: Recommendation[] = [];,/g/;
for (const syndrome of syndromes.slice(0, 2)) {if (syndrome.confidence > 0.7) {;,}const treatments = await this.knowledgeBase.getTreatmentRecommendations(;);
          [syndrome.;i;d;];
        ;);
for (const treatment of treatments) {";,}recommendations.push({";,)category: "treatment";","";,}priority: syndrome.urgency === "high" ? "high" : "medium";",";
title: treatment.name,;
description: treatment.description,);
duration: treatment.duration,);
}
            const contraindications = treatment.contraindications;)}
          });
        }
      }
    }";,"";
recommendations.push({)";,}category: "lifestyle";",";
const priority = "medium";";"";
);
);
}
)}
    });";,"";
for (const risk of riskFactors) {";,}if (risk.level === "high") {";,}recommendations.push({";,)category: "prevention";","";,}priority: "high";","";"";
);
const description = risk.description;);
}
)}
        });
      }
    }
    return recommendations.sort(a,b;); => {}
      priorityOrder: { high: 3, medium: 2, low;: ;1 ;};
return priorityOrder[b.priority] - priorityOrder[a.priorit;y;];
    });
  }
  private async checkDataConsistency(input: FusionInput): Promise<number>  {}}
    return 0.;8;}
  }
  private async checkDataReliability(input: FusionInput);: Promise<number>  {}}
    return 0.8;5;}
  }
  private extractLookingEvidence(result: unknown);: Evidence[]  {}}
    return [];}
  }
  private extractListeningEvidence(result: unknown);: Evidence[]  {}}
    return [];}
  }
  private extractInquiryEvidence(result: unknown);: Evidence[]  {}}
    return [];}
  }
  private extractPalpationEvidence(result: unknown);: Evidence[]  {}}
    return [];}
  }
  private extractCalculationEvidence(result: unknown);: Evidence[]  {}}
    return [];}
  }
  private calculateSyndromeConfidence(evidence: Evidence[],);
const pattern = unknown;);: number  {}}
    return 0.;7;}
  }
  private getRelevantEvidence(evidence: Evidence[], pattern: unknown);: Evidence[]  {}}
    return evidence.slice(0, 3;);}
  }";,"";
private assessSeverity(evidence: Evidence[],)";,"";
const pattern = unknown;): "mild" | "moderate" | "severe"  {";}}"";
    return "moderate";"}"";"";
  }";,"";
private assessUrgency(evidence: Evidence[],)";,"";
const pattern = unknown;);: "low" | "medium" | "high"  {";}}"";
    return "medium";"}"";"";
  }
  private calculateConstitutionScore(evidence: Evidence[],);
const type = string;
userProfile?: UserProfile;
  );: number  {}}
    return Math.random * 0.5 + 0.5 ;}
  };
private calculateOverallConfidence(evidence: Evidence[],syndromes: SyndromeResult[],dataQuality: DataQualityReport;);: number  {const evidenceWeight = 0.;4;,}const syndromeWeight = 0;.;4;
const qualityWeight = 0;.;2;
const  evidenceScore =;
evidence.length > 0;
        ? evidence.reduce(sum,e;); => sum + e.confidence, 0) / evidence.length/            : 0.5;/;,/g/;
const  syndromeScore =;
syndromes.length > 0;
        ? syndromes.reduce(sum,s;); => sum + s.confidence, 0) / syndromes.length/            : 0.5;/;,/g/;
const  qualityScore =;
      (dataQuality.completeness +;);
dataQuality.consistency +;
dataQuality.reliability)      ;3;
    // 记录渲染性能/;,/g/;
performanceMonitor.recordRender();
return (;);
evidenceScore * evidenceWeight +;
syndromeScore * syndromeWeight +;
}
      qualityScore * qualityWeigh;t;);}
  }
  private async generateOverallAssessment(syndromes: SyndromeResult[],);
constitution: ConstitutionResult,;
const evidence = Evidence[];);: Promise<string>  {const assessmentParts: string[] = [];,}if (syndromes.length > 0) {const primarySyndrome = syndromes[0];,}assessmentParts.push();

}
          primarySyndrome.confidence * 100;}
        ).toFixed(1)}%``````;```;
      );
    }

    if (evidence.length > 0) {}}
}
    }
    return (;);

    );
  }
  private async generateFollowUpAdvice(syndromes: SyndromeResult[],);
constitution: ConstitutionResult,;
const dataQuality = DataQualityReport;);: Promise<string[]>  {const advice: string[] = [];,}if (dataQuality.completeness < 0.8) {}}
}";"";
    }";,"";
if (syndromes.some(s) => s.urgency === "high")) {";}}"";
}
    } else {}}
}
    }

    return advi;c;e;
  }
  // 模拟事件发射  public on(event: string, callback: (data: unknown) => void): void {}/;/g/;
    ;}
  public: emit(event: string, data?: unknown): void  {}
    ;}
  // 清理资源  public async cleanup(): Promise<void> {/;,}this.weightMatrix.clear();/g/;
}
    this.syndromePatterns.clear();}
  }
}";,"";
export default DiagnosisFusionAlgorithm;""";