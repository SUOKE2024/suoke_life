/**
 * 穴位节点类
 * 继承自TCM节点类，专门用于表示中医穴位
 */

import { TCMNode, TCMNodeProperties, TCMNodeImpl } from './tcm-node';

export interface AcupointLocation {
  description: string;
  anatomicalLandmarks: string[];
  measurements?: string; // 如"1.5寸"等
  coordinates?: {
    x: number;
    y: number;
    z: number;
    referenceSystem: string;
  };
  depthRange?: {
    min: number;
    max: number;
    unit: string;
  };
}

export interface AcupointProperties {
  pinyin?: string;
  englishName?: string;
  code?: string; // 如 "LI4"
  meridian: string;
  location: AcupointLocation;
  needlingMethod: {
    direction: string;
    depth: string;
    angle: string;
    sensation: string[];
    technique?: string[];
  };
  actions: string[];
  indications: string[];
  contraindications?: string[];
  combinationPoints?: Array<{
    points: string[];
    purpose: string;
    name?: string;
  }>;
  traditionalFunctions: string[];
  properties?: {
    type?: Array<'yuan' | 'luo' | 'xi' | 'mu' | 'shu' | 'hui' | 'jing' | 'he'>;
    fiveElements?: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    yinYang?: 'yin' | 'yang';
  };
  clinicalApplications?: Array<{
    condition: string;
    needlingMethod?: string;
    effectiveness: 'highly effective' | 'effective' | 'moderately effective' | 'limited evidence';
    evidence?: string;
  }>;
  anatomicalStructures?: {
    muscles?: string[];
    nerves?: string[];
    vessels?: string[];
    bones?: string[];
  };
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  safetyConsiderations?: string[];
  alternativeTreatmentMethods?: Array<{
    method: string;
    description: string;
  }>;
  images?: string[];
}

export interface AcupointNode extends TCMNode {
  pinyin?: string;
  englishName?: string;
  code?: string; // 如 "LI4"
  meridian: string;
  location: AcupointLocation;
  needlingMethod: {
    direction: string;
    depth: string;
    angle: string;
    sensation: string[];
    technique?: string[];
  };
  actions: string[];
  indications: string[];
  contraindications?: string[];
  combinationPoints?: Array<{
    points: string[];
    purpose: string;
    name?: string;
  }>;
  traditionalFunctions: string[];
  properties?: {
    type?: Array<'yuan' | 'luo' | 'xi' | 'mu' | 'shu' | 'hui' | 'jing' | 'he'>;
    fiveElements?: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    yinYang?: 'yin' | 'yang';
  };
  clinicalApplications?: Array<{
    condition: string;
    needlingMethod?: string;
    effectiveness: 'highly effective' | 'effective' | 'moderately effective' | 'limited evidence';
    evidence?: string;
  }>;
  anatomicalStructures?: {
    muscles?: string[];
    nerves?: string[];
    vessels?: string[];
    bones?: string[];
  };
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  safetyConsiderations?: string[];
  alternativeTreatmentMethods?: Array<{
    method: string;
    description: string;
  }>;
  images?: string[];
}

export interface AcupointNodeProperties extends TCMNodeProperties, AcupointProperties {}

export class AcupointNodeImpl extends TCMNodeImpl implements AcupointNode {
  pinyin?: string;
  englishName?: string;
  code?: string;
  meridian: string;
  location: AcupointLocation;
  needlingMethod: {
    direction: string;
    depth: string;
    angle: string;
    sensation: string[];
    technique?: string[];
  };
  actions: string[];
  indications: string[];
  contraindications?: string[];
  combinationPoints?: Array<{
    points: string[];
    purpose: string;
    name?: string;
  }>;
  traditionalFunctions: string[];
  properties?: {
    type?: Array<'yuan' | 'luo' | 'xi' | 'mu' | 'shu' | 'hui' | 'jing' | 'he'>;
    fiveElements?: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    yinYang?: 'yin' | 'yang';
  };
  clinicalApplications?: Array<{
    condition: string;
    needlingMethod?: string;
    effectiveness: 'highly effective' | 'effective' | 'moderately effective' | 'limited evidence';
    evidence?: string;
  }>;
  anatomicalStructures?: {
    muscles?: string[];
    nerves?: string[];
    vessels?: string[];
    bones?: string[];
  };
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  safetyConsiderations?: string[];
  alternativeTreatmentMethods?: Array<{
    method: string;
    description: string;
  }>;
  images?: string[];

  constructor(props: AcupointNodeProperties) {
    super({
      ...props,
      category: 'acupoint'
    });

    this.pinyin = props.pinyin;
    this.englishName = props.englishName;
    this.code = props.code;
    this.meridian = props.meridian;
    this.location = props.location;
    this.needlingMethod = props.needlingMethod;
    this.actions = props.actions;
    this.indications = props.indications;
    this.contraindications = props.contraindications;
    this.combinationPoints = props.combinationPoints;
    this.traditionalFunctions = props.traditionalFunctions;
    this.properties = props.properties;
    this.clinicalApplications = props.clinicalApplications;
    this.anatomicalStructures = props.anatomicalStructures;
    this.modernResearch = props.modernResearch;
    this.safetyConsiderations = props.safetyConsiderations;
    this.alternativeTreatmentMethods = props.alternativeTreatmentMethods;
    this.images = props.images;
  }

  override update(props: Partial<AcupointNodeProperties>): void {
    super.update(props);

    if (props.pinyin) this.pinyin = props.pinyin;
    if (props.englishName) this.englishName = props.englishName;
    if (props.code) this.code = props.code;
    if (props.meridian) this.meridian = props.meridian;
    if (props.location) this.location = props.location;
    if (props.needlingMethod) this.needlingMethod = props.needlingMethod;
    if (props.actions) this.actions = props.actions;
    if (props.indications) this.indications = props.indications;
    if (props.contraindications) this.contraindications = props.contraindications;
    if (props.combinationPoints) this.combinationPoints = props.combinationPoints;
    if (props.traditionalFunctions) this.traditionalFunctions = props.traditionalFunctions;
    if (props.properties) this.properties = props.properties;
    if (props.clinicalApplications) this.clinicalApplications = props.clinicalApplications;
    if (props.anatomicalStructures) this.anatomicalStructures = props.anatomicalStructures;
    if (props.modernResearch) this.modernResearch = props.modernResearch;
    if (props.safetyConsiderations) this.safetyConsiderations = props.safetyConsiderations;
    if (props.alternativeTreatmentMethods) this.alternativeTreatmentMethods = props.alternativeTreatmentMethods;
    if (props.images) this.images = props.images;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      pinyin: this.pinyin,
      englishName: this.englishName,
      code: this.code,
      meridian: this.meridian,
      location: this.location,
      needlingMethod: this.needlingMethod,
      actions: this.actions,
      indications: this.indications,
      contraindications: this.contraindications,
      combinationPoints: this.combinationPoints,
      traditionalFunctions: this.traditionalFunctions,
      properties: this.properties,
      clinicalApplications: this.clinicalApplications,
      anatomicalStructures: this.anatomicalStructures,
      modernResearch: this.modernResearch,
      safetyConsiderations: this.safetyConsiderations,
      alternativeTreatmentMethods: this.alternativeTreatmentMethods,
      images: this.images
    };
  }
} 