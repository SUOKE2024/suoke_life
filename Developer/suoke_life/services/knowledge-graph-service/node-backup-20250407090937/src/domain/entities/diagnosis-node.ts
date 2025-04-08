/**
 * 诊断节点类
 * 继承自TCM节点类，专门用于表示中医诊断
 */

import { TCMNode, TCMNodeProperties, TCMNodeImpl } from './tcm-node';

export type DiagnosisCategory = 
  | 'syndrome' 
  | 'pattern' 
  | 'disease' 
  | 'condition' 
  | 'disharmony' 
  | 'stage';

export interface DiagnosticEvidence {
  inspection?: {
    face?: string[];
    tongue?: {
      body?: string[];
      coating?: string[];
      shape?: string[];
      movement?: string[];
    };
    body?: string[];
    nails?: string[];
    eyes?: string[];
    skin?: string[];
  };
  auscultation_olfaction?: {
    voice?: string[];
    breathing?: string[];
    cough?: string[];
    odor?: string[];
  };
  inquiry?: {
    main_complaint?: string[];
    history?: string[];
    sleep?: string[];
    temperature?: string[];
    sweat?: string[];
    pain?: string[];
    head?: string[];
    chest?: string[];
    abdomen?: string[];
    urine?: string[];
    stool?: string[];
    thirst?: string[];
    taste?: string[];
    appetite?: string[];
    gynecological?: string[];
  };
  palpation?: {
    pulse?: {
      position?: string[];
      quality?: string[];
      rhythm?: string[];
      strength?: string[];
    };
    abdomen?: string[];
    channels?: string[];
    acupoints?: string[];
    skin?: string[];
  };
}

export interface DiagnosisProperties {
  englishName?: string;
  pinyin?: string;
  diagnosticCategory: DiagnosisCategory;
  etiology: string[];
  pathogenesis: string[];
  diagnosticEvidence: DiagnosticEvidence;
  differentialDiagnosis?: Array<{
    diagnosisName: string;
    keyDifferences: string[];
  }>;
  tcm_principles_of_treatment: string[];
  treatment_methods?: string[];
  recommended_formulas?: string[];
  recommended_herbs?: string[];
  recommended_acupoints?: string[];
  prognosis?: string;
  complications?: string[];
  preventionAdvice?: string[];
  related_western_diagnoses?: string[];
  classification?: {
    sixStages?: 'taiyang' | 'yangming' | 'shaoyang' | 'taiyin' | 'shaoyin' | 'jueyin';
    fourLevels?: 'wei' | 'qi' | 'ying' | 'xue';
    sanJiao?: 'upper' | 'middle' | 'lower';
    eightPrinciples?: {
      interior_exterior?: 'interior' | 'exterior';
      cold_heat?: 'cold' | 'heat';
      deficiency_excess?: 'deficiency' | 'excess';
      yin_yang?: 'yin' | 'yang';
    };
    zangFu?: string[];
  };
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  clinicalPracticeGuidelines?: string[];
  cases?: Array<{
    description: string;
    treatment: string;
    outcome: string;
    source?: string;
  }>;
}

export interface DiagnosisNode extends TCMNode {
  englishName?: string;
  pinyin?: string;
  diagnosticCategory: DiagnosisCategory;
  etiology: string[];
  pathogenesis: string[];
  diagnosticEvidence: DiagnosticEvidence;
  differentialDiagnosis?: Array<{
    diagnosisName: string;
    keyDifferences: string[];
  }>;
  tcm_principles_of_treatment: string[];
  treatment_methods?: string[];
  recommended_formulas?: string[];
  recommended_herbs?: string[];
  recommended_acupoints?: string[];
  prognosis?: string;
  complications?: string[];
  preventionAdvice?: string[];
  related_western_diagnoses?: string[];
  classification?: {
    sixStages?: 'taiyang' | 'yangming' | 'shaoyang' | 'taiyin' | 'shaoyin' | 'jueyin';
    fourLevels?: 'wei' | 'qi' | 'ying' | 'xue';
    sanJiao?: 'upper' | 'middle' | 'lower';
    eightPrinciples?: {
      interior_exterior?: 'interior' | 'exterior';
      cold_heat?: 'cold' | 'heat';
      deficiency_excess?: 'deficiency' | 'excess';
      yin_yang?: 'yin' | 'yang';
    };
    zangFu?: string[];
  };
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  clinicalPracticeGuidelines?: string[];
  cases?: Array<{
    description: string;
    treatment: string;
    outcome: string;
    source?: string;
  }>;
}

export interface DiagnosisNodeProperties extends TCMNodeProperties, DiagnosisProperties {}

export class DiagnosisNodeImpl extends TCMNodeImpl implements DiagnosisNode {
  englishName?: string;
  pinyin?: string;
  diagnosticCategory: DiagnosisCategory;
  etiology: string[];
  pathogenesis: string[];
  diagnosticEvidence: DiagnosticEvidence;
  differentialDiagnosis?: Array<{
    diagnosisName: string;
    keyDifferences: string[];
  }>;
  tcm_principles_of_treatment: string[];
  treatment_methods?: string[];
  recommended_formulas?: string[];
  recommended_herbs?: string[];
  recommended_acupoints?: string[];
  prognosis?: string;
  complications?: string[];
  preventionAdvice?: string[];
  related_western_diagnoses?: string[];
  classification?: {
    sixStages?: 'taiyang' | 'yangming' | 'shaoyang' | 'taiyin' | 'shaoyin' | 'jueyin';
    fourLevels?: 'wei' | 'qi' | 'ying' | 'xue';
    sanJiao?: 'upper' | 'middle' | 'lower';
    eightPrinciples?: {
      interior_exterior?: 'interior' | 'exterior';
      cold_heat?: 'cold' | 'heat';
      deficiency_excess?: 'deficiency' | 'excess';
      yin_yang?: 'yin' | 'yang';
    };
    zangFu?: string[];
  };
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  clinicalPracticeGuidelines?: string[];
  cases?: Array<{
    description: string;
    treatment: string;
    outcome: string;
    source?: string;
  }>;

  constructor(props: DiagnosisNodeProperties) {
    super({
      ...props,
      category: 'diagnosis'
    });

    this.englishName = props.englishName;
    this.pinyin = props.pinyin;
    this.diagnosticCategory = props.diagnosticCategory;
    this.etiology = props.etiology;
    this.pathogenesis = props.pathogenesis;
    this.diagnosticEvidence = props.diagnosticEvidence;
    this.differentialDiagnosis = props.differentialDiagnosis;
    this.tcm_principles_of_treatment = props.tcm_principles_of_treatment;
    this.treatment_methods = props.treatment_methods;
    this.recommended_formulas = props.recommended_formulas;
    this.recommended_herbs = props.recommended_herbs;
    this.recommended_acupoints = props.recommended_acupoints;
    this.prognosis = props.prognosis;
    this.complications = props.complications;
    this.preventionAdvice = props.preventionAdvice;
    this.related_western_diagnoses = props.related_western_diagnoses;
    this.classification = props.classification;
    this.modernResearch = props.modernResearch;
    this.clinicalPracticeGuidelines = props.clinicalPracticeGuidelines;
    this.cases = props.cases;
  }

  override update(props: Partial<DiagnosisNodeProperties>): void {
    super.update(props);

    if (props.englishName) this.englishName = props.englishName;
    if (props.pinyin) this.pinyin = props.pinyin;
    if (props.diagnosticCategory) this.diagnosticCategory = props.diagnosticCategory;
    if (props.etiology) this.etiology = props.etiology;
    if (props.pathogenesis) this.pathogenesis = props.pathogenesis;
    if (props.diagnosticEvidence) this.diagnosticEvidence = props.diagnosticEvidence;
    if (props.differentialDiagnosis) this.differentialDiagnosis = props.differentialDiagnosis;
    if (props.tcm_principles_of_treatment) this.tcm_principles_of_treatment = props.tcm_principles_of_treatment;
    if (props.treatment_methods) this.treatment_methods = props.treatment_methods;
    if (props.recommended_formulas) this.recommended_formulas = props.recommended_formulas;
    if (props.recommended_herbs) this.recommended_herbs = props.recommended_herbs;
    if (props.recommended_acupoints) this.recommended_acupoints = props.recommended_acupoints;
    if (props.prognosis) this.prognosis = props.prognosis;
    if (props.complications) this.complications = props.complications;
    if (props.preventionAdvice) this.preventionAdvice = props.preventionAdvice;
    if (props.related_western_diagnoses) this.related_western_diagnoses = props.related_western_diagnoses;
    if (props.classification) this.classification = props.classification;
    if (props.modernResearch) this.modernResearch = props.modernResearch;
    if (props.clinicalPracticeGuidelines) this.clinicalPracticeGuidelines = props.clinicalPracticeGuidelines;
    if (props.cases) this.cases = props.cases;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      englishName: this.englishName,
      pinyin: this.pinyin,
      diagnosticCategory: this.diagnosticCategory,
      etiology: this.etiology,
      pathogenesis: this.pathogenesis,
      diagnosticEvidence: this.diagnosticEvidence,
      differentialDiagnosis: this.differentialDiagnosis,
      tcm_principles_of_treatment: this.tcm_principles_of_treatment,
      treatment_methods: this.treatment_methods,
      recommended_formulas: this.recommended_formulas,
      recommended_herbs: this.recommended_herbs,
      recommended_acupoints: this.recommended_acupoints,
      prognosis: this.prognosis,
      complications: this.complications,
      preventionAdvice: this.preventionAdvice,
      related_western_diagnoses: this.related_western_diagnoses,
      classification: this.classification,
      modernResearch: this.modernResearch,
      clinicalPracticeGuidelines: this.clinicalPracticeGuidelines,
      cases: this.cases
    };
  }
} 