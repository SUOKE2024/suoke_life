/**
 * 体质节点类
 * 继承自TCM节点类，专门用于表示中医体质类型
 */

import { TCMNode, TCMNodeProperties, TCMNodeImpl } from './tcm-node';

export type ConstitutionType = 
  | 'balanced' 
  | 'qi_deficiency' 
  | 'yang_deficiency' 
  | 'yin_deficiency' 
  | 'phlegm_dampness' 
  | 'damp_heat' 
  | 'blood_stasis' 
  | 'qi_stagnation' 
  | 'special';

export interface ConstitutionProperties {
  constitutionType: ConstitutionType;
  englishName?: string;
  pinyin?: string;
  characteristics: {
    physical: string[];
    psychological: string[];
    diseaseDisposition: string[];
  };
  diagnosticCriteria: {
    observation: string[];
    auscultation: string[];
    inquiry: string[];
    pulse: string[];
    tongue: string[];
  };
  treatmentPrinciples: string[];
  lifestyleRecommendations: {
    diet: string[];
    exercise: string[];
    rest: string[];
    environment: string[];
    emotion: string[];
  };
  dietaryAdvice: {
    recommended: string[];
    avoid: string[];
    recipes?: string[];
  };
  seasonalCare?: {
    spring?: string[];
    summer?: string[];
    autumn?: string[];
    winter?: string[];
  };
  developmentalFactors?: string[];
  transformationRules?: {
    potentialTransformations: Array<{
      toType: ConstitutionType;
      causingFactors: string[];
      preventionMeasures: string[];
    }>;
  };
  prevalenceStatistics?: {
    generalPopulation?: number; // 百分比
    ageGroups?: Array<{
      range: string;
      percentage: number;
    }>;
    genderDistribution?: {
      male: number;
      female: number;
    };
    regionalVariation?: Array<{
      region: string;
      percentage: number;
    }>;
  };
  associatedHerbs?: string[];
  associatedPrescriptions?: string[];
  associatedAcupoints?: string[];
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
}

export interface ConstitutionNode extends TCMNode {
  constitutionType: ConstitutionType;
  englishName?: string;
  pinyin?: string;
  characteristics: {
    physical: string[];
    psychological: string[];
    diseaseDisposition: string[];
  };
  diagnosticCriteria: {
    observation: string[];
    auscultation: string[];
    inquiry: string[];
    pulse: string[];
    tongue: string[];
  };
  treatmentPrinciples: string[];
  lifestyleRecommendations: {
    diet: string[];
    exercise: string[];
    rest: string[];
    environment: string[];
    emotion: string[];
  };
  dietaryAdvice: {
    recommended: string[];
    avoid: string[];
    recipes?: string[];
  };
  seasonalCare?: {
    spring?: string[];
    summer?: string[];
    autumn?: string[];
    winter?: string[];
  };
  developmentalFactors?: string[];
  transformationRules?: {
    potentialTransformations: Array<{
      toType: ConstitutionType;
      causingFactors: string[];
      preventionMeasures: string[];
    }>;
  };
  prevalenceStatistics?: {
    generalPopulation?: number; // 百分比
    ageGroups?: Array<{
      range: string;
      percentage: number;
    }>;
    genderDistribution?: {
      male: number;
      female: number;
    };
    regionalVariation?: Array<{
      region: string;
      percentage: number;
    }>;
  };
  associatedHerbs?: string[];
  associatedPrescriptions?: string[];
  associatedAcupoints?: string[];
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
}

export interface ConstitutionNodeProperties extends TCMNodeProperties, ConstitutionProperties {}

export class ConstitutionNodeImpl extends TCMNodeImpl implements ConstitutionNode {
  constitutionType: ConstitutionType;
  englishName?: string;
  pinyin?: string;
  characteristics: {
    physical: string[];
    psychological: string[];
    diseaseDisposition: string[];
  };
  diagnosticCriteria: {
    observation: string[];
    auscultation: string[];
    inquiry: string[];
    pulse: string[];
    tongue: string[];
  };
  treatmentPrinciples: string[];
  lifestyleRecommendations: {
    diet: string[];
    exercise: string[];
    rest: string[];
    environment: string[];
    emotion: string[];
  };
  dietaryAdvice: {
    recommended: string[];
    avoid: string[];
    recipes?: string[];
  };
  seasonalCare?: {
    spring?: string[];
    summer?: string[];
    autumn?: string[];
    winter?: string[];
  };
  developmentalFactors?: string[];
  transformationRules?: {
    potentialTransformations: Array<{
      toType: ConstitutionType;
      causingFactors: string[];
      preventionMeasures: string[];
    }>;
  };
  prevalenceStatistics?: {
    generalPopulation?: number;
    ageGroups?: Array<{
      range: string;
      percentage: number;
    }>;
    genderDistribution?: {
      male: number;
      female: number;
    };
    regionalVariation?: Array<{
      region: string;
      percentage: number;
    }>;
  };
  associatedHerbs?: string[];
  associatedPrescriptions?: string[];
  associatedAcupoints?: string[];
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;

  constructor(props: ConstitutionNodeProperties) {
    super({
      ...props,
      category: 'constitution'
    });

    this.constitutionType = props.constitutionType;
    this.englishName = props.englishName;
    this.pinyin = props.pinyin;
    this.characteristics = props.characteristics;
    this.diagnosticCriteria = props.diagnosticCriteria;
    this.treatmentPrinciples = props.treatmentPrinciples;
    this.lifestyleRecommendations = props.lifestyleRecommendations;
    this.dietaryAdvice = props.dietaryAdvice;
    this.seasonalCare = props.seasonalCare;
    this.developmentalFactors = props.developmentalFactors;
    this.transformationRules = props.transformationRules;
    this.prevalenceStatistics = props.prevalenceStatistics;
    this.associatedHerbs = props.associatedHerbs;
    this.associatedPrescriptions = props.associatedPrescriptions;
    this.associatedAcupoints = props.associatedAcupoints;
    this.modernResearch = props.modernResearch;
  }

  override update(props: Partial<ConstitutionNodeProperties>): void {
    super.update(props);

    if (props.constitutionType) this.constitutionType = props.constitutionType;
    if (props.englishName) this.englishName = props.englishName;
    if (props.pinyin) this.pinyin = props.pinyin;
    if (props.characteristics) this.characteristics = props.characteristics;
    if (props.diagnosticCriteria) this.diagnosticCriteria = props.diagnosticCriteria;
    if (props.treatmentPrinciples) this.treatmentPrinciples = props.treatmentPrinciples;
    if (props.lifestyleRecommendations) this.lifestyleRecommendations = props.lifestyleRecommendations;
    if (props.dietaryAdvice) this.dietaryAdvice = props.dietaryAdvice;
    if (props.seasonalCare) this.seasonalCare = props.seasonalCare;
    if (props.developmentalFactors) this.developmentalFactors = props.developmentalFactors;
    if (props.transformationRules) this.transformationRules = props.transformationRules;
    if (props.prevalenceStatistics) this.prevalenceStatistics = props.prevalenceStatistics;
    if (props.associatedHerbs) this.associatedHerbs = props.associatedHerbs;
    if (props.associatedPrescriptions) this.associatedPrescriptions = props.associatedPrescriptions;
    if (props.associatedAcupoints) this.associatedAcupoints = props.associatedAcupoints;
    if (props.modernResearch) this.modernResearch = props.modernResearch;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      constitutionType: this.constitutionType,
      englishName: this.englishName,
      pinyin: this.pinyin,
      characteristics: this.characteristics,
      diagnosticCriteria: this.diagnosticCriteria,
      treatmentPrinciples: this.treatmentPrinciples,
      lifestyleRecommendations: this.lifestyleRecommendations,
      dietaryAdvice: this.dietaryAdvice,
      seasonalCare: this.seasonalCare,
      developmentalFactors: this.developmentalFactors,
      transformationRules: this.transformationRules,
      prevalenceStatistics: this.prevalenceStatistics,
      associatedHerbs: this.associatedHerbs,
      associatedPrescriptions: this.associatedPrescriptions,
      associatedAcupoints: this.associatedAcupoints,
      modernResearch: this.modernResearch
    };
  }
} 