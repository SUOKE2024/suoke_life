/**
 * 知识关系模型
 * 描述知识图谱中节点之间的关系
 */
const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');
const { NodeType } = require('./knowledge-node.model');

/**
 * 关系类型枚举
 * @type {Object}
 */
const RelationType = {
  IS_A: 'is_a',                     // 是一种
  PART_OF: 'part_of',               // 是部分
  HAS_PART: 'has_part',             // 拥有部分
  CAUSES: 'causes',                 // 导致
  CAUSED_BY: 'caused_by',           // 由...导致
  TREATS: 'treats',                 // 治疗
  TREATED_BY: 'treated_by',         // 被...治疗
  PREVENTS: 'prevents',             // 预防
  PREVENTED_BY: 'prevented_by',     // 被...预防
  INDICATES: 'indicates',           // 指示
  INDICATED_BY: 'indicated_by',     // 被...指示
  CONTRADICTS: 'contradicts',       // 禁忌
  CONTRADICTED_BY: 'contradicted_by', // 被...禁忌
  RELATED_TO: 'related_to',         // 相关
  SIMILAR_TO: 'similar_to',         // 相似
  OPPOSITE_OF: 'opposite_of',       // 相反
  MANIFESTS_AS: 'manifests_as',     // 表现为
  MANIFESTED_IN: 'manifested_in',   // 体现在
  ENTERS: 'enters',                 // 入(经络)
  ENTERED_BY: 'entered_by',         // 被...所入
  COMPOSED_OF: 'composed_of',       // 组成
  COMPONENT_OF: 'component_of',     // 组成部分
  LOCATED_AT: 'located_at',         // 位于
  LOCATION_OF: 'location_of',       // 是...的位置
  BELONGS_TO: 'belongs_to',         // 属于
  CONTAINS: 'contains',             // 包含
  PRECEDES: 'precedes',             // 先于
  FOLLOWS: 'follows',               // 后于
  TRANSFORMS_INTO: 'transforms_into', // 转化为
  TRANSFORMED_FROM: 'transformed_from', // 从...转化而来
  SYNERGIZES_WITH: 'synergizes_with', // 协同
  ANTAGONIZES: 'antagonizes',       // 拮抗
  REGULATES: 'regulates',           // 调节
  REGULATED_BY: 'regulated_by',     // 被...调节
  DERIVED_FROM: 'derived_from',     // 源自
  BASIS_OF: 'basis_of',             // 是...的基础
  DISCUSSED_IN: 'discussed_in',     // 在...中讨论
  DISCUSSES: 'discusses',           // 讨论了
  PRACTICED_BY: 'practiced_by',     // 由...实践
  PRACTICES: 'practices'            // 实践
};

/**
 * 关系合法性规则
 * 定义哪些类型的节点之间可以建立哪些类型的关系
 * @type {Object}
 */
const relationRules = {
  // 疾病相关关系
  [NodeType.DISEASE]: {
    [RelationType.CAUSED_BY]: [NodeType.CONCEPT, NodeType.ENTITY, NodeType.DISEASE],
    [RelationType.MANIFESTS_AS]: [NodeType.SYMPTOM],
    [RelationType.TREATED_BY]: [NodeType.HERB, NodeType.FORMULA, NodeType.TREATMENT, NodeType.ACUPOINT],
    [RelationType.PREVENTED_BY]: [NodeType.HERB, NodeType.FORMULA, NodeType.TREATMENT, NodeType.LIFESTYLE, NodeType.FOOD],
    [RelationType.RELATED_TO]: [NodeType.DISEASE, NodeType.SYNDROME],
    [RelationType.IS_A]: [NodeType.DISEASE]
  },
  
  // 症状相关关系
  [NodeType.SYMPTOM]: {
    [RelationType.INDICATES]: [NodeType.DISEASE, NodeType.SYNDROME],
    [RelationType.CAUSED_BY]: [NodeType.CONCEPT, NodeType.ENTITY],
    [RelationType.TREATED_BY]: [NodeType.HERB, NodeType.FORMULA, NodeType.TREATMENT, NodeType.ACUPOINT],
    [RelationType.RELATED_TO]: [NodeType.SYMPTOM],
    [RelationType.MANIFESTED_IN]: [NodeType.ORGAN, NodeType.MERIDIAN]
  },
  
  // 中药相关关系
  [NodeType.HERB]: {
    [RelationType.TREATS]: [NodeType.DISEASE, NodeType.SYMPTOM, NodeType.SYNDROME],
    [RelationType.ENTERS]: [NodeType.MERIDIAN, NodeType.ORGAN],
    [RelationType.CONTRADICTS]: [NodeType.HERB, NodeType.FOOD, NodeType.DISEASE, NodeType.CONSTITUTION],
    [RelationType.SYNERGIZES_WITH]: [NodeType.HERB],
    [RelationType.ANTAGONIZES]: [NodeType.HERB],
    [RelationType.COMPONENT_OF]: [NodeType.FORMULA]
  },
  
  // 方剂相关关系
  [NodeType.FORMULA]: {
    [RelationType.TREATS]: [NodeType.DISEASE, NodeType.SYMPTOM, NodeType.SYNDROME],
    [RelationType.COMPOSED_OF]: [NodeType.HERB],
    [RelationType.DISCUSSED_IN]: [NodeType.BOOK],
    [RelationType.CONTRADICTS]: [NodeType.DISEASE, NodeType.CONSTITUTION],
    [RelationType.DERIVED_FROM]: [NodeType.FORMULA]
  },
  
  // 穴位相关关系
  [NodeType.ACUPOINT]: {
    [RelationType.TREATS]: [NodeType.DISEASE, NodeType.SYMPTOM, NodeType.SYNDROME],
    [RelationType.LOCATED_AT]: [NodeType.MERIDIAN],
    [RelationType.RELATED_TO]: [NodeType.ORGAN, NodeType.ACUPOINT],
    [RelationType.SYNERGIZES_WITH]: [NodeType.ACUPOINT]
  },
  
  // 经络相关关系
  [NodeType.MERIDIAN]: {
    [RelationType.RELATED_TO]: [NodeType.ORGAN, NodeType.MERIDIAN],
    [RelationType.LOCATION_OF]: [NodeType.ACUPOINT],
    [RelationType.ENTERED_BY]: [NodeType.HERB]
  },
  
  // 脏腑相关关系
  [NodeType.ORGAN]: {
    [RelationType.RELATED_TO]: [NodeType.MERIDIAN, NodeType.ORGAN],
    [RelationType.REGULATES]: [NodeType.ORGAN, NodeType.ENTITY],
    [RelationType.REGULATED_BY]: [NodeType.ORGAN, NodeType.ENTITY, NodeType.HERB, NodeType.FORMULA]
  },
  
  // 证型相关关系
  [NodeType.SYNDROME]: {
    [RelationType.MANIFESTS_AS]: [NodeType.SYMPTOM],
    [RelationType.RELATED_TO]: [NodeType.DISEASE, NodeType.ORGAN, NodeType.MERIDIAN],
    [RelationType.TREATED_BY]: [NodeType.HERB, NodeType.FORMULA, NodeType.TREATMENT, NodeType.ACUPOINT],
    [RelationType.TRANSFORMS_INTO]: [NodeType.SYNDROME],
    [RelationType.TRANSFORMED_FROM]: [NodeType.SYNDROME]
  },
  
  // 体质相关关系
  [NodeType.CONSTITUTION]: {
    [RelationType.PREDISPOSES_TO]: [NodeType.DISEASE, NodeType.SYNDROME],
    [RelationType.REGULATED_BY]: [NodeType.LIFESTYLE, NodeType.FOOD, NodeType.HERB, NodeType.FORMULA],
    [RelationType.CONTRADICTS]: [NodeType.FOOD, NodeType.HERB, NodeType.LIFESTYLE],
    [RelationType.RELATED_TO]: [NodeType.CONCEPT]
  },
  
  // 食物相关关系
  [NodeType.FOOD]: {
    [RelationType.TREATS]: [NodeType.DISEASE, NodeType.SYMPTOM, NodeType.SYNDROME],
    [RelationType.PREVENTS]: [NodeType.DISEASE],
    [RelationType.CONTRADICTS]: [NodeType.DISEASE, NodeType.CONSTITUTION],
    [RelationType.ENTERS]: [NodeType.MERIDIAN, NodeType.ORGAN],
    [RelationType.SYNERGIZES_WITH]: [NodeType.FOOD, NodeType.HERB],
    [RelationType.ANTAGONIZES]: [NodeType.FOOD, NodeType.HERB]
  },
  
  // 概念相关关系
  [NodeType.CONCEPT]: {
    [RelationType.RELATED_TO]: [NodeType.CONCEPT, NodeType.THEORY],
    [RelationType.BASIS_OF]: [NodeType.THEORY, NodeType.TREATMENT],
    [RelationType.DISCUSSED_IN]: [NodeType.BOOK],
    [RelationType.IS_A]: [NodeType.CONCEPT],
    [RelationType.OPPOSITE_OF]: [NodeType.CONCEPT]
  },
  
  // 理论相关关系
  [NodeType.THEORY]: {
    [RelationType.DERIVED_FROM]: [NodeType.CONCEPT, NodeType.THEORY],
    [RelationType.DISCUSSED_IN]: [NodeType.BOOK],
    [RelationType.PRACTICED_BY]: [NodeType.PRACTITIONER],
    [RelationType.BASIS_OF]: [NodeType.THEORY, NodeType.TREATMENT, NodeType.DIAGNOSTIC_METHOD]
  },
  
  // 医家相关关系
  [NodeType.PRACTITIONER]: {
    [RelationType.PRACTICES]: [NodeType.THEORY],
    [RelationType.DISCUSSES]: [NodeType.CONCEPT, NodeType.THEORY, NodeType.TREATMENT],
    [RelationType.RELATED_TO]: [NodeType.PRACTITIONER]
  },
  
  // 经典著作相关关系
  [NodeType.BOOK]: {
    [RelationType.DISCUSSES]: [NodeType.CONCEPT, NodeType.THEORY, NodeType.HERB, NodeType.FORMULA],
    [RelationType.WRITTEN_BY]: [NodeType.PRACTITIONER],
    [RelationType.RELATED_TO]: [NodeType.BOOK]
  }
};

/**
 * 知识关系验证模式
 * @type {Object}
 */
const knowledgeRelationSchema = Joi.object({
  id: Joi.string().uuid().default(() => uuidv4()),
  type: Joi.string().valid(...Object.values(RelationType)).required(),
  sourceId: Joi.string().uuid().required(),
  sourceType: Joi.string().valid(...Object.values(NodeType)).required(),
  targetId: Joi.string().uuid().required(),
  targetType: Joi.string().valid(...Object.values(NodeType)).required(),
  isDirected: Joi.boolean().default(true),
  properties: Joi.object().default({}),
  weight: Joi.number().min(0).max(1).default(1),
  source: Joi.object({
    type: Joi.string().valid('classic', 'modern_research', 'expert_opinion', 'clinical_practice', 'standard', 'user_contributed', 'internal').required(),
    reference: Joi.string(),
    confidence: Joi.number().min(0).max(1).default(0.8),
    verified: Joi.boolean().default(false)
  }).default({ type: 'internal', confidence: 0.8, verified: false }),
  createdAt: Joi.date().default(() => new Date()),
  updatedAt: Joi.date().default(() => new Date()),
  createdBy: Joi.string(),
  updatedBy: Joi.string()
});

/**
 * 反向关系映射
 * 用于自动创建反向关系
 * @type {Object}
 */
const inverseRelationMap = {
  [RelationType.IS_A]: null, // 没有自动反向关系
  [RelationType.PART_OF]: RelationType.HAS_PART,
  [RelationType.HAS_PART]: RelationType.PART_OF,
  [RelationType.CAUSES]: RelationType.CAUSED_BY,
  [RelationType.CAUSED_BY]: RelationType.CAUSES,
  [RelationType.TREATS]: RelationType.TREATED_BY,
  [RelationType.TREATED_BY]: RelationType.TREATS,
  [RelationType.PREVENTS]: RelationType.PREVENTED_BY,
  [RelationType.PREVENTED_BY]: RelationType.PREVENTS,
  [RelationType.INDICATES]: RelationType.INDICATED_BY,
  [RelationType.INDICATED_BY]: RelationType.INDICATES,
  [RelationType.CONTRADICTS]: RelationType.CONTRADICTED_BY,
  [RelationType.CONTRADICTED_BY]: RelationType.CONTRADICTS,
  [RelationType.RELATED_TO]: RelationType.RELATED_TO,
  [RelationType.SIMILAR_TO]: RelationType.SIMILAR_TO,
  [RelationType.OPPOSITE_OF]: RelationType.OPPOSITE_OF,
  [RelationType.MANIFESTS_AS]: RelationType.MANIFESTED_IN,
  [RelationType.MANIFESTED_IN]: RelationType.MANIFESTS_AS,
  [RelationType.ENTERS]: RelationType.ENTERED_BY,
  [RelationType.ENTERED_BY]: RelationType.ENTERS,
  [RelationType.COMPOSED_OF]: RelationType.COMPONENT_OF,
  [RelationType.COMPONENT_OF]: RelationType.COMPOSED_OF,
  [RelationType.LOCATED_AT]: RelationType.LOCATION_OF,
  [RelationType.LOCATION_OF]: RelationType.LOCATED_AT,
  [RelationType.BELONGS_TO]: RelationType.CONTAINS,
  [RelationType.CONTAINS]: RelationType.BELONGS_TO,
  [RelationType.PRECEDES]: RelationType.FOLLOWS,
  [RelationType.FOLLOWS]: RelationType.PRECEDES,
  [RelationType.TRANSFORMS_INTO]: RelationType.TRANSFORMED_FROM,
  [RelationType.TRANSFORMED_FROM]: RelationType.TRANSFORMS_INTO,
  [RelationType.SYNERGIZES_WITH]: RelationType.SYNERGIZES_WITH,
  [RelationType.ANTAGONIZES]: RelationType.ANTAGONIZES,
  [RelationType.REGULATES]: RelationType.REGULATED_BY,
  [RelationType.REGULATED_BY]: RelationType.REGULATES,
  [RelationType.DERIVED_FROM]: RelationType.BASIS_OF,
  [RelationType.BASIS_OF]: RelationType.DERIVED_FROM,
  [RelationType.DISCUSSED_IN]: RelationType.DISCUSSES,
  [RelationType.DISCUSSES]: RelationType.DISCUSSED_IN,
  [RelationType.PRACTICED_BY]: RelationType.PRACTICES,
  [RelationType.PRACTICES]: RelationType.PRACTICED_BY
};

/**
 * 检查关系是否合法
 * @param {string} sourceType - 源节点类型
 * @param {string} relationType - 关系类型
 * @param {string} targetType - 目标节点类型
 * @returns {boolean} 关系是否合法
 */
function isValidRelation(sourceType, relationType, targetType) {
  // 检查源节点类型是否支持该关系类型
  if (!relationRules[sourceType] || !relationRules[sourceType][relationType]) {
    return false;
  }
  
  // 检查目标节点类型是否在允许的类型列表中
  return relationRules[sourceType][relationType].includes(targetType);
}

/**
 * 获取关系的反向关系类型
 * @param {string} relationType - 关系类型
 * @returns {string|null} 反向关系类型，如果没有反向关系则返回null
 */
function getInverseRelationType(relationType) {
  return inverseRelationMap[relationType] || null;
}

/**
 * 创建反向关系
 * @param {Object} relation - 原始关系
 * @returns {Object|null} 反向关系，如果没有反向关系则返回null
 */
function createInverseRelation(relation) {
  const inverseType = getInverseRelationType(relation.type);
  if (!inverseType) {
    return null;
  }
  
  return {
    id: uuidv4(),
    type: inverseType,
    sourceId: relation.targetId,
    sourceType: relation.targetType,
    targetId: relation.sourceId,
    targetType: relation.sourceType,
    isDirected: relation.isDirected,
    properties: { ...relation.properties, isInverse: true },
    weight: relation.weight,
    source: relation.source,
    createdAt: relation.createdAt,
    updatedAt: relation.updatedAt,
    createdBy: relation.createdBy,
    updatedBy: relation.updatedBy
  };
}

/**
 * 创建知识关系
 * @param {Object} data - 关系数据
 * @returns {Object} 验证后的关系对象
 */
function createKnowledgeRelation(data) {
  // 验证关系符合节点类型规则
  if (!isValidRelation(data.sourceType, data.type, data.targetType)) {
    throw new Error(`无效的关系: ${data.sourceType} --[${data.type}]--> ${data.targetType}`);
  }
  
  // 验证关系数据
  const { error, value } = knowledgeRelationSchema.validate(data);
  if (error) {
    throw new Error(`知识关系验证失败: ${error.message}`);
  }
  
  return value;
}

/**
 * 更新知识关系
 * @param {Object} relation - 已有关系
 * @param {Object} updates - 更新数据
 * @returns {Object} 更新后的关系
 */
function updateKnowledgeRelation(relation, updates) {
  if (!relation || !updates) {
    throw new Error('更新知识关系需要提供有效的关系和更新数据');
  }
  
  // 如果更新了关系类型、源节点类型或目标节点类型，需要重新验证关系合法性
  if (updates.type || updates.sourceType || updates.targetType) {
    const sourceType = updates.sourceType || relation.sourceType;
    const relationType = updates.type || relation.type;
    const targetType = updates.targetType || relation.targetType;
    
    if (!isValidRelation(sourceType, relationType, targetType)) {
      throw new Error(`无效的关系: ${sourceType} --[${relationType}]--> ${targetType}`);
    }
  }
  
  // 合并更新数据
  const updatedRelation = {
    ...relation,
    ...updates,
    updatedAt: new Date()
  };
  
  // 验证更新后的关系
  const { error, value } = knowledgeRelationSchema.validate(updatedRelation);
  if (error) {
    throw new Error(`知识关系更新验证失败: ${error.message}`);
  }
  
  return value;
}

/**
 * 获取关系类型名称
 * @param {string} relationType - 关系类型
 * @returns {string} 关系类型名称
 */
function getRelationTypeName(relationType) {
  const relationTypeNames = {
    [RelationType.IS_A]: '是一种',
    [RelationType.PART_OF]: '是部分',
    [RelationType.HAS_PART]: '拥有部分',
    [RelationType.CAUSES]: '导致',
    [RelationType.CAUSED_BY]: '由...导致',
    [RelationType.TREATS]: '治疗',
    [RelationType.TREATED_BY]: '被...治疗',
    [RelationType.PREVENTS]: '预防',
    [RelationType.PREVENTED_BY]: '被...预防',
    [RelationType.INDICATES]: '指示',
    [RelationType.INDICATED_BY]: '被...指示',
    [RelationType.CONTRADICTS]: '禁忌',
    [RelationType.CONTRADICTED_BY]: '被...禁忌',
    [RelationType.RELATED_TO]: '相关',
    [RelationType.SIMILAR_TO]: '相似',
    [RelationType.OPPOSITE_OF]: '相反',
    [RelationType.MANIFESTS_AS]: '表现为',
    [RelationType.MANIFESTED_IN]: '体现在',
    [RelationType.ENTERS]: '入',
    [RelationType.ENTERED_BY]: '被...所入',
    [RelationType.COMPOSED_OF]: '组成',
    [RelationType.COMPONENT_OF]: '组成部分',
    [RelationType.LOCATED_AT]: '位于',
    [RelationType.LOCATION_OF]: '是...的位置',
    [RelationType.BELONGS_TO]: '属于',
    [RelationType.CONTAINS]: '包含',
    [RelationType.PRECEDES]: '先于',
    [RelationType.FOLLOWS]: '后于',
    [RelationType.TRANSFORMS_INTO]: '转化为',
    [RelationType.TRANSFORMED_FROM]: '从...转化而来',
    [RelationType.SYNERGIZES_WITH]: '协同',
    [RelationType.ANTAGONIZES]: '拮抗',
    [RelationType.REGULATES]: '调节',
    [RelationType.REGULATED_BY]: '被...调节',
    [RelationType.DERIVED_FROM]: '源自',
    [RelationType.BASIS_OF]: '是...的基础',
    [RelationType.DISCUSSED_IN]: '在...中讨论',
    [RelationType.DISCUSSES]: '讨论了',
    [RelationType.PRACTICED_BY]: '由...实践',
    [RelationType.PRACTICES]: '实践'
  };
  
  return relationTypeNames[relationType] || '未知关系';
}

/**
 * 获取关系描述
 * @param {Object} relation - 关系对象
 * @param {Object} sourceNode - 源节点
 * @param {Object} targetNode - 目标节点
 * @returns {string} 关系描述
 */
function getRelationDescription(relation, sourceNode, targetNode) {
  if (!relation || !sourceNode || !targetNode) {
    throw new Error('获取关系描述需要提供有效的关系和节点');
  }
  
  const relationName = getRelationTypeName(relation.type);
  const sourceName = sourceNode.name;
  const targetName = targetNode.name;
  
  return `${sourceName} ${relationName} ${targetName}`;
}

module.exports = {
  RelationType,
  knowledgeRelationSchema,
  relationRules,
  inverseRelationMap,
  isValidRelation,
  getInverseRelationType,
  createInverseRelation,
  createKnowledgeRelation,
  updateKnowledgeRelation,
  getRelationTypeName,
  getRelationDescription
}; 