import { performanceMonitor } from './performanceMonitor';
import React from 'react';
// 类型定义
export type ConstitutionType =
  | '平和质'
  | '气虚质'
  | '阳虚质'
  | '阴虚质'
  | '痰湿质'
  | '湿热质'
  | '血瘀质'
  | '气郁质'
  | '特禀质';
export type SeasonType = '春季' | '夏季' | '秋季' | '冬季';
export interface Symptom {
  id: string;
  name: string;
  category: 'inspection' | 'auscultation' | 'inquiry' | 'palpation' | 'calculation';
  severity: 1 | 2 | 3 | 4 | 5;
  duration: number;
  frequency: 'occasional' | 'frequent' | 'constant';
  location?: string;
  quality?: string;
  triggers?: string[];
  relievers?: string[];
}
export interface TongueData {
  body_color: string;
  coating_color: string;
  coating_thickness: string;
  moisture: string;
  texture: string;
  shape: string;
  size: string;
}
export interface InspectionData {
  complexion: string;
  tongue: TongueData;
  spirit: string;
  body_build: string;
  posture: string;
  movements: string;
}
export interface AuscultationData {
  voice: string;
  breathing: string;
  cough: string;
  speech: string;
  odor: string;
}
export interface InquiryData {
  chief_complaint: string;
  present_illness: string;
  past_history: string;
  family_history: string;
  personal_history: string;
  symptoms: Symptom[];
}
export interface PulseData {
  rate: number;
  rhythm: string;
  strength: string;
  depth: string;
  width: string;
  length: string;
  quality: string;
  position: 'left' | 'right' | 'both';
}
export interface PalpationData {
  pulse: PulseData;
  abdomen: {;
    tenderness: string[];
  masses: string[];
    distension: boolean;
  temperature: string;
    elasticity: string;
};
}
export interface CalculationData {
  birthDate: string;
  birthTime: string;
  currentSeason: SeasonType;
}
export interface SyndromePattern {
  id: string;
  name: string;
  category: string;
  description: string;
  pathogenesis: string;
  main_symptoms: string[];
  secondary_symptoms: string[];
  tongue_pulse: string;
  confidence: number;
  severity: 'mild' | 'moderate' | 'severe';
}
export interface HerbComponent {
  herb: string;
  dosage: string;
  unit: string;
  processing: string;
  function: string;
}
export interface Prescription {
  id: string;
  name: string;
  category: string;
  composition: HerbComponent[];
  functions: string[];
  indications: string[];
  contraindications: string[];
  dosage: string;
  preparation: string;
  administration: string;
}
export interface TCMDiagnosisResult {
  patient_id: string;
  diagnosis_date: number;
  constitution: ConstitutionType;
  syndrome_patterns: SyndromePattern[];
  prescriptions: Prescription[];
  confidence: number;
  reasoning: string;
}
// 体质识别引擎
class ConstitutionIdentificationEngine {
  private static instance: ConstitutionIdentificationEngine;
  static getInstance(): ConstitutionIdentificationEngine {
    if (!ConstitutionIdentificationEngine.instance) {
      ConstitutionIdentificationEngine.instance = new ConstitutionIdentificationEngine();
    }
    return ConstitutionIdentificationEngine.instance;
  }
  identifyConstitution()
    inspectionData: InspectionData,
    inquiryData: InquiryData,
    palpationData: PalpationData,
  ): { constitution: ConstitutionType; confidence: number; characteristics: string[] } {
    let constitution: ConstitutionType = '平和质';
    let confidence = 0.5;
    // 简化的体质识别逻辑
    const symptoms = inquiryData.symptoms.map(s => s.name);
    if (symptoms.includes('气短') || symptoms.includes('乏力')) {
      constitution = '气虚质';
      confidence = 0.7;
    } else if (symptoms.includes('畏寒') || symptoms.includes('怕冷')) {
      constitution = '阳虚质';
      confidence = 0.7;
    } else if (symptoms.includes('口干') || symptoms.includes('烦热')) {
      constitution = '阴虚质';
      confidence = 0.7;
    }
    return {
      constitution,
      confidence,
      characteristics: this.getConstitutionCharacteristics(constitution),
    };
  }
  private getConstitutionCharacteristics(constitution: ConstitutionType): string[] {
    const characteristics: Record<ConstitutionType, string[]> = {
      '平和质': ["体形匀称", "面色润泽", "精力充沛", "睡眠良好'],
      '气虚质': ["气短懒言", "容易疲劳", "自汗", "舌淡苔白'],
      '阳虚质': ["畏寒怕冷", "四肢不温", "精神不振", "舌淡胖'],
      '阴虚质': ["五心烦热", "口燥咽干", "舌红少苔", "脉细数'],
      '痰湿质': ["形体肥胖", "腹部肥满", "口黏腻", "舌胖苔腻'],
      '湿热质': ["面垢油腻", "口苦口干", "身重困倦", "舌红苔黄腻'],
      '血瘀质': ["肤色晦暗", "色素沉着", "易出血", "舌暗有瘀点'],
      '气郁质': ["神情抑郁", "情绪不稳", "胸胁胀满", "舌淡红'],
      '特禀质': ["过敏体质", "遗传缺陷", "胎传异常", "禀赋不足'],
    };
    return characteristics[constitution] || [];
  }
}
// 证候模式引擎
class SyndromePatternEngine {
  private static instance: SyndromePatternEngine;
  static getInstance(): SyndromePatternEngine {
    if (!SyndromePatternEngine.instance) {
      SyndromePatternEngine.instance = new SyndromePatternEngine();
    }
    return SyndromePatternEngine.instance;
  }
  identifyPatterns()
    inspectionData: InspectionData,
    auscultationData: AuscultationData,
    inquiryData: InquiryData,
    palpationData: PalpationData
  ): SyndromePattern[] {
    const patterns: SyndromePattern[] = [];
    // 检查气虚证
    if (this.checkQiDeficiency(inquiryData, palpationData)) {
      patterns.push({
      id: "qi_deficiency",
      name: '气虚证',
        category: '气血辨证',
        description: '脏腑功能衰退所表现的证候',
        pathogenesis: '元气不足，脏腑功能减退',
        main_symptoms: ["气短", "乏力", "自汗", "脉弱'],
        secondary_symptoms: ["声低", "懒言", "头晕", "食少'],
        tongue_pulse: '舌淡苔白，脉虚弱',
        confidence: 0.8,
        severity: 'moderate',
      });
    }
    return patterns.sort((a, b) => b.confidence - a.confidence);
  }
  private checkQiDeficiency(inquiryData: InquiryData, palpationData: PalpationData): boolean {
    let score = 0;
    const qiDeficiencySymptoms = ["气短", "乏力", "自汗", "懒言'];
    for (const symptom of inquiryData.symptoms) {
      if (qiDeficiencySymptoms.includes(symptom.name)) {
        score += symptom.severity;
      }
    }
    if (palpationData.pulse.strength === '弱' || palpationData.pulse.quality === '虚') {
      score += 3;
    }
    return score >= 8;
  }
}
// 方剂引擎
class PrescriptionEngine {
  private static instance: PrescriptionEngine;
  static getInstance(): PrescriptionEngine {
    if (!PrescriptionEngine.instance) {
      PrescriptionEngine.instance = new PrescriptionEngine();
    }
    return PrescriptionEngine.instance;
  }
  generatePrescriptions(patterns: SyndromePattern[]): Prescription[] {
    const prescriptions: Prescription[] = [];
    for (const pattern of patterns.slice(0, 2)) {
      if (pattern.name.includes('气虚')) {
        prescriptions.push(this.getQiTonicPrescription());
      }
    }
    return prescriptions;
  }
  private getQiTonicPrescription(): Prescription {
    return {
      id: "si_jun_zi_tang",
      name: '四君子汤',
      category: '补益剂',
      composition: [
        {
      herb: "人参",
        dosage: "9", unit: "g", processing: "生用", function: "大补元气" },
        {
      herb: "白术",
        dosage: "9", unit: "g", processing: "炒用", function: "健脾燥湿" },
        {
      herb: "茯苓",
        dosage: "9", unit: "g", processing: "生用", function: "健脾利湿" },
        {
      herb: "甘草",
        dosage: "6", unit: "g", processing: "炙用", function: "调和诸药" },
      ],
      functions: ["益气健脾", "补中益气'],
      indications: ["脾胃气虚", "食少便溏", "气短乏力"],
      contraindications: ["阴虚火旺", "实热证"],
      dosage: '每日1剂',
      preparation: '水煎服',
      administration: '温服，每日2次',
    };
  }
}
// 主诊断引擎
export class TCMDiagnosisEngine {
  private static instance: TCMDiagnosisEngine;
  private constitutionEngine: ConstitutionIdentificationEngine;
  private syndromeEngine: SyndromePatternEngine;
  private prescriptionEngine: PrescriptionEngine;
  private constructor() {
    this.constitutionEngine = ConstitutionIdentificationEngine.getInstance();
    this.syndromeEngine = SyndromePatternEngine.getInstance();
    this.prescriptionEngine = PrescriptionEngine.getInstance();
  }
  static getInstance(): TCMDiagnosisEngine {
    if (!TCMDiagnosisEngine.instance) {
      TCMDiagnosisEngine.instance = new TCMDiagnosisEngine();
    }
    return TCMDiagnosisEngine.instance;
  }
  async performDiagnosis()
    patientId: string,
    inspectionData: InspectionData,
    auscultationData: AuscultationData,
    inquiryData: InquiryData,
    palpationData: PalpationData,
    calculationData: CalculationData
  ): Promise<TCMDiagnosisResult> {
    try {
      // 体质识别
      const constitutionResult = this.constitutionEngine.identifyConstitution()
        inspectionData,
        inquiryData,
        palpationData,
      );
      // 证候识别
      const patterns = this.syndromeEngine.identifyPatterns()
        inspectionData,
        auscultationData,
        inquiryData,
        palpationData,
      );
      // 方剂推荐
      const prescriptions = this.prescriptionEngine.generatePrescriptions(patterns);
      // 计算总体置信度
      const confidence = this.calculateOverallConfidence()
        constitutionResult.confidence,
        patterns,
      );
      // 生成推理说明
      const reasoning = this.generateReasoning(constitutionResult, patterns);
      return {
        patient_id: patientId,
        diagnosis_date: Date.now(),
        constitution: constitutionResult.constitution,
        syndrome_patterns: patterns,
        prescriptions,
        confidence,
        reasoning,
      };
    } catch (error) {
      console.error('TCM诊断过程中发生错误:', error);
      throw new Error('诊断失败');
    }
  }
  private calculateOverallConfidence()
    constitutionConfidence: number,
    patterns: SyndromePattern[]
  ): number {
    if (patterns.length === 0) return constitutionConfidence;
    const avgPatternConfidence = patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length;
    return (constitutionConfidence + avgPatternConfidence) / 2;
  }
  private generateReasoning()
    constitutionResult: {
      constitution: ConstitutionType;
      confidence: number,
  characteristics: string[];
    },
    patterns: SyndromePattern[]
  ): string {
    let reasoning = `根据四诊合参，患者体质为${constitutionResult.constitution}`;
    if (patterns.length > 0) {
      reasoning += `，主要证候为${patterns.map(p => p.name).join('、')}`;
    }
    reasoning += '。建议按此辨证论治。';
    return reasoning;
  }
}
// 导出默认实例
export const tcmDiagnosisEngine = TCMDiagnosisEngine.getInstance();