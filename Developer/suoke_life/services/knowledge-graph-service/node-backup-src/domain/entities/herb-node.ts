/**
 * 中药节点类
 * 继承自TCM节点类，专门用于表示中药材
 */

import { TCMNode, TCMNodeProperties, TCMNodeImpl } from './tcm-node';

export interface HerbProperties {
  pinyin?: string;
  latinName?: string;
  commonName?: {
    chinese: string;
    english?: string;
  };
  properties: {
    taste: Array<'sour' | 'bitter' | 'sweet' | 'spicy' | 'salty'>;
    nature: 'cold' | 'cool' | 'neutral' | 'warm' | 'hot';
    meridianAffinity?: string[];
    toxicity?: 'none' | 'mild' | 'moderate' | 'high' | 'very high';
  };
  functions: string[];
  applications: string[];
  dosage?: {
    min: number;
    max: number;
    unit: string;
  };
  preparationMethods?: string[];
  contradictions?: string[];
  sideEffects?: string[];
  interactions?: Array<{
    herb?: string;
    drug?: string;
    effect: string;
    severity: 'mild' | 'moderate' | 'severe';
  }>;
  modernResearch?: {
    compounds?: string[];
    effects?: string[];
    studies?: Array<{
      title: string;
      authors?: string[];
      journal?: string;
      year?: number;
      doi?: string;
      findings: string;
    }>;
  };
  images?: string[];
}

export interface HerbNode extends TCMNode {
  pinyin?: string;
  latinName?: string;
  commonName?: {
    chinese: string;
    english?: string;
  };
  properties: {
    taste: Array<'sour' | 'bitter' | 'sweet' | 'spicy' | 'salty'>;
    nature: 'cold' | 'cool' | 'neutral' | 'warm' | 'hot';
    meridianAffinity?: string[];
    toxicity?: 'none' | 'mild' | 'moderate' | 'high' | 'very high';
  };
  functions: string[];
  applications: string[];
  dosage?: {
    min: number;
    max: number;
    unit: string;
  };
  preparationMethods?: string[];
  contradictions?: string[];
  sideEffects?: string[];
  interactions?: Array<{
    herb?: string;
    drug?: string;
    effect: string;
    severity: 'mild' | 'moderate' | 'severe';
  }>;
  modernResearch?: {
    compounds?: string[];
    effects?: string[];
    studies?: Array<{
      title: string;
      authors?: string[];
      journal?: string;
      year?: number;
      doi?: string;
      findings: string;
    }>;
  };
  images?: string[];
}

export interface HerbNodeProperties extends TCMNodeProperties, HerbProperties {}

export class HerbNodeImpl extends TCMNodeImpl implements HerbNode {
  pinyin?: string;
  latinName?: string;
  commonName?: {
    chinese: string;
    english?: string;
  };
  properties: {
    taste: Array<'sour' | 'bitter' | 'sweet' | 'spicy' | 'salty'>;
    nature: 'cold' | 'cool' | 'neutral' | 'warm' | 'hot';
    meridianAffinity?: string[];
    toxicity?: 'none' | 'mild' | 'moderate' | 'high' | 'very high';
  };
  functions: string[];
  applications: string[];
  dosage?: {
    min: number;
    max: number;
    unit: string;
  };
  preparationMethods?: string[];
  contradictions?: string[];
  sideEffects?: string[];
  interactions?: Array<{
    herb?: string;
    drug?: string;
    effect: string;
    severity: 'mild' | 'moderate' | 'severe';
  }>;
  modernResearch?: {
    compounds?: string[];
    effects?: string[];
    studies?: Array<{
      title: string;
      authors?: string[];
      journal?: string;
      year?: number;
      doi?: string;
      findings: string;
    }>;
  };
  images?: string[];

  constructor(props: HerbNodeProperties) {
    super({
      ...props,
      category: 'herb'
    });
    
    this.pinyin = props.pinyin;
    this.latinName = props.latinName;
    this.commonName = props.commonName;
    this.properties = props.properties;
    this.functions = props.functions;
    this.applications = props.applications;
    this.dosage = props.dosage;
    this.preparationMethods = props.preparationMethods;
    this.contradictions = props.contradictions;
    this.sideEffects = props.sideEffects;
    this.interactions = props.interactions;
    this.modernResearch = props.modernResearch;
    this.images = props.images;
  }

  override update(props: Partial<HerbNodeProperties>): void {
    super.update(props);
    
    if (props.pinyin) this.pinyin = props.pinyin;
    if (props.latinName) this.latinName = props.latinName;
    if (props.commonName) this.commonName = props.commonName;
    if (props.properties) this.properties = props.properties;
    if (props.functions) this.functions = props.functions;
    if (props.applications) this.applications = props.applications;
    if (props.dosage) this.dosage = props.dosage;
    if (props.preparationMethods) this.preparationMethods = props.preparationMethods;
    if (props.contradictions) this.contradictions = props.contradictions;
    if (props.sideEffects) this.sideEffects = props.sideEffects;
    if (props.interactions) this.interactions = props.interactions;
    if (props.modernResearch) this.modernResearch = props.modernResearch;
    if (props.images) this.images = props.images;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      pinyin: this.pinyin,
      latinName: this.latinName,
      commonName: this.commonName,
      properties: this.properties,
      functions: this.functions,
      applications: this.applications,
      dosage: this.dosage,
      preparationMethods: this.preparationMethods,
      contradictions: this.contradictions,
      sideEffects: this.sideEffects,
      interactions: this.interactions,
      modernResearch: this.modernResearch,
      images: this.images
    };
  }
} 