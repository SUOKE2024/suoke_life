"
";"";
export interface InquiryData {;}symptoms?: SymptomData[];
medicalHistory?: MedicalHistoryData;
lifestyle?: LifestyleData;
familyHistory?: FamilyHistoryData;
currentComplaints?: string;
painAssessment?: PainAssessment;
sleepPattern?: SleepPattern;
dietaryHabits?: DietaryHabits;
emotionalState?: EmotionalState;
}
}
  metadata?: Record<string; any>;}
}
export interface SymptomData {;}name: string,description: string,severity: number;
  , duration: string,
frequency: string,
triggers: string[],
relievingFactors: string[],
const associatedSymptoms = string[];
location?: string;
}
}
  quality?: string;}
}
export interface MedicalHistoryData {previousDiagnoses: string[]}surgeries: string[],;
hospitalizations: string[],
medications: MedicationData[],
}
}
  allergies: string[],immunizations: string[],familyHistory: string[];}
}
export interface MedicationData {name: string}dosage: string,;
frequency: string,duration: string,purpose: string;
}
}
  sideEffects?: string[];}
}
export interface LifestyleData {occupation: string}exerciseHabits: string,;
smokingStatus: string,alcoholConsumption: string,stressLevel: number;
  , workEnvironment: string,
}
}
  const hobbies = string[];}
}
export interface FamilyHistoryData {parents: string[]}siblings: string[],;
}
}
  grandparents: string[],commonDiseases: string[],geneticConditions: string[];}
}
export interface PainAssessment {location: string[],intensity: number}quality: string  / 刺痛、胀痛、隐痛等*  , aggravatingFactors: string[], * /;
const relievingFactors = string[];
}
}
  radiationPattern?: string;}
}
export interface SleepPattern {bedtime: string}wakeTime: string,sleepDuration: number,sleepQuality: number;
}
}
  , difficulties: string[]  / 入睡困难、易醒等* ;}
} * /
export interface DietaryHabits {mealTimes: string[]}appetite: string,;
preferences: string[],
aversions: string[],digestiveIssues: string[],waterIntake: number;
}
}
///     , specialDiets: string[];}
}
export interface EmotionalState {;}mood: string,stressLevel: number;
  , anxietyLevel: number  / 1-10* ///,/;/g,/;
  copingMechanisms: string[],
}
}
  const socialSupport = string;}
}
export interface InquiryResult {;}confidence: number,features: InquiryFeatures,analysis: string;
symptomAnalysis?: SymptomAnalysis;
constitutionalAnalysis?: ConstitutionalAnalysis;
}
}
  syndromePatterns?: SyndromePattern[];}
}
export interface InquiryFeatures {symptoms: ProcessedSymptom[]}constitution: ConstitutionalFeatures,;
lifestyle: LifestyleFeatures,
}
}
  const emotional = EmotionalFeatures;}
}
export interface ProcessedSymptom {name: string}tcmCategory: string,;
severity: number,
}
}
  chronicity: string,pattern: string,organSystem: string[];}
}
export interface ConstitutionalFeatures {bodyType: string}energyLevel: string,;
temperaturePreference: string,
digestiveStrength: string,
}
}
  const sleepQuality = string;}
}
export interface LifestyleFeatures {activityLevel: string}stressFactors: string[],;
environmentalFactors: string[],
}
}
  const socialFactors = string[];}
}
export interface EmotionalFeatures {dominantEmotion: string}emotionalStability: string,;
stressResponse: string,
}
}
  const mentalEnergy = string;}
}
export interface SymptomAnalysis {primarySymptoms: AnalyzedSymptom[]}secondarySymptoms: AnalyzedSymptom[],;
symptomPatterns: SymptomPattern[],
organSystemInvolvement: OrganSystemAnalysis[],
}
}
  const pathogenesis = PathogenesisAnalysis;}
}
export interface AnalyzedSymptom {symptom: ProcessedSymptom}tcmSignificance: string,";
organCorrelation: string[],";
syndromeImplication: string[],";
}
}
  const severity = "mild" | "moderate" | "severe}"";
}
export interface SymptomPattern {name: string}symptoms: string[],;
confidence: number,
}
}
  const tcmInterpretation = string;}
};
export interface OrganSystemAnalysis {;}system: string,involvement: number;
  , symptoms: string[],
}
}
  const dysfunction = string;}
}
export interface PathogenesisAnalysis {primaryCause: string}secondaryCauses: string[],;
pathogenicFactors: string[],
diseaseStage: string,
}
}
  const prognosis = string;}
}
export interface ConstitutionalAnalysis {bodyType: string}constitution: string,;
strengths: string[],
weaknesses: string[],
tendencies: string[],
}
}
  const recommendations = string[];}
}
export interface SyndromePattern {name: string}confidence: number,;
supportingSymptoms: string[],
contradictingSymptoms: string[],
}
}
  const tcmExplanation = string;}
}
export interface UserProfile {";}age: number,";
gender: "male" | "female" | "other,";
height: number,
weight: number,
occupation: string,
medicalHistory: string[],
allergies: string[],
}
}
  const medications = string[];}
}
// 问诊算法类export class InquiryDiagnosisAlgorithm {/;}private config: InquiryConfig;/g/;
private knowledgeBase: TCMKnowledgeBase;
private symptomAnalyzer!: SymptomAnalyzer;
private nlpProcessor!: NLPProcessor;
private patternRecognizer!: PatternRecognizer;
constructor(config: InquiryConfig, knowledgeBase: TCMKnowledgeBase) {this.config = config;}this.knowledgeBase = knowledgeBase;
}
}
    this.initializeAnalyzers(}
  }
  // 初始化分析器  private initializeAnalyzers(): void {/;}this.symptomAnalyzer = new SymptomAnalyzer();/g/;
this.config.models.symptomAnalysis,
this.knowledgeBase;
    );
this.nlpProcessor = new NLPProcessor();
this.config.models.nlpProcessing,
this.knowledgeBase;
    );
this.patternRecognizer = new PatternRecognizer();
this.config.models.semanticAnalysis,
this.knowledgeBase;
}
    }
  }
  // 执行问诊分析  public async analyze(data: InquiryData,)
userProfile?: UserProfile;
  ): Promise<InquiryResult /    >  {/;}if (!this.config.enabled) {}}/g/;
}
    }";
try {";}this.emit("algorithm:progress", {")"";}stage: "preprocessing,")"";
}
      const progress = 0.1;)}
      });";
const processedData = await this.preprocessData(da;t;a;);";
this.emit("algorithm:progress", {)")"";}stage: "nlp_processing,")"";
}
      const progress = 0.3;)}
      });";
const nlpResults = await this.processNaturalLanguage(processedDa;t;a;);";
this.emit("algorithm:progress", {)")"";}stage: "feature_extraction,")"";
}
      const progress = 0.5;)}
      });";
features: await this.extractFeatures(processedData, nlpResul;t;s;);";
this.emit("algorithm:progress", {)")"";}}
      stage: "analysis,)"}
const progress = 0.7;});";
analyses: await this.performAnalyses(features, userProfi;l;e;);";
this.emit("algorithm:progress", {)")"";}}
      stage: "integration,)"}
const progress = 0.9;});";
result: await this.integrateResults(features, analys;e;s;);";
this.emit("algorithm:progress", {)")"";}}
      stage: "completed,)"}";
const progress = 1.0;});
return resu;l;t;
    } catch (error) {"}
this.emit("algorithm:error", { error, stage: "inquiry_analysis";});";"";
const throw = error;
    }
  }
  ///    >  {/;}const: processed: ProcessedInquiryData = {symptoms: []}medicalHistory: data.medicalHistory,/g,/;
  lifestyle: data.lifestyle,
familyHistory: data.familyHistory,
painAssessment: data.painAssessment,
sleepPattern: data.sleepPattern,
dietaryHabits: data.dietaryHabits,
}
      const emotionalState = data.emotionalState;}
    };
if (data.symptoms) {}}
      processed.symptoms = await this.preprocessSymptoms(data.symptoms;}
    }
    if (data.currentComplaints) {processed.currentComplaints = await this.preprocessText(}}
        data.currentComplaints;}
    }
    return process;e;d;
  }
  ///    >  {/;}return symptoms.map(sympto;m;); => ({}      ...symptom,);/g/;
}
      name: this.normalizeSymptomName(symptom.name),}
      const description = this.normalizeText(symptom.description}));
  }
  // 预处理文本  private async preprocessText(text: string): Promise<string>  {/;}}/g/;
    return text.trim().toLowerCase;}
  }
  ///    >  {/;}const: results: NLPResults = {extractedSymptoms: []}medicalEntities: [],/g,/;
  sentimentAnalysis: null,
}
      const keyPhrases = []}
    ;};
if (data.currentComplaints) {results.extractedSymptoms = await this.nlpProcessor.extractSymptoms(}}
        data.currentComplaints;}
    }
    results.medicalEntities = await this.nlpProcessor.extractMedicalEntities();
data;);
results.sentimentAnalysis = await this.nlpProcessor.analyzeSentiment(data;);
results.keyPhrases = await this.nlpProcessor.extractKeyPhrases(data;);
return resul;t;s;
  }
  // 特征提取  private async extractFeatures(data: ProcessedInquiryData,)"
const nlpResults = NLPResults): Promise<InquiryFeatures /    >  {/;}const: features: InquiryFeatures = {symptoms: [],";}constitution: {,";}bodyType: ,";"/g,"/;
  energyLevel: ",",";
temperaturePreference: ,";
digestiveStrength: ",",";
}
        const sleepQuality = "}
      ;},";
lifestyle: {,";}activityLevel: ,";"";
stressFactors: [],
environmentalFactors: [],
}
        const socialFactors = []}
      ;},";
emotional: {,";}dominantEmotion: ",",";
emotionalStability: ,";
stressResponse: ",",";
}
        const mentalEnergy = "}"";
      ;}
    };
features.symptoms = await this.symptomAnalyzer.processSymptoms();
data.symptoms || [],
nlpResults.extractedSymptoms;);
features.constitution = await this.extractConstitutionalFeatures(data;);
features.lifestyle = await this.extractLifestyleFeatures(data;);
features.emotional = await this.extractEmotionalFeatures(data, nlpResults;);
return featur;e;s;
  }
  // 执行各项分析  private async performAnalyses(features: InquiryFeatures,)
userProfile?: UserProfile;
  ): Promise<AnalysisResults /    >  {}
const results: AnalysisResults = {;};
results.symptomAnalysis = await this.symptomAnalyzer.analyzeSymptoms();
features.symptoms,
userProfile;);
results.constitutionalAnalysis = await this.analyzeConstitution();
features,
userProfile;);
results.syndromePatterns = await this.patternRecognizer.identifyPatterns();
features;);
return resul;t;s;
  }
  // 整合分析结果  private async integrateResults(features: InquiryFeatures,)
const analyses = AnalysisResults);: Promise<InquiryResult /    >  {/;}confidence: this.calculateOverallConfidence(features, analyses;);/g/;
}
    const analysis = await this.generateComprehensiveAnalysis(analys;e;s;}
    return {confidence,features,analysis,symptomAnalysis: analyses.symptomAnalysis,constitutionalAnalysis: analyses.constitutionalAnalysis,syndromePatterns: analyses.syndromePattern;s;};
  }
  // 计算整体置信度  private calculateOverallConfidence(features: InquiryFeatures,)
const analyses = AnalysisResults);: number  {let totalWeight = 0;}let weightedSum = 0;
symptomWeight: Math.min(features.symptoms.length  / 5, 1;);  0.4;/ totalWeight += symptomWeight;
weightedSum += symptomWeight * 0.8;
if (analyses.constitutionalAnalysis) {totalWeight += 0.3;}}
      weightedSum += 0.3 * 0.7;}
    }
    if (analyses.syndromePatterns && analyses.syndromePatterns.length > 0) {const  avgConfidence =;}analyses.syndromePatterns.reduce(sum, p;); => sum + p.confidence, 0) // analyses.syndromePatterns.length;
totalWeight += 0.3;
}
      weightedSum += 0.3 * avgConfidence;}
    }
    return totalWeight > 0 ? weightedSum / totalWeight : 0;.;5;/      }
  // 生成综合分析  private async generateComprehensiveAnalysis(analyses: AnalysisResults);: Promise<string>  {/;}const analysisTexts: string[] = [];/g/;
if (analyses.symptomAnalysis) {const primarySymptoms = analyses.symptomAnalysis.primarySymptoms;";}        .map(s) => s.symptom.name)
        .join("、");";
}
}
    }
    if (analyses.constitutionalAnalysis) {analysisTexts.push(}}
      }
    }
    if (analyses.syndromePatterns && analyses.syndromePatterns.length > 0) {const topPattern = analyses.syndromePatterns[0];}analysisTexts.push();
}
          topPattern.confidence * 100;}
        ).toFixed(1)}%）`;`````;```;
      );
    }
    const  comprehensiveAnalysis =;
const await = this.knowledgeBase.generateCalculationAnalysis({ inquiryAnalysis: anal;y;s;e;s ; });
    ;);
  }
  private normalizeSymptomName(name: string): string  {}}
    return name.trim().toLowerCase;}
  }
  private normalizeText(text: string): string  {}}
    return text.trim;}
  }
  private async extractConstitutionalFeatures(data: ProcessedInquiryData): Promise<ConstitutionalFeatures /    >  {/;}return {}}/g/;
}
    ;};
  }
  private async extractLifestyleFeatures(data: ProcessedInquiryData;);: Promise<LifestyleFeatures /    >  {/;}: [],/g/;
const environmentalFactors = data.lifestyle?.workEnvironment;? [data.lifestyle.workEnvironment];
        : [],
}
      const socialFactors = []}
    ;};
  }
  private async extractEmotionalFeatures(data: ProcessedInquiryData,);
const nlpResults = NLPResults;);: Promise<EmotionalFeatures /    >  {/;}}/g/;
}
    };
  }
  private async analyzeConstitution(features: InquiryFeatures,);
userProfile?: UserProfile;
  ): Promise<ConstitutionalAnalysis /    >  {/;}}/g/;
}
  }
  // 模拟事件发射  public on(event: string, callback: (data: unknown) => void): void {}
    ;}
  public: emit(event: string, data?: unknown): void  {}
    ;}
  // 清理资源  public async cleanup(): Promise<void> {/;}const await = Promise.all();/g/;
      [;]this.symptomAnalyzer.cleanup?.(),
this.nlpProcessor.cleanup?.(),
this.patternRecognizer.cleanup?.();
];
      ].filter(Boolean;);
}
    }
  }
}
// 辅助类型定义 * interface ProcessedInquiryData {/;}const symptoms = SymptomData[] ;/g/;
medicalHistory?: MedicalHistoryData;
lifestyle?: LifestyleData;
familyHistory?: FamilyHistoryData;
currentComplaints?: string;
painAssessment?: PainAssessment;
sleepPattern?: SleepPattern;
dietaryHabits?: DietaryHabits;
}
}
  emotionalState?: EmotionalState;}
}
interface NLPResults {extractedSymptoms: string[]}medicalEntities: string[],
sentimentAnalysis: unknown,
}
}
  const keyPhrases = string[];}
}
interface AnalysisResults {symptomAnalysis?: SymptomAnalysis;}constitutionalAnalysis?: ConstitutionalAnalysis;
}
}
  syndromePatterns?: SyndromePattern[];}
}
//
constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {;}
  async: processSymptoms(symptoms: SymptomData[],);
const extractedSymptoms = string[]);: Promise<ProcessedSymptom[] /    >  {/;}return symptoms.map(symptom;) => ({)      name: symptom.name}severity: symptom.severity,/g/;
const chronicity = symptom.duration;);
);
}
)}
    }));
  }
  async: analyzeSymptoms(symptoms: ProcessedSymptom[],);
userProfile?: UserProfile;
  );: Promise<SymptomAnalysis /    >  {/;}return {primarySymptoms: symptoms.map(s) => ({)}symptom: s,/g,/;
  organCorrelation: s.organSystem,
";
}
        const severity = "moderate" as const;"}"";
      })),
secondarySymptoms: [],
symptomPatterns: [;]{symptoms: symptoms.map(s) => s.name),
const confidence = 0.8;
}
}
        };
];
      ],organSystemInvolvement: [;]{,}}
}
        ;};
];
      ],pathogenesis: {,}}
}
      ;};
    };
  }
  const async = cleanup(): Promise<void> {}
}
class NLPProcessor {}
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {;}
  const async = extractSymptoms(text: string): Promise<string[]>  {}}
}
  ;}
  const async = extractMedicalEntities(data: ProcessedInquiryData);: Promise<string[]>  {}}
}
  }
  const async = analyzeSentiment(data: ProcessedInquiryData);: Promise<any>  {";}return {";}}
      mood: "neutral,"}";
const confidence = 0.;7 ;};
  }
  const async = extractKeyPhrases(data: ProcessedInquiryData): Promise<string[]>  {}}
}
  ;}
  const async = cleanup(): Promise<void> {}
}
class PatternRecognizer {}
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {;}
  const async = identifyPatterns(features: InquiryFeatures;);: Promise<SyndromePattern[] /    >  {/;}return [;];/g/;
      {}}
}
      };
];
    ];
  };
const async = cleanup(): Promise<void> {};
};";
export default InquiryDiagnosisAlgorithm;""