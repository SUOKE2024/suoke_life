/**
 * 中医节点类
 * 继承自基础节点类，专门用于表示中医知识体系中的概念
 */

import { BaseNode, BaseNodeProperties, BaseNodeImpl } from './base-node';

export interface TCMTheory {
  name: string;
  description: string;
  origin?: string;
  classicalReferences?: string[];
}

export interface TCMNode extends BaseNode {
  theory: TCMTheory[];
  classicalReferences?: string[];
  modernInterpretation?: string;
  clinicalSignificance?: string;
  yin_yang_attributes?: {
    nature: 'yin' | 'yang' | 'balanced';
    degree?: number; // 1-10表示强度
  };
  five_elements?: {
    category: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    relationships?: Array<{
      element: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
      type: 'generates' | 'controls' | 'insulted_by' | 'insults';
    }>;
  };
  six_pathogens?: Array<'wind' | 'cold' | 'heat' | 'dampness' | 'dryness' | 'fire'>;
  seven_emotions?: Array<'joy' | 'anger' | 'worry' | 'pensiveness' | 'sadness' | 'fear' | 'fright'>;
  eight_principles?: {
    interior_exterior?: 'interior' | 'exterior';
    cold_heat?: 'cold' | 'heat';
    deficiency_excess?: 'deficiency' | 'excess';
    yin_yang?: 'yin' | 'yang';
  };
}

export interface TCMNodeProperties extends BaseNodeProperties {
  theory: TCMTheory[];
  classicalReferences?: string[];
  modernInterpretation?: string;
  clinicalSignificance?: string;
  yin_yang_attributes?: {
    nature: 'yin' | 'yang' | 'balanced';
    degree?: number;
  };
  five_elements?: {
    category: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    relationships?: Array<{
      element: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
      type: 'generates' | 'controls' | 'insulted_by' | 'insults';
    }>;
  };
  six_pathogens?: Array<'wind' | 'cold' | 'heat' | 'dampness' | 'dryness' | 'fire'>;
  seven_emotions?: Array<'joy' | 'anger' | 'worry' | 'pensiveness' | 'sadness' | 'fear' | 'fright'>;
  eight_principles?: {
    interior_exterior?: 'interior' | 'exterior';
    cold_heat?: 'cold' | 'heat';
    deficiency_excess?: 'deficiency' | 'excess';
    yin_yang?: 'yin' | 'yang';
  };
}

export class TCMNodeImpl extends BaseNodeImpl implements TCMNode {
  theory: TCMTheory[];
  classicalReferences?: string[];
  modernInterpretation?: string;
  clinicalSignificance?: string;
  yin_yang_attributes?: {
    nature: 'yin' | 'yang' | 'balanced';
    degree?: number;
  };
  five_elements?: {
    category: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
    relationships?: Array<{
      element: 'wood' | 'fire' | 'earth' | 'metal' | 'water';
      type: 'generates' | 'controls' | 'insulted_by' | 'insults';
    }>;
  };
  six_pathogens?: Array<'wind' | 'cold' | 'heat' | 'dampness' | 'dryness' | 'fire'>;
  seven_emotions?: Array<'joy' | 'anger' | 'worry' | 'pensiveness' | 'sadness' | 'fear' | 'fright'>;
  eight_principles?: {
    interior_exterior?: 'interior' | 'exterior';
    cold_heat?: 'cold' | 'heat';
    deficiency_excess?: 'deficiency' | 'excess';
    yin_yang?: 'yin' | 'yang';
  };

  constructor(props: TCMNodeProperties) {
    super({
      ...props,
      category: props.category || 'TCM'
    });
    
    this.theory = props.theory;
    this.classicalReferences = props.classicalReferences;
    this.modernInterpretation = props.modernInterpretation;
    this.clinicalSignificance = props.clinicalSignificance;
    this.yin_yang_attributes = props.yin_yang_attributes;
    this.five_elements = props.five_elements;
    this.six_pathogens = props.six_pathogens;
    this.seven_emotions = props.seven_emotions;
    this.eight_principles = props.eight_principles;
  }

  override update(props: Partial<TCMNodeProperties>): void {
    super.update(props);
    
    if (props.theory) this.theory = props.theory;
    if (props.classicalReferences) this.classicalReferences = props.classicalReferences;
    if (props.modernInterpretation) this.modernInterpretation = props.modernInterpretation;
    if (props.clinicalSignificance) this.clinicalSignificance = props.clinicalSignificance;
    if (props.yin_yang_attributes) this.yin_yang_attributes = props.yin_yang_attributes;
    if (props.five_elements) this.five_elements = props.five_elements;
    if (props.six_pathogens) this.six_pathogens = props.six_pathogens;
    if (props.seven_emotions) this.seven_emotions = props.seven_emotions;
    if (props.eight_principles) this.eight_principles = props.eight_principles;
  }

  override toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      theory: this.theory,
      classicalReferences: this.classicalReferences,
      modernInterpretation: this.modernInterpretation,
      clinicalSignificance: this.clinicalSignificance,
      yin_yang_attributes: this.yin_yang_attributes,
      five_elements: this.five_elements,
      six_pathogens: this.six_pathogens,
      seven_emotions: this.seven_emotions,
      eight_principles: this.eight_principles
    };
  }
} 