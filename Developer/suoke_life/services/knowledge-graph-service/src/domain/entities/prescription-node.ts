/**
 * 方剂节点类
 * 继承自TCM节点类，专门用于表示中医方剂
 */

import { TCMNode, TCMNodeProperties, TCMNodeImpl } from './tcm-node';

export interface HerbComposition {
  herbName: string;
  herbId?: string;
  dosage: {
    value: number;
    unit: string;
  };
  role: 'sovereign' | 'minister' | 'assistant' | 'courier'; // 君臣佐使
  processingMethod?: string;
}

export type PrescriptionCategory = 
  | 'exterior releasing'
  | 'heat clearing'
  | 'purgative'
  | 'harmonizing'
  | 'warming'
  | 'tonifying'
  | 'securing and astringing'
  | 'tranquilizing'
  | 'orifice opening'
  | 'wind expelling'
  | 'phlegm dispelling'
  | 'digestant'
  | 'parasites expelling'
  | 'blood regulating';

export interface PrescriptionProperties {
  englishName?: string;
  pinyin?: string;
  composedHerbs: HerbComposition[];
  preparation: {
    methods: string[];
    notes?: string;
  };
  administration: {
    route: 'oral' | 'external' | 'both';
    frequency?: string;
    duration?: string;
    notes?: string;
  };
  indications: string[];
  contraindications?: string[];
  sideEffects?: string[];
  origin?: {
    dynasty: string;
    source: string;
    year?: number;
  };
  prescriptionCategories: PrescriptionCategory[];  // 重命名以避免与BaseNode的category冲突
  variations?: Array<{
    name: string;
    description: string;
    modification: string;
  }>;
  clinicalApplications?: Array<{
    condition: string;
    modification?: string;
    effectiveness: 'highly effective' | 'effective' | 'moderately effective' | 'limited evidence';
    evidence?: string;
  }>;
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
}

export interface PrescriptionNode extends TCMNode {
  englishName?: string;
  pinyin?: string;
  composedHerbs: HerbComposition[];
  preparation: {
    methods: string[];
    notes?: string;
  };
  administration: {
    route: 'oral' | 'external' | 'both';
    frequency?: string;
    duration?: string;
    notes?: string;
  };
  indications: string[];
  contraindications?: string[];
  sideEffects?: string[];
  origin?: {
    dynasty: string;
    source: string;
    year?: number;
  };
  prescriptionCategories: PrescriptionCategory[];  // 重命名以避免与BaseNode的category冲突
  variations?: Array<{
    name: string;
    description: string;
    modification: string;
  }>;
  clinicalApplications?: Array<{
    condition: string;
    modification?: string;
    effectiveness: 'highly effective' | 'effective' | 'moderately effective' | 'limited evidence';
    evidence?: string;
  }>;
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
}

export interface PrescriptionNodeProperties extends TCMNodeProperties, PrescriptionProperties {}

export class PrescriptionNodeImpl extends TCMNodeImpl implements PrescriptionNode {
  englishName?: string;
  pinyin?: string;
  composedHerbs: HerbComposition[];
  preparation: {
    methods: string[];
    notes?: string;
  };
  administration: {
    route: 'oral' | 'external' | 'both';
    frequency?: string;
    duration?: string;
    notes?: string;
  };
  indications: string[];
  contraindications?: string[];
  sideEffects?: string[];
  origin?: {
    dynasty: string;
    source: string;
    year?: number;
  };
  prescriptionCategories: PrescriptionCategory[];  // 重命名以避免与BaseNode的category冲突
  variations?: Array<{
    name: string;
    description: string;
    modification: string;
  }>;
  clinicalApplications?: Array<{
    condition: string;
    modification?: string;
    effectiveness: 'highly effective' | 'effective' | 'moderately effective' | 'limited evidence';
    evidence?: string;
  }>;
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;

  constructor(props: PrescriptionNodeProperties) {
    super({
      ...props,
      category: 'prescription'
    });

    this.englishName = props.englishName;
    this.pinyin = props.pinyin;
    this.composedHerbs = props.composedHerbs;
    this.preparation = props.preparation;
    this.administration = props.administration;
    this.indications = props.indications;
    this.contraindications = props.contraindications;
    this.sideEffects = props.sideEffects;
    this.origin = props.origin;
    this.prescriptionCategories = props.prescriptionCategories;
    this.variations = props.variations;
    this.clinicalApplications = props.clinicalApplications;
    this.modernResearch = props.modernResearch;
  }

  override update(props: Partial<PrescriptionNodeProperties>): void {
    super.update(props);

    if (props.englishName) this.englishName = props.englishName;
    if (props.pinyin) this.pinyin = props.pinyin;
    if (props.composedHerbs) this.composedHerbs = props.composedHerbs;
    if (props.preparation) this.preparation = props.preparation;
    if (props.administration) this.administration = props.administration;
    if (props.indications) this.indications = props.indications;
    if (props.contraindications) this.contraindications = props.contraindications;
    if (props.sideEffects) this.sideEffects = props.sideEffects;
    if (props.origin) this.origin = props.origin;
    if (props.prescriptionCategories) this.prescriptionCategories = props.prescriptionCategories;
    if (props.variations) this.variations = props.variations;
    if (props.clinicalApplications) this.clinicalApplications = props.clinicalApplications;
    if (props.modernResearch) this.modernResearch = props.modernResearch;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      englishName: this.englishName,
      pinyin: this.pinyin,
      composedHerbs: this.composedHerbs,
      preparation: this.preparation,
      administration: this.administration,
      indications: this.indications,
      contraindications: this.contraindications,
      sideEffects: this.sideEffects,
      origin: this.origin,
      prescriptionCategories: this.prescriptionCategories,
      variations: this.variations,
      clinicalApplications: this.clinicalApplications,
      modernResearch: this.modernResearch
    };
  }
} 