/**
 * 症状节点类
 * 继承自TCM节点类，专门用于表示中医症状
 */

import { TCMNode, TCMNodeProperties, TCMNodeImpl } from './tcm-node';

export interface SymptomProperties {
  pinyin?: string;
  englishName?: string;
  bodyRegion?: string[];
  severity?: 'mild' | 'moderate' | 'severe';
  manifestation: {
    observable: string[];
    subjective?: string[];
  };
  associated: {
    disharmonies?: string[];
    organs?: string[];
    meridians?: string[];
    emotions?: string[];
    pathogens?: string[];
  };
  differentialDiagnosis?: Array<{
    name: string;
    distinguishingFeatures: string[];
  }>;
  relevantTreatmentMethods?: string[];
  relevantHerbs?: string[];
  relevantPrescriptions?: string[];
  relevantAcupoints?: string[];
  relevantCases?: string[];
  progressiveStages?: Array<{
    stage: string;
    description: string;
    indicators: string[];
  }>;
  westernMedicalCorrelation?: {
    relatedConditions?: string[];
    pathophysiology?: string;
    researchFindings?: string[];
  };
  prognosis?: {
    timelineDescription: string;
    favorableOutcome: string[];
    unfavorableOutcome: string[];
    chronicity: 'acute' | 'subacute' | 'chronic' | 'recurrent';
  };
}

export interface SymptomNode extends TCMNode {
  pinyin?: string;
  englishName?: string;
  bodyRegion?: string[];
  severity?: 'mild' | 'moderate' | 'severe';
  manifestation: {
    observable: string[];
    subjective?: string[];
  };
  associated: {
    disharmonies?: string[];
    organs?: string[];
    meridians?: string[];
    emotions?: string[];
    pathogens?: string[];
  };
  differentialDiagnosis?: Array<{
    name: string;
    distinguishingFeatures: string[];
  }>;
  relevantTreatmentMethods?: string[];
  relevantHerbs?: string[];
  relevantPrescriptions?: string[];
  relevantAcupoints?: string[];
  relevantCases?: string[];
  progressiveStages?: Array<{
    stage: string;
    description: string;
    indicators: string[];
  }>;
  westernMedicalCorrelation?: {
    relatedConditions?: string[];
    pathophysiology?: string;
    researchFindings?: string[];
  };
  prognosis?: {
    timelineDescription: string;
    favorableOutcome: string[];
    unfavorableOutcome: string[];
    chronicity: 'acute' | 'subacute' | 'chronic' | 'recurrent';
  };
}

export interface SymptomNodeProperties extends TCMNodeProperties, SymptomProperties {}

export class SymptomNodeImpl extends TCMNodeImpl implements SymptomNode {
  pinyin?: string;
  englishName?: string;
  bodyRegion?: string[];
  severity?: 'mild' | 'moderate' | 'severe';
  manifestation: {
    observable: string[];
    subjective?: string[];
  };
  associated: {
    disharmonies?: string[];
    organs?: string[];
    meridians?: string[];
    emotions?: string[];
    pathogens?: string[];
  };
  differentialDiagnosis?: Array<{
    name: string;
    distinguishingFeatures: string[];
  }>;
  relevantTreatmentMethods?: string[];
  relevantHerbs?: string[];
  relevantPrescriptions?: string[];
  relevantAcupoints?: string[];
  relevantCases?: string[];
  progressiveStages?: Array<{
    stage: string;
    description: string;
    indicators: string[];
  }>;
  westernMedicalCorrelation?: {
    relatedConditions?: string[];
    pathophysiology?: string;
    researchFindings?: string[];
  };
  prognosis?: {
    timelineDescription: string;
    favorableOutcome: string[];
    unfavorableOutcome: string[];
    chronicity: 'acute' | 'subacute' | 'chronic' | 'recurrent';
  };

  constructor(props: SymptomNodeProperties) {
    super({
      ...props,
      category: 'symptom'
    });

    this.pinyin = props.pinyin;
    this.englishName = props.englishName;
    this.bodyRegion = props.bodyRegion;
    this.severity = props.severity;
    this.manifestation = props.manifestation;
    this.associated = props.associated;
    this.differentialDiagnosis = props.differentialDiagnosis;
    this.relevantTreatmentMethods = props.relevantTreatmentMethods;
    this.relevantHerbs = props.relevantHerbs;
    this.relevantPrescriptions = props.relevantPrescriptions;
    this.relevantAcupoints = props.relevantAcupoints;
    this.relevantCases = props.relevantCases;
    this.progressiveStages = props.progressiveStages;
    this.westernMedicalCorrelation = props.westernMedicalCorrelation;
    this.prognosis = props.prognosis;
  }

  override update(props: Partial<SymptomNodeProperties>): void {
    super.update(props);

    if (props.pinyin) this.pinyin = props.pinyin;
    if (props.englishName) this.englishName = props.englishName;
    if (props.bodyRegion) this.bodyRegion = props.bodyRegion;
    if (props.severity) this.severity = props.severity;
    if (props.manifestation) this.manifestation = props.manifestation;
    if (props.associated) this.associated = props.associated;
    if (props.differentialDiagnosis) this.differentialDiagnosis = props.differentialDiagnosis;
    if (props.relevantTreatmentMethods) this.relevantTreatmentMethods = props.relevantTreatmentMethods;
    if (props.relevantHerbs) this.relevantHerbs = props.relevantHerbs;
    if (props.relevantPrescriptions) this.relevantPrescriptions = props.relevantPrescriptions;
    if (props.relevantAcupoints) this.relevantAcupoints = props.relevantAcupoints;
    if (props.relevantCases) this.relevantCases = props.relevantCases;
    if (props.progressiveStages) this.progressiveStages = props.progressiveStages;
    if (props.westernMedicalCorrelation) this.westernMedicalCorrelation = props.westernMedicalCorrelation;
    if (props.prognosis) this.prognosis = props.prognosis;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      pinyin: this.pinyin,
      englishName: this.englishName,
      bodyRegion: this.bodyRegion,
      severity: this.severity,
      manifestation: this.manifestation,
      associated: this.associated,
      differentialDiagnosis: this.differentialDiagnosis,
      relevantTreatmentMethods: this.relevantTreatmentMethods,
      relevantHerbs: this.relevantHerbs,
      relevantPrescriptions: this.relevantPrescriptions,
      relevantAcupoints: this.relevantAcupoints,
      relevantCases: this.relevantCases,
      progressiveStages: this.progressiveStages,
      westernMedicalCorrelation: this.westernMedicalCorrelation,
      prognosis: this.prognosis
    };
  }
} 