/**
 * 现代医学节点类
 * 继承自基础节点类，专门用于表示现代医学概念
 */

import { BaseNode, BaseNodeProperties, BaseNodeImpl } from './base-node';

export type ModernMedicineNodeType = 
  | 'disease' 
  | 'drug' 
  | 'therapy' 
  | 'test' 
  | 'anatomical_structure' 
  | 'physiological_process' 
  | 'pathological_process' 
  | 'medical_device' 
  | 'biomarker';

export interface ModernMedicineProperties {
  nodeType: ModernMedicineNodeType;
  scientificName?: string;
  alternativeNames?: string[];
  medicalDefinition: string;
  icd10Code?: string[];
  icd11Code?: string[];
  snomedCtCode?: string[];
  etiology?: string[];
  epidemiology?: {
    prevalence?: string;
    incidence?: string;
    demographics?: string;
    riskFactors?: string[];
  };
  pathophysiology?: string;
  clinicalPresentation?: {
    symptoms?: string[];
    signs?: string[];
    stages?: Array<{
      name: string;
      description: string;
      characteristics: string[];
    }>;
  };
  diagnosticCriteria?: {
    laboratoryFindings?: string[];
    imagingFindings?: string[];
    clinicalCriteria?: string[];
    differentialDiagnosis?: string[];
  };
  treatmentOptions?: Array<{
    type: 'pharmacological' | 'surgical' | 'lifestyle' | 'physical' | 'psychological' | 'other';
    name: string;
    description: string;
    evidenceLevel?: 
      | 'high_quality_evidence' 
      | 'moderate_quality_evidence' 
      | 'low_quality_evidence' 
      | 'very_low_quality_evidence' 
      | 'expert_opinion';
    recommendationGrade?: 'strong' | 'conditional' | 'weak';
  }>;
  clinicalGuidelines?: Array<{
    organization: string;
    title: string;
    year: number;
    url?: string;
    key_recommendations: string[];
  }>;
  scientificResearch?: Array<{
    title: string;
    authors: string[];
    journal: string;
    year: number;
    doi?: string;
    conclusions: string;
    type: 'rct' | 'meta_analysis' | 'systematic_review' | 'cohort_study' | 'case_control' | 'case_series' | 'other';
  }>;
  interactions?: Array<{
    withType: 'drug' | 'food' | 'herb' | 'supplement' | 'disease' | 'condition';
    name: string;
    effect: string;
    mechanism?: string;
    severity: 'minor' | 'moderate' | 'major' | 'contraindicated';
    evidence?: string;
  }>;
  tcmCorrespondence?: {
    relatedTCMConcepts?: string[];
    integrationApproaches?: string[];
    comparativeEfficacy?: string;
  };
}

export interface ModernMedicineNode extends BaseNode {
  nodeType: ModernMedicineNodeType;
  scientificName?: string;
  alternativeNames?: string[];
  medicalDefinition: string;
  icd10Code?: string[];
  icd11Code?: string[];
  snomedCtCode?: string[];
  etiology?: string[];
  epidemiology?: {
    prevalence?: string;
    incidence?: string;
    demographics?: string;
    riskFactors?: string[];
  };
  pathophysiology?: string;
  clinicalPresentation?: {
    symptoms?: string[];
    signs?: string[];
    stages?: Array<{
      name: string;
      description: string;
      characteristics: string[];
    }>;
  };
  diagnosticCriteria?: {
    laboratoryFindings?: string[];
    imagingFindings?: string[];
    clinicalCriteria?: string[];
    differentialDiagnosis?: string[];
  };
  treatmentOptions?: Array<{
    type: 'pharmacological' | 'surgical' | 'lifestyle' | 'physical' | 'psychological' | 'other';
    name: string;
    description: string;
    evidenceLevel?: 
      | 'high_quality_evidence' 
      | 'moderate_quality_evidence' 
      | 'low_quality_evidence' 
      | 'very_low_quality_evidence' 
      | 'expert_opinion';
    recommendationGrade?: 'strong' | 'conditional' | 'weak';
  }>;
  clinicalGuidelines?: Array<{
    organization: string;
    title: string;
    year: number;
    url?: string;
    key_recommendations: string[];
  }>;
  scientificResearch?: Array<{
    title: string;
    authors: string[];
    journal: string;
    year: number;
    doi?: string;
    conclusions: string;
    type: 'rct' | 'meta_analysis' | 'systematic_review' | 'cohort_study' | 'case_control' | 'case_series' | 'other';
  }>;
  interactions?: Array<{
    withType: 'drug' | 'food' | 'herb' | 'supplement' | 'disease' | 'condition';
    name: string;
    effect: string;
    mechanism?: string;
    severity: 'minor' | 'moderate' | 'major' | 'contraindicated';
    evidence?: string;
  }>;
  tcmCorrespondence?: {
    relatedTCMConcepts?: string[];
    integrationApproaches?: string[];
    comparativeEfficacy?: string;
  };
}

export interface ModernMedicineNodeProperties extends BaseNodeProperties, ModernMedicineProperties {}

export class ModernMedicineNodeImpl extends BaseNodeImpl implements ModernMedicineNode {
  nodeType: ModernMedicineNodeType;
  scientificName?: string;
  alternativeNames?: string[];
  medicalDefinition: string;
  icd10Code?: string[];
  icd11Code?: string[];
  snomedCtCode?: string[];
  etiology?: string[];
  epidemiology?: {
    prevalence?: string;
    incidence?: string;
    demographics?: string;
    riskFactors?: string[];
  };
  pathophysiology?: string;
  clinicalPresentation?: {
    symptoms?: string[];
    signs?: string[];
    stages?: Array<{
      name: string;
      description: string;
      characteristics: string[];
    }>;
  };
  diagnosticCriteria?: {
    laboratoryFindings?: string[];
    imagingFindings?: string[];
    clinicalCriteria?: string[];
    differentialDiagnosis?: string[];
  };
  treatmentOptions?: Array<{
    type: 'pharmacological' | 'surgical' | 'lifestyle' | 'physical' | 'psychological' | 'other';
    name: string;
    description: string;
    evidenceLevel?: 
      | 'high_quality_evidence' 
      | 'moderate_quality_evidence' 
      | 'low_quality_evidence' 
      | 'very_low_quality_evidence' 
      | 'expert_opinion';
    recommendationGrade?: 'strong' | 'conditional' | 'weak';
  }>;
  clinicalGuidelines?: Array<{
    organization: string;
    title: string;
    year: number;
    url?: string;
    key_recommendations: string[];
  }>;
  scientificResearch?: Array<{
    title: string;
    authors: string[];
    journal: string;
    year: number;
    doi?: string;
    conclusions: string;
    type: 'rct' | 'meta_analysis' | 'systematic_review' | 'cohort_study' | 'case_control' | 'case_series' | 'other';
  }>;
  interactions?: Array<{
    withType: 'drug' | 'food' | 'herb' | 'supplement' | 'disease' | 'condition';
    name: string;
    effect: string;
    mechanism?: string;
    severity: 'minor' | 'moderate' | 'major' | 'contraindicated';
    evidence?: string;
  }>;
  tcmCorrespondence?: {
    relatedTCMConcepts?: string[];
    integrationApproaches?: string[];
    comparativeEfficacy?: string;
  };

  constructor(props: ModernMedicineNodeProperties) {
    super({
      ...props,
      category: `modern_medicine_${props.nodeType}`
    });

    this.nodeType = props.nodeType;
    this.scientificName = props.scientificName;
    this.alternativeNames = props.alternativeNames;
    this.medicalDefinition = props.medicalDefinition;
    this.icd10Code = props.icd10Code;
    this.icd11Code = props.icd11Code;
    this.snomedCtCode = props.snomedCtCode;
    this.etiology = props.etiology;
    this.epidemiology = props.epidemiology;
    this.pathophysiology = props.pathophysiology;
    this.clinicalPresentation = props.clinicalPresentation;
    this.diagnosticCriteria = props.diagnosticCriteria;
    this.treatmentOptions = props.treatmentOptions;
    this.clinicalGuidelines = props.clinicalGuidelines;
    this.scientificResearch = props.scientificResearch;
    this.interactions = props.interactions;
    this.tcmCorrespondence = props.tcmCorrespondence;
  }

  override update(props: Partial<ModernMedicineNodeProperties>): void {
    super.update(props);

    if (props.nodeType) this.nodeType = props.nodeType;
    if (props.scientificName) this.scientificName = props.scientificName;
    if (props.alternativeNames) this.alternativeNames = props.alternativeNames;
    if (props.medicalDefinition) this.medicalDefinition = props.medicalDefinition;
    if (props.icd10Code) this.icd10Code = props.icd10Code;
    if (props.icd11Code) this.icd11Code = props.icd11Code;
    if (props.snomedCtCode) this.snomedCtCode = props.snomedCtCode;
    if (props.etiology) this.etiology = props.etiology;
    if (props.epidemiology) this.epidemiology = props.epidemiology;
    if (props.pathophysiology) this.pathophysiology = props.pathophysiology;
    if (props.clinicalPresentation) this.clinicalPresentation = props.clinicalPresentation;
    if (props.diagnosticCriteria) this.diagnosticCriteria = props.diagnosticCriteria;
    if (props.treatmentOptions) this.treatmentOptions = props.treatmentOptions;
    if (props.clinicalGuidelines) this.clinicalGuidelines = props.clinicalGuidelines;
    if (props.scientificResearch) this.scientificResearch = props.scientificResearch;
    if (props.interactions) this.interactions = props.interactions;
    if (props.tcmCorrespondence) this.tcmCorrespondence = props.tcmCorrespondence;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      nodeType: this.nodeType,
      scientificName: this.scientificName,
      alternativeNames: this.alternativeNames,
      medicalDefinition: this.medicalDefinition,
      icd10Code: this.icd10Code,
      icd11Code: this.icd11Code,
      snomedCtCode: this.snomedCtCode,
      etiology: this.etiology,
      epidemiology: this.epidemiology,
      pathophysiology: this.pathophysiology,
      clinicalPresentation: this.clinicalPresentation,
      diagnosticCriteria: this.diagnosticCriteria,
      treatmentOptions: this.treatmentOptions,
      clinicalGuidelines: this.clinicalGuidelines,
      scientificResearch: this.scientificResearch,
      interactions: this.interactions,
      tcmCorrespondence: this.tcmCorrespondence
    };
  }
} 