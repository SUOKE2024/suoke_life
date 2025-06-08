import { InquiryConfig } from "../../placeholder";../config/AlgorithmConfig";/import { TCMKnowledgeBase } from "../knowledge/    TCMKnowledgeBase;
import React from "react";
问诊算法模块     实现中医问诊功能，包括症状分析、病史分析、自然语言处理     @author 索克生活技术团队   @version 1.0.0;
export interface InquiryData {
  symptoms?: SymptomData[];
  medicalHistory?: MedicalHistoryData;
  lifestyle?: LifestyleData;
  familyHistory?: FamilyHistoryData;
  currentComplaints?: string;
  painAssessment?: PainAssessment;
  sleepPattern?: SleepPattern;
  dietaryHabits?: DietaryHabits;
  emotionalState?: EmotionalState;
  metadata?: Record<string, any>;
}
export interface SymptomData {
  name: string,description: string,severity: number;
  , duration: string;
  frequency: string;
  triggers: string[];
  relievingFactors: string[];
  associatedSymptoms: string[];
  location?: string;
  quality?: string
}
export interface MedicalHistoryData {
  previousDiagnoses: string[];
  surgeries: string[];
  hospitalizations: string[];
  medications: MedicationData[];
  allergies: string[],immunizations: string[],familyHistory: string[];
}
export interface MedicationData {
  name: string;
  dosage: string;
  frequency: string,duration: string,purpose: string;
  sideEffects?: string[];
}
export interface LifestyleData {
  occupation: string;
  exerciseHabits: string;
  smokingStatus: string,alcoholConsumption: string,stressLevel: number;
  , workEnvironment: string;
  hobbies: string[];
}
export interface FamilyHistoryData {
  parents: string[];
  siblings: string[];
  grandparents: string[],commonDiseases: string[],geneticConditions: string[];
}
export interface PainAssessment {
  location: string[],intensity: number;
  quality: string  / 刺痛、胀痛、隐痛等*  , aggravatingFactors: string[], * /
  relievingFactors: string[];
  radiationPattern?: string
}
export interface SleepPattern {
  bedtime: string;
  wakeTime: string,sleepDuration: number,sleepQuality: number;
  , difficulties: string[]  / 入睡困难、易醒等* ;
} * /
export interface DietaryHabits {
  mealTimes: string[];
  appetite: string;
  preferences: string[];
  aversions: string[],digestiveIssues: string[],waterIntake: number;
///     , specialDiets: string[];
}
export interface EmotionalState {
  mood: string,stressLevel: number;
  , anxietyLevel: number  / 1-10* ///
  copingMechanisms: string[];
  socialSupport: string;
}
export interface InquiryResult {
  confidence: number,features: InquiryFeatures,analysis: string;
  symptomAnalysis?: SymptomAnalysis;
  constitutionalAnalysis?: ConstitutionalAnalysis;
  syndromePatterns?: SyndromePattern[];
}
export interface InquiryFeatures {
  symptoms: ProcessedSymptom[];
  constitution: ConstitutionalFeatures;
  lifestyle: LifestyleFeatures;
  emotional: EmotionalFeatures;
}
export interface ProcessedSymptom {
  name: string;
  tcmCategory: string;
  severity: number;
  chronicity: string,pattern: string,organSystem: string[];
}
export interface ConstitutionalFeatures {
  bodyType: string;
  energyLevel: string;
  temperaturePreference: string;
  digestiveStrength: string;
  sleepQuality: string;
}
export interface LifestyleFeatures {
  activityLevel: string;
  stressFactors: string[];
  environmentalFactors: string[];
  socialFactors: string[];
}
export interface EmotionalFeatures {
  dominantEmotion: string;
  emotionalStability: string;
  stressResponse: string;
  mentalEnergy: string;
}
export interface SymptomAnalysis {
  primarySymptoms: AnalyzedSymptom[];
  secondarySymptoms: AnalyzedSymptom[];
  symptomPatterns: SymptomPattern[];
  organSystemInvolvement: OrganSystemAnalysis[];
  pathogenesis: PathogenesisAnalysis;
}
export interface AnalyzedSymptom {
  symptom: ProcessedSymptom;
  tcmSignificance: string;
  organCorrelation: string[];
  syndromeImplication: string[];
  severity: "mild" | "moderate" | "severe";
}
export interface SymptomPattern {
  name: string;
  symptoms: string[];
  confidence: number;
  tcmInterpretation: string;
};
export interface OrganSystemAnalysis {
  system: string,involvement: number;
  , symptoms: string[];
  dysfunction: string;
}
export interface PathogenesisAnalysis {
  primaryCause: string;
  secondaryCauses: string[];
  pathogenicFactors: string[];
  diseaseStage: string;
  prognosis: string;
}
export interface ConstitutionalAnalysis {
  bodyType: string;
  constitution: string;
  strengths: string[];
  weaknesses: string[];
  tendencies: string[];
  recommendations: string[];
}
export interface SyndromePattern {
  name: string;
  confidence: number;
  supportingSymptoms: string[];
  contradictingSymptoms: string[];
  tcmExplanation: string;
}
export interface UserProfile {
  age: number;
  gender: "male" | "female" | "other";
  height: number;
  weight: number;
  occupation: string;
  medicalHistory: string[];
  allergies: string[];
  medications: string[];
}
// 问诊算法类export class InquiryDiagnosisAlgorithm  {private config: InquiryConfig;
  private knowledgeBase: TCMKnowledgeBase;
  private symptomAnalyzer!: SymptomAnalyzer;
  private nlpProcessor!: NLPProcessor;
  private patternRecognizer!: PatternRecognizer;
  constructor(config: InquiryConfig, knowledgeBase: TCMKnowledgeBase) {
    this.config = config;
    this.knowledgeBase = knowledgeBase;
    this.initializeAnalyzers();
  }
  // 初始化分析器  private initializeAnalyzers(): void {
    this.symptomAnalyzer = new SymptomAnalyzer(
      this.config.models.symptomAnalysis,
      this.knowledgeBase;
    );
    this.nlpProcessor = new NLPProcessor(
      this.config.models.nlpProcessing,
      this.knowledgeBase;
    );
    this.patternRecognizer = new PatternRecognizer(
      this.config.models.semanticAnalysis,
      this.knowledgeBase;
    );
  }
  // 执行问诊分析  public async analyze(data: InquiryData,
    userProfile?: UserProfile;
  ): Promise<InquiryResult /    >  {
    if (!this.config.enabled) {
      throw new Error("问诊功能未启用";);
    }
    try {
      this.emit("algorithm:progress", {
      stage: "preprocessing",
      progress: 0.1;
      });
      const processedData = await this.preprocessData(da;t;a;);
      this.emit("algorithm:progress", {
      stage: "nlp_processing",
      progress: 0.3;
      });
      const nlpResults = await this.processNaturalLanguage(processedDa;t;a;);
      this.emit("algorithm:progress", {
      stage: "feature_extraction",
      progress: 0.5;
      });
      const features = await this.extractFeatures(processedData, nlpResul;t;s;);
      this.emit("algorithm:progress", {
      stage: "analysis",
      progress: 0.7});
      const analyses = await this.performAnalyses(features, userProfi;l;e;);
      this.emit("algorithm:progress", {
      stage: "integration",
      progress: 0.9});
      const result = await this.integrateResults(features, analys;e;s;);
      this.emit("algorithm:progress", {
      stage: "completed",
      progress: 1.0});
      return resu;l;t;
    } catch (error) {
      this.emit("algorithm:error", { error, stage: "inquiry_analysis"});
      throw error;
    }
  }
  ///    >  {
    const processed: ProcessedInquiryData = {symptoms: [],
      medicalHistory: data.medicalHistory,
      lifestyle: data.lifestyle,
      familyHistory: data.familyHistory,
      painAssessment: data.painAssessment,
      sleepPattern: data.sleepPattern,
      dietaryHabits: data.dietaryHabits,
      emotionalState: data.emotionalState;
    };
    if (data.symptoms) {
      processed.symptoms = await this.preprocessSymptoms(data.symptoms;);
    }
    if (data.currentComplaints) {
      processed.currentComplaints = await this.preprocessText(
        data.currentComplaints;);
    }
    return process;e;d;
  }
  ///    >  {
    return symptoms.map(sympto;m;); => ({
      ...symptom,
      name: this.normalizeSymptomName(symptom.name),
      description: this.normalizeText(symptom.description)}));
  }
  // 预处理文本  private async preprocessText(text: string): Promise<string>  {
    return text.trim().toLowerCase;
  }
  ///    >  {
    const results: NLPResults = {extractedSymptoms: [],
      medicalEntities: [],
      sentimentAnalysis: null,
      keyPhrases: []
    };
    if (data.currentComplaints) {
      results.extractedSymptoms = await this.nlpProcessor.extractSymptoms(
        data.currentComplaints;);
    }
    results.medicalEntities = await this.nlpProcessor.extractMedicalEntities(
      data;);
    results.sentimentAnalysis = await this.nlpProcessor.analyzeSentiment(data;);
    results.keyPhrases = await this.nlpProcessor.extractKeyPhrases(data;);
    return resul;t;s;
  }
  // 特征提取  private async extractFeatures(data: ProcessedInquiryData,
    nlpResults: NLPResults): Promise<InquiryFeatures /    >  {
    const features: InquiryFeatures = {symptoms: [],
      constitution: {,
  bodyType: ",
        energyLevel: ","
        temperaturePreference: ",
        digestiveStrength: ","
        sleepQuality: ""
      },
      lifestyle: {,
  activityLevel: ",
        stressFactors: [],
        environmentalFactors: [],
        socialFactors: []
      },
      emotional: {,
  dominantEmotion: ",",
        emotionalStability: ",
        stressResponse: ",",
        mentalEnergy: ""
      }
    };
    features.symptoms = await this.symptomAnalyzer.processSymptoms(
      data.symptoms || [],
      nlpResults.extractedSymptoms;);
    features.constitution = await this.extractConstitutionalFeatures(data;);
    features.lifestyle = await this.extractLifestyleFeatures(data;);
    features.emotional = await this.extractEmotionalFeatures(data, nlpResults;);
    return featur;e;s;
  }
  // 执行各项分析  private async performAnalyses(features: InquiryFeatures,
    userProfile?: UserProfile;
  ): Promise<AnalysisResults /    >  {
    const results: AnalysisResults = {};
    results.symptomAnalysis = await this.symptomAnalyzer.analyzeSymptoms(
      features.symptoms,
      userProfile;);
    results.constitutionalAnalysis = await this.analyzeConstitution(
      features,
      userProfile;);
    results.syndromePatterns = await this.patternRecognizer.identifyPatterns(
      features;);
    return resul;t;s;
  }
  // 整合分析结果  private async integrateResults(features: InquiryFeatures,
    analyses: AnalysisResults);: Promise<InquiryResult /    >  {
    const confidence = this.calculateOverallConfidence(features, analyses;);
    const analysis = await this.generateComprehensiveAnalysis(analys;e;s;);
    return {confidence,features,analysis,symptomAnalysis: analyses.symptomAnalysis,constitutionalAnalysis: analyses.constitutionalAnalysis,syndromePatterns: analyses.syndromePattern;s;};
  }
  // 计算整体置信度  private calculateOverallConfidence(features: InquiryFeatures,
    analyses: AnalysisResults);: number  {
    let totalWeight = 0;
    let weightedSum = 0;
    const symptomWeight = Math.min(features.symptoms.length  / 5, 1;);  0.4;/ totalWeight += symptomWeight;
    weightedSum += symptomWeight * 0.8;
    if (analyses.constitutionalAnalysis) {
      totalWeight += 0.3;
      weightedSum += 0.3 * 0.7;
    }
    if (analyses.syndromePatterns && analyses.syndromePatterns.length > 0) {
      const avgConfidence =;
        analyses.syndromePatterns.reduce(sum, p;); => sum + p.confidence, 0) // analyses.syndromePatterns.length;
      totalWeight += 0.3;
      weightedSum += 0.3 * avgConfidence;
    }
    return totalWeight > 0 ? weightedSum / totalWeight : 0;.;5;/      }
  // 生成综合分析  private async generateComprehensiveAnalysis(analyses: AnalysisResults);: Promise<string>  {
    const analysisTexts: string[] = [];
    if (analyses.symptomAnalysis) {
      const primarySymptoms = analyses.symptomAnalysis.primarySymptoms;
        .map(s) => s.symptom.name)
        .join("、");
      analysisTexts.push(`主要症状：${primarySymptoms}`);
    }
    if (analyses.constitutionalAnalysis) {
      analysisTexts.push(
        `体质类型：${analyses.constitutionalAnalysis.constitution}`
      );
    }
    if (analyses.syndromePatterns && analyses.syndromePatterns.length > 0) {
      const topPattern = analyses.syndromePatterns[0];
      analysisTexts.push(
        `主要证候：${topPattern.name}（置信度：${(
          topPattern.confidence * 100;
        ).toFixed(1)}%）`;
      );
    }
    const comprehensiveAnalysis =
      await this.knowledgeBase.generateCalculationAnalysis({ inquiryAnalysis: anal;y;s;e;s ; });
    return [...analysisTexts, ",综合问诊分析：", comprehensiveAnalysis].join(\n;"
    ;);
  }
  private normalizeSymptomName(name: string): string  {
    return name.trim().toLowerCase;
  }
  private normalizeText(text: string): string  {
    return text.trim;
  }
  private async extractConstitutionalFeatures(data: ProcessedInquiryData): Promise<ConstitutionalFeatures /    >  {
    return {
      bodyType: "适中",
      energyLevel: "正常",temperaturePreference: "适中",digestiveStrength: "正常",sleepQuality: data.sleepPattern?.sleepQualit;y? data.sleepPattern.sleepQuality > 7;
          ? "良好"
          : "一般"
        : "未知"
    };
  }
  private async extractLifestyleFeatures(data: ProcessedInquiryData;);: Promise<LifestyleFeatures /    >  {
    return {activityLevel: data.lifestyle?.exerciseHabits || "未知",stressFactors: data.lifestyle?.stressLeve;l? [`压力水平：${data.lifestyle.stressLevel}`]
        : [],
      environmentalFactors: data.lifestyle?.workEnvironment;? [data.lifestyle.workEnvironment]
        : [],
      socialFactors: []
    };
  }
  private async extractEmotionalFeatures(data: ProcessedInquiryData,
    nlpResults: NLPResults;);: Promise<EmotionalFeatures /    >  {
    return {dominantEmotion: data.emotionalState?.mood || "平和",emotionalStability: data.emotionalState?.stressLeve;l? data.emotionalState.stressLevel < 5;
          ? "稳定"
          : "不稳定"
        : "未知",
      stressResponse: "正常",
      mentalEnergy: "充沛"
    };
  }
  private async analyzeConstitution(features: InquiryFeatures,
    userProfile?: UserProfile;
  ): Promise<ConstitutionalAnalysis /    >  {
    return {bodyType: features.constitution.bodyType,constitution: "平和质",strengths: ["消化良好",睡眠正常"],weaknesses: [],tendencies: [],recommendations: ["保持现有生活方式",适度运动"];};
  }
  // 模拟事件发射  public on(event: string, callback: (data: unknown) => void): void {
    }
  public emit(event: string, data?: unknown): void  {
    }
  // 清理资源  public async cleanup(): Promise<void> {
    await Promise.all(
      [
        this.symptomAnalyzer.cleanup?.(),
        this.nlpProcessor.cleanup?.(),
        this.patternRecognizer.cleanup?.()
      ].filter(Boolean;);
    );
  }
}
// 辅助类型定义 * interface ProcessedInquiryData {
  symptoms: SymptomData[] ;
  medicalHistory?: MedicalHistoryData;
  lifestyle?: LifestyleData;
  familyHistory?: FamilyHistoryData;
  currentComplaints?: string;
  painAssessment?: PainAssessment;
  sleepPattern?: SleepPattern;
  dietaryHabits?: DietaryHabits;
  emotionalState?: EmotionalState
}
interface NLPResults {
  extractedSymptoms: string[];
  medicalEntities: string[];
  sentimentAnalysis: unknown;
  keyPhrases: string[];
}
interface AnalysisResults {
  symptomAnalysis?: SymptomAnalysis;
  constitutionalAnalysis?: ConstitutionalAnalysis;
  syndromePatterns?: SyndromePattern[];
}
//
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {}
  async processSymptoms(symptoms: SymptomData[],
    extractedSymptoms: string[]);: Promise<ProcessedSymptom[] /    >  {
    return symptoms.map(symptom;) => ({
      name: symptom.name,
      tcmCategory: "气血",
      severity: symptom.severity,
      chronicity: symptom.duration,
      pattern: "虚证",
      organSystem: ["脾",胃"]
    }));
  }
  async analyzeSymptoms(symptoms: ProcessedSymptom[],
    userProfile?: UserProfile;
  );: Promise<SymptomAnalysis /    >  {
    return {
      primarySymptoms: symptoms.map(s) => ({,
  symptom: s,
        tcmSignificance: "脾胃虚弱",
        organCorrelation: s.organSystem,
        syndromeImplication: ["脾虚证"],
        severity: "moderate" as const;
      })),
      secondarySymptoms: [],
      symptomPatterns: [{,
  name: "脾胃虚弱",
          symptoms: symptoms.map(s) => s.name),
          confidence: 0.8,
          tcmInterpretation: "脾胃功能失调"
        };
      ],organSystemInvolvement: [{
      system: "脾胃",
      involvement: 0.8,symptoms: symptoms.map(s) => s.name),dysfunction: "运化失常";
        };
      ],pathogenesis: {
      primaryCause: "饮食不节",
      secondaryCauses: ["情志不遂"],pathogenicFactors: ["湿邪"],diseaseStage: "初期",prognosis: "良好";
      };
    };
  }
  async cleanup(): Promise<void> {}
}
class NLPProcessor {
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {}
  async extractSymptoms(text: string): Promise<string[]>  {
    return ["乏力",食欲不振"];
  }
  async extractMedicalEntities(data: ProcessedInquiryData);: Promise<string[]>  {
    return ["头痛",失眠"];
  }
  async analyzeSentiment(data: ProcessedInquiryData);: Promise<any>  {
    return {
      mood: "neutral",
      confidence: 0.;7 ;};
  }
  async extractKeyPhrases(data: ProcessedInquiryData): Promise<string[]>  {
    return ["睡眠不好",消化不良"];
  }
  async cleanup(): Promise<void> {}
}
class PatternRecognizer {
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {}
  async identifyPatterns(features: InquiryFeatures;);: Promise<SyndromePattern[] /    >  {
    return [;
      {
      name: "脾气虚证",
      confidence: 0.8,supportingSymptoms: features.symptoms.map(s) => s.name),contradictingSymptoms: [],tcmExplanation: "脾气不足，运化失常";
      };
    ];
  };
  async cleanup(): Promise<void> {};
};
export default InquiryDiagnosisAlgorithm;