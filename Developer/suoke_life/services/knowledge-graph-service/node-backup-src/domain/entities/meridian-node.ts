/**
 * 经络节点类
 * 继承自TCM节点类，专门用于表示中医经络系统
 */

import { TCMNode, TCMNodeProperties, TCMNodeImpl } from './tcm-node';

export type MeridianType = 
  | 'regular_meridian'  // 正经（十二正经）
  | 'extraordinary_meridian' // 奇经八脉
  | 'divergent_meridian' // 经别
  | 'luo_vessel' // 络脉
  | 'muscle_region' // 经筋
  | 'cutaneous_region'; // 皮部

export type RegularMeridianName = 
  | 'lung' // 肺经
  | 'large_intestine' // 大肠经
  | 'stomach' // 胃经
  | 'spleen' // 脾经
  | 'heart' // 心经
  | 'small_intestine' // 小肠经
  | 'bladder' // 膀胱经
  | 'kidney' // 肾经
  | 'pericardium' // 心包经
  | 'triple_energizer' // 三焦经
  | 'gallbladder' // 胆经
  | 'liver'; // 肝经

export type ExtraordinaryMeridianName =
  | 'governing_vessel' // 督脉
  | 'conception_vessel' // 任脉
  | 'penetrating_vessel' // 冲脉
  | 'girdle_vessel' // 带脉
  | 'yin_linking_vessel' // 阴维脉
  | 'yang_linking_vessel' // 阳维脉
  | 'yin_heel_vessel' // 阴跷脉
  | 'yang_heel_vessel'; // 阳跷脉

export interface MeridianPathway {
  external: string[]; // 体表循行路线
  internal?: string[]; // 体内联络脏腑路线
  description: string; // 循行路线总体描述
  connections: string[]; // 与其他经络的连接
  landmarks: string[]; // 主要标志点
}

export interface MeridianProperties {
  meridianType: MeridianType;
  regularMeridianName?: RegularMeridianName;
  extraordinaryMeridianName?: ExtraordinaryMeridianName;
  customName?: string; // 用于其他类型的经络
  pinyin?: string;
  englishName?: string;
  pathway: MeridianPathway;
  relatedOrgan?: string; // 对应脏腑
  acupoints: string[]; // 所含穴位
  openingTime?: {  // 经络开放时辰
    startHour: number;
    endHour: number;
    description: string;
  };
  functions: string[]; // 功能描述
  disorders: string[]; // 相关病症
  properties: {
    yinYang: 'yin' | 'yang';
    fiveElements?: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    energy?: string; // 气血特性
  };
  relationships: Array<{
    meridianName: string;
    relationshipType: 'interior-exterior' | 'preceding-following' | 'connecting' | 'branching' | 'other';
    description: string;
  }>;
  classicalDescription?: string; // 经典文献描述
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  clinicalSignificance?: string;
  palpationCharacteristics?: string[];
  therapeuticMethods?: Array<{
    method: string;
    description: string;
    indications: string[];
  }>;
  images?: string[]; // 经络图谱
}

export interface MeridianNode extends TCMNode {
  meridianType: MeridianType;
  regularMeridianName?: RegularMeridianName;
  extraordinaryMeridianName?: ExtraordinaryMeridianName;
  customName?: string;
  pinyin?: string;
  englishName?: string;
  pathway: MeridianPathway;
  relatedOrgan?: string;
  acupoints: string[];
  openingTime?: {
    startHour: number;
    endHour: number;
    description: string;
  };
  functions: string[];
  disorders: string[];
  properties: {
    yinYang: 'yin' | 'yang';
    fiveElements?: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    energy?: string;
  };
  relationships: Array<{
    meridianName: string;
    relationshipType: 'interior-exterior' | 'preceding-following' | 'connecting' | 'branching' | 'other';
    description: string;
  }>;
  classicalDescription?: string;
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  clinicalSignificance?: string;
  palpationCharacteristics?: string[];
  therapeuticMethods?: Array<{
    method: string;
    description: string;
    indications: string[];
  }>;
  images?: string[];
}

export interface MeridianNodeProperties extends TCMNodeProperties, MeridianProperties {}

export class MeridianNodeImpl extends TCMNodeImpl implements MeridianNode {
  meridianType: MeridianType;
  regularMeridianName?: RegularMeridianName;
  extraordinaryMeridianName?: ExtraordinaryMeridianName;
  customName?: string;
  pinyin?: string;
  englishName?: string;
  pathway: MeridianPathway;
  relatedOrgan?: string;
  acupoints: string[];
  openingTime?: {
    startHour: number;
    endHour: number;
    description: string;
  };
  functions: string[];
  disorders: string[];
  properties: {
    yinYang: 'yin' | 'yang';
    fiveElements?: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    energy?: string;
  };
  relationships: Array<{
    meridianName: string;
    relationshipType: 'interior-exterior' | 'preceding-following' | 'connecting' | 'branching' | 'other';
    description: string;
  }>;
  classicalDescription?: string;
  modernResearch?: Array<{
    title: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    findings: string;
  }>;
  clinicalSignificance?: string;
  palpationCharacteristics?: string[];
  therapeuticMethods?: Array<{
    method: string;
    description: string;
    indications: string[];
  }>;
  images?: string[];

  constructor(props: MeridianNodeProperties) {
    super({
      ...props,
      category: 'meridian'
    });

    this.meridianType = props.meridianType;
    this.regularMeridianName = props.regularMeridianName;
    this.extraordinaryMeridianName = props.extraordinaryMeridianName;
    this.customName = props.customName;
    this.pinyin = props.pinyin;
    this.englishName = props.englishName;
    this.pathway = props.pathway;
    this.relatedOrgan = props.relatedOrgan;
    this.acupoints = props.acupoints;
    this.openingTime = props.openingTime;
    this.functions = props.functions;
    this.disorders = props.disorders;
    this.properties = props.properties;
    this.relationships = props.relationships;
    this.classicalDescription = props.classicalDescription;
    this.modernResearch = props.modernResearch;
    this.clinicalSignificance = props.clinicalSignificance;
    this.palpationCharacteristics = props.palpationCharacteristics;
    this.therapeuticMethods = props.therapeuticMethods;
    this.images = props.images;
  }

  override update(props: Partial<MeridianNodeProperties>): void {
    super.update(props);

    if (props.meridianType) this.meridianType = props.meridianType;
    if (props.regularMeridianName) this.regularMeridianName = props.regularMeridianName;
    if (props.extraordinaryMeridianName) this.extraordinaryMeridianName = props.extraordinaryMeridianName;
    if (props.customName) this.customName = props.customName;
    if (props.pinyin) this.pinyin = props.pinyin;
    if (props.englishName) this.englishName = props.englishName;
    if (props.pathway) this.pathway = props.pathway;
    if (props.relatedOrgan) this.relatedOrgan = props.relatedOrgan;
    if (props.acupoints) this.acupoints = props.acupoints;
    if (props.openingTime) this.openingTime = props.openingTime;
    if (props.functions) this.functions = props.functions;
    if (props.disorders) this.disorders = props.disorders;
    if (props.properties) this.properties = props.properties;
    if (props.relationships) this.relationships = props.relationships;
    if (props.classicalDescription) this.classicalDescription = props.classicalDescription;
    if (props.modernResearch) this.modernResearch = props.modernResearch;
    if (props.clinicalSignificance) this.clinicalSignificance = props.clinicalSignificance;
    if (props.palpationCharacteristics) this.palpationCharacteristics = props.palpationCharacteristics;
    if (props.therapeuticMethods) this.therapeuticMethods = props.therapeuticMethods;
    if (props.images) this.images = props.images;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      meridianType: this.meridianType,
      regularMeridianName: this.regularMeridianName,
      extraordinaryMeridianName: this.extraordinaryMeridianName,
      customName: this.customName,
      pinyin: this.pinyin,
      englishName: this.englishName,
      pathway: this.pathway,
      relatedOrgan: this.relatedOrgan,
      acupoints: this.acupoints,
      openingTime: this.openingTime,
      functions: this.functions,
      disorders: this.disorders,
      properties: this.properties,
      relationships: this.relationships,
      classicalDescription: this.classicalDescription,
      modernResearch: this.modernResearch,
      clinicalSignificance: this.clinicalSignificance,
      palpationCharacteristics: this.palpationCharacteristics,
      therapeuticMethods: this.therapeuticMethods,
      images: this.images
    };
  }
} 