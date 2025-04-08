/**
 * 知识图谱关系类型定义
 * 定义了图数据库中节点间的各种关系类型
 */

export type RelationshipDirection = 'OUTGOING' | 'INCOMING' | 'BOTH';

export interface RelationshipType {
  name: string;
  description: string;
  sourceTypes: string[];
  targetTypes: string[];
  properties?: RelationshipProperty[];
  bidirectional?: boolean;
  inverse?: string;
}

export interface RelationshipProperty {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'array' | 'object';
  description: string;
  required?: boolean;
  defaultValue?: any;
  enum?: string[];
}

export const TCM_RELATIONSHIPS: RelationshipType[] = [
  {
    name: 'TREATS',
    description: '治疗关系，表示一种节点（如药材、方剂、疗法）可以治疗另一种节点（如症状、疾病、证型）',
    sourceTypes: ['herb', 'prescription', 'acupoint', 'therapy'],
    targetTypes: ['symptom', 'diagnosis', 'syndrome'],
    properties: [
      {
        name: 'effectivenessLevel',
        type: 'string',
        description: '治疗效果级别',
        enum: ['highly_effective', 'effective', 'moderately_effective', 'limited_evidence']
      },
      {
        name: 'evidence',
        type: 'string',
        description: '支持该治疗关系的证据'
      }
    ]
  },
  {
    name: 'COMPOSED_OF',
    description: '组成关系，表示一个方剂由多种药材组成',
    sourceTypes: ['prescription'],
    targetTypes: ['herb'],
    properties: [
      {
        name: 'quantity',
        type: 'number',
        description: '药材在方剂中的数量'
      },
      {
        name: 'unit',
        type: 'string',
        description: '药材数量的单位'
      },
      {
        name: 'role',
        type: 'string',
        description: '药材在方剂中的角色（君臣佐使）',
        enum: ['sovereign', 'minister', 'assistant', 'courier']
      },
      {
        name: 'processingMethod',
        type: 'string',
        description: '药材的炮制方法'
      }
    ]
  },
  {
    name: 'MANIFESTS_AS',
    description: '表现为关系，表示一种诊断或证型表现为某些症状',
    sourceTypes: ['diagnosis', 'syndrome'],
    targetTypes: ['symptom'],
    properties: [
      {
        name: 'frequency',
        type: 'string',
        description: '症状出现的频率',
        enum: ['always', 'common', 'occasional', 'rare']
      },
      {
        name: 'significance',
        type: 'string',
        description: '症状的诊断意义',
        enum: ['key', 'major', 'minor', 'variable']
      }
    ]
  },
  {
    name: 'BELONGS_TO',
    description: '归属关系，表示一个穴位归属于某条经络',
    sourceTypes: ['acupoint'],
    targetTypes: ['meridian'],
    properties: [
      {
        name: 'order',
        type: 'number',
        description: '穴位在经络上的顺序'
      }
    ]
  },
  {
    name: 'INDICATES',
    description: '指示关系，表示某种症状可能指示某种诊断或证型',
    sourceTypes: ['symptom'],
    targetTypes: ['diagnosis', 'syndrome'],
    properties: [
      {
        name: 'diagnosticWeight',
        type: 'string',
        description: '症状对诊断的权重',
        enum: ['pathognomonic', 'major', 'minor', 'supporting']
      },
      {
        name: 'specificity',
        type: 'number',
        description: '症状对该诊断的特异性（0-1）'
      },
      {
        name: 'sensitivity',
        type: 'number',
        description: '症状对该诊断的敏感性（0-1）'
      }
    ],
    inverse: 'MANIFESTS_AS'
  },
  {
    name: 'RELATED_TO',
    description: '相关关系，表示两个节点之间有某种相关性',
    sourceTypes: ['*'],
    targetTypes: ['*'],
    properties: [
      {
        name: 'relationType',
        type: 'string',
        description: '相关性的类型'
      },
      {
        name: 'strength',
        type: 'number',
        description: '相关性的强度（0-1）'
      }
    ],
    bidirectional: true
  },
  {
    name: 'RECOMMENDED_FOR',
    description: '推荐关系，表示某种方法（如食疗、运动等）被推荐用于某种体质或状态',
    sourceTypes: ['diet', 'exercise', 'lifestyle', 'herb', 'prescription'],
    targetTypes: ['constitution', 'diagnosis', 'syndrome', 'condition'],
    properties: [
      {
        name: 'recommendationStrength',
        type: 'string',
        description: '推荐强度',
        enum: ['strong', 'moderate', 'weak']
      },
      {
        name: 'evidence',
        type: 'string',
        description: '推荐的证据基础'
      }
    ]
  },
  {
    name: 'CONTRAINDICATED_FOR',
    description: '禁忌关系，表示某种方法（如药材、方剂）对某种状态是禁忌的',
    sourceTypes: ['herb', 'prescription', 'therapy', 'diet'],
    targetTypes: ['constitution', 'diagnosis', 'syndrome', 'condition'],
    properties: [
      {
        name: 'severity',
        type: 'string',
        description: '禁忌的严重程度',
        enum: ['absolute', 'strong', 'relative', 'cautionary']
      },
      {
        name: 'reasoning',
        type: 'string',
        description: '禁忌的原因'
      }
    ]
  },
  {
    name: 'CORRESPONDS_TO',
    description: '对应关系，表示中医概念与现代医学概念之间的对应关系',
    sourceTypes: ['tcm_node', 'herb', 'prescription', 'symptom', 'diagnosis', 'syndrome'],
    targetTypes: ['modern_medicine_node'],
    properties: [
      {
        name: 'correspondenceType',
        type: 'string',
        description: '对应类型',
        enum: ['direct_equivalence', 'partial_equivalence', 'conceptual_similarity', 'historical_correlation']
      },
      {
        name: 'correspondenceStrength',
        type: 'number',
        description: '对应强度（0-1）'
      },
      {
        name: 'evidence',
        type: 'string',
        description: '支持该对应关系的证据'
      }
    ],
    bidirectional: true
  },
  {
    name: 'AFFECTS',
    description: '影响关系，表示一个节点对另一个节点有影响作用',
    sourceTypes: ['*'],
    targetTypes: ['*'],
    properties: [
      {
        name: 'effectType',
        type: 'string',
        description: '影响类型',
        enum: ['inhibits', 'promotes', 'regulates', 'transforms', 'harmonizes']
      },
      {
        name: 'mechanism',
        type: 'string',
        description: '作用机制'
      },
      {
        name: 'strength',
        type: 'string',
        description: '影响强度',
        enum: ['strong', 'moderate', 'mild']
      }
    ]
  },
  {
    name: 'INTERACTS_WITH',
    description: '相互作用关系，表示两个节点（通常是药物、药材）之间的相互作用',
    sourceTypes: ['herb', 'prescription', 'modern_medicine_node'],
    targetTypes: ['herb', 'prescription', 'modern_medicine_node'],
    properties: [
      {
        name: 'interactionType',
        type: 'string',
        description: '相互作用类型',
        enum: ['synergistic', 'antagonistic', 'potentiation', 'diminution', 'toxic']
      },
      {
        name: 'severity',
        type: 'string',
        description: '严重程度',
        enum: ['minor', 'moderate', 'major', 'contraindicated']
      },
      {
        name: 'evidence',
        type: 'string',
        description: '支持该相互作用的证据'
      }
    ],
    bidirectional: true
  },
  {
    name: 'SIMILAR_TO',
    description: '相似关系，表示两个节点之间的相似性',
    sourceTypes: ['*'],
    targetTypes: ['*'],
    properties: [
      {
        name: 'similarityScore',
        type: 'number',
        description: '相似度分数（0-1）'
      },
      {
        name: 'similarityAspects',
        type: 'array',
        description: '相似的方面'
      }
    ],
    bidirectional: true
  },
  {
    name: 'CAUSES',
    description: '导致关系，表示一个节点导致另一个节点',
    sourceTypes: ['*'],
    targetTypes: ['symptom', 'diagnosis', 'syndrome', 'condition'],
    properties: [
      {
        name: 'causalityStrength',
        type: 'string',
        description: '因果关系强度',
        enum: ['definite', 'probable', 'possible', 'unlikely']
      },
      {
        name: 'mechanism',
        type: 'string',
        description: '致病机制'
      }
    ]
  },
  {
    name: 'CLASSIFIED_AS',
    description: '分类关系，表示一个节点被分类为某个类别',
    sourceTypes: ['*'],
    targetTypes: ['category', 'classification'],
    properties: [
      {
        name: 'classificationSystem',
        type: 'string',
        description: '分类系统'
      }
    ]
  },
  {
    name: 'EVOLVED_FROM',
    description: '演化关系，表示一个概念从另一个概念演化而来',
    sourceTypes: ['*'],
    targetTypes: ['*'],
    properties: [
      {
        name: 'evolutionPeriod',
        type: 'string',
        description: '演化时期'
      },
      {
        name: 'historicalContext',
        type: 'string',
        description: '历史背景'
      }
    ]
  },
  {
    name: 'RESEARCHED_IN',
    description: '研究关系，表示一个概念在某项研究中被研究',
    sourceTypes: ['*'],
    targetTypes: ['research_study'],
    properties: [
      {
        name: 'researchFocus',
        type: 'string',
        description: '研究重点'
      },
      {
        name: 'findings',
        type: 'string',
        description: '研究发现'
      }
    ]
  },
  {
    name: 'FLOWS_THROUGH',
    description: '经络流经的部位或穴位',
    sourceTypes: ['meridian'],
    targetTypes: ['acupoint', 'body_region'],
    bidirectional: false,
    inverse: 'LOCATED_ON'
  },
  {
    name: 'CONNECTS_TO',
    description: '经络之间的连接关系',
    sourceTypes: ['meridian'],
    targetTypes: ['meridian'],
    bidirectional: true
  },
  {
    name: 'BELONGS_TO_MERIDIAN',
    description: '穴位属于的经络',
    sourceTypes: ['acupoint'],
    targetTypes: ['meridian'],
    bidirectional: false,
    inverse: 'HAS_ACUPOINT'
  },
  {
    name: 'GOVERNS',
    description: '经络所主管的脏腑',
    sourceTypes: ['meridian'],
    targetTypes: ['organ'],
    bidirectional: false,
    inverse: 'GOVERNED_BY'
  },
  {
    name: 'HAS_OPENING_TIME',
    description: '经络的开放时辰',
    sourceTypes: ['meridian'],
    targetTypes: ['time_period'],
    properties: [
      {
        name: 'start_hour',
        type: 'number',
        description: '开始时辰（24小时制）',
        required: true
      },
      {
        name: 'end_hour',
        type: 'number',
        description: '结束时辰（24小时制）',
        required: true
      }
    ]
  },
  {
    name: 'INFLUENCES_CONSTITUTION',
    description: '经络对体质的影响关系',
    sourceTypes: ['meridian'],
    targetTypes: ['constitution'],
    bidirectional: false,
    properties: [
      {
        name: 'influence_type',
        type: 'string',
        description: '影响类型',
        enum: ['strengthening', 'weakening', 'balancing', 'disturbing']
      },
      {
        name: 'influence_degree',
        type: 'string',
        description: '影响程度',
        enum: ['strong', 'moderate', 'mild']
      }
    ]
  },
  {
    name: 'ASSOCIATED_WITH_PATHOLOGY',
    description: '经络与病理状态的关联',
    sourceTypes: ['meridian'],
    targetTypes: ['diagnosis', 'symptom', 'syndrome'],
    bidirectional: false,
    properties: [
      {
        name: 'pathology_type',
        type: 'string',
        description: '病理类型',
        enum: ['excess', 'deficiency', 'stagnation', 'invasion', 'depletion']
      },
      {
        name: 'clinical_manifestation',
        type: 'string',
        description: '临床表现'
      }
    ]
  }
];

export const MODERN_MEDICINE_RELATIONSHIPS: RelationshipType[] = [
  {
    name: 'CAUSES',
    description: '致病关系，表示一个节点（如病原体、环境因素）导致另一个节点（如疾病、症状）',
    sourceTypes: ['pathogen', 'environmental_factor', 'genetic_factor', 'lifestyle_factor'],
    targetTypes: ['disease', 'symptom', 'syndrome'],
    bidirectional: false,
    inverse: 'CAUSED_BY',
    properties: [
      {
        name: 'mechanism',
        type: 'string',
        description: '致病机制',
        required: false
      },
      {
        name: 'evidence_level',
        type: 'string',
        description: '证据等级',
        required: false,
        enum: ['high', 'moderate', 'low', 'very_low']
      }
    ]
  },
  {
    name: 'TREATS_CONDITION',
    description: '治疗关系，表示一种医疗干预（如药物、手术）可以治疗某种疾病或状态',
    sourceTypes: ['modern_medicine_drug', 'modern_medicine_therapy', 'modern_medicine_device'],
    targetTypes: ['modern_medicine_disease', 'modern_medicine_condition'],
    properties: [
      {
        name: 'efficacy',
        type: 'string',
        description: '治疗效果',
        enum: ['high', 'moderate', 'low', 'variable']
      },
      {
        name: 'evidenceLevel',
        type: 'string',
        description: '证据级别',
        enum: ['level_1a', 'level_1b', 'level_2a', 'level_2b', 'level_3', 'level_4', 'level_5']
      },
      {
        name: 'recommendationGrade',
        type: 'string',
        description: '推荐级别',
        enum: ['A', 'B', 'C', 'D']
      }
    ]
  },
  {
    name: 'HAS_SYMPTOM',
    description: '症状关系，表示一种疾病有某种症状',
    sourceTypes: ['modern_medicine_disease', 'modern_medicine_condition'],
    targetTypes: ['modern_medicine_symptom'],
    properties: [
      {
        name: 'prevalence',
        type: 'string',
        description: '发生率',
        enum: ['very_common', 'common', 'uncommon', 'rare', 'very_rare']
      },
      {
        name: 'diagnosticValue',
        type: 'string',
        description: '诊断价值',
        enum: ['pathognomonic', 'high', 'moderate', 'low']
      }
    ]
  },
  {
    name: 'DIAGNOSES',
    description: '诊断关系，表示一种测试用于诊断某种疾病',
    sourceTypes: ['modern_medicine_test'],
    targetTypes: ['modern_medicine_disease', 'modern_medicine_condition'],
    properties: [
      {
        name: 'sensitivity',
        type: 'number',
        description: '敏感性（0-1）'
      },
      {
        name: 'specificity',
        type: 'number',
        description: '特异性（0-1）'
      },
      {
        name: 'positivePredicativeValue',
        type: 'number',
        description: '阳性预测值（0-1）'
      },
      {
        name: 'negativePredicativeValue',
        type: 'number',
        description: '阴性预测值（0-1）'
      }
    ]
  },
  {
    name: 'CAUSES_CONDITION',
    description: '致病关系，表示一个因素导致某种疾病',
    sourceTypes: ['*'],
    targetTypes: ['modern_medicine_disease', 'modern_medicine_condition'],
    properties: [
      {
        name: 'causalStrength',
        type: 'string',
        description: '因果强度',
        enum: ['definite', 'probable', 'possible', 'unlikely']
      },
      {
        name: 'riskRatio',
        type: 'number',
        description: '风险比'
      },
      {
        name: 'oddsRatio',
        type: 'number',
        description: '优势比'
      }
    ]
  },
  {
    name: 'INTERACTS_WITH_DRUG',
    description: '药物相互作用关系',
    sourceTypes: ['modern_medicine_drug', 'herb'],
    targetTypes: ['modern_medicine_drug', 'herb'],
    properties: [
      {
        name: 'interactionMechanism',
        type: 'string',
        description: '相互作用机制'
      },
      {
        name: 'effectOnLevel',
        type: 'string',
        description: '对药物水平的影响',
        enum: ['increase', 'decrease', 'no_effect', 'variable']
      },
      {
        name: 'clinicalSignificance',
        type: 'string',
        description: '临床重要性',
        enum: ['major', 'moderate', 'minor']
      },
      {
        name: 'recommendedAction',
        type: 'string',
        description: '推荐措施',
        enum: ['avoid_combination', 'monitor_therapy', 'no_action_needed']
      }
    ],
    bidirectional: true
  },
  {
    name: 'PART_OF',
    description: '组成关系，表示一个结构是另一个结构的一部分',
    sourceTypes: ['modern_medicine_anatomical_structure'],
    targetTypes: ['modern_medicine_anatomical_structure'],
    properties: [
      {
        name: 'partType',
        type: 'string',
        description: '部分类型',
        enum: ['structural', 'functional', 'developmental']
      }
    ]
  },
  {
    name: 'REGULATES',
    description: '调节关系，表示一个过程调节另一个过程',
    sourceTypes: ['modern_medicine_physiological_process', 'modern_medicine_drug'],
    targetTypes: ['modern_medicine_physiological_process', 'modern_medicine_pathological_process'],
    properties: [
      {
        name: 'regulationType',
        type: 'string',
        description: '调节类型',
        enum: ['up_regulation', 'down_regulation', 'modulation', 'inhibition', 'activation']
      },
      {
        name: 'mechanism',
        type: 'string',
        description: '调节机制'
      }
    ]
  },
  {
    name: 'INDICATES_RISK',
    description: '风险指示关系，表示一个生物标志物指示某种疾病风险',
    sourceTypes: ['modern_medicine_biomarker'],
    targetTypes: ['modern_medicine_disease', 'modern_medicine_condition'],
    properties: [
      {
        name: 'riskLevel',
        type: 'string',
        description: '风险级别',
        enum: ['high', 'moderate', 'low', 'protective']
      },
      {
        name: 'predictionAccuracy',
        type: 'number',
        description: '预测准确性（0-1）'
      }
    ]
  }
];

// 导出所有关系类型
export const ALL_RELATIONSHIP_TYPES: RelationshipType[] = [
  ...TCM_RELATIONSHIPS,
  ...MODERN_MEDICINE_RELATIONSHIPS
]; 