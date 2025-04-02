/**
 * 知识节点模型
 * 描述知识图谱中的节点数据结构
 */
const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');

/**
 * 知识节点类型枚举
 * @type {Object}
 */
const NodeType = {
  CONCEPT: 'concept',             // 概念
  ENTITY: 'entity',               // 实体
  SYMPTOM: 'symptom',             // 症状
  DISEASE: 'disease',             // 疾病
  TREATMENT: 'treatment',         // 治疗方法
  HERB: 'herb',                   // 中药
  FORMULA: 'formula',             // 方剂
  ACUPOINT: 'acupoint',           // 穴位
  MERIDIAN: 'meridian',           // 经络
  ORGAN: 'organ',                 // 脏腑
  SYNDROME: 'syndrome',           // 证型
  DIAGNOSTIC_METHOD: 'diagnostic_method', // 诊断方法
  CONSTITUTION: 'constitution',    // 体质
  FOOD: 'food',                   // 食物
  LIFESTYLE: 'lifestyle',         // 生活方式
  RESEARCH: 'research',           // 研究
  THEORY: 'theory',               // 理论
  PRACTITIONER: 'practitioner',   // 医家
  BOOK: 'book'                    // 经典著作
};

/**
 * 节点来源类型枚举
 * @type {Object}
 */
const SourceType = {
  CLASSIC: 'classic',             // 经典文献
  MODERN_RESEARCH: 'modern_research', // 现代研究
  EXPERT_OPINION: 'expert_opinion',   // 专家意见
  CLINICAL_PRACTICE: 'clinical_practice', // 临床实践
  STANDARD: 'standard',           // 标准规范
  USER_CONTRIBUTED: 'user_contributed', // 用户贡献
  INTERNAL: 'internal'            // 内部定义
};

/**
 * 知识节点验证模式
 * @type {Object}
 */
const knowledgeNodeSchema = Joi.object({
  id: Joi.string().uuid().default(() => uuidv4()),
  type: Joi.string().valid(...Object.values(NodeType)).required(),
  name: Joi.string().required(),
  nameEn: Joi.string(),
  aliases: Joi.array().items(Joi.string()),
  description: Joi.string().required(),
  properties: Joi.object().default({}),
  tags: Joi.array().items(Joi.string()),
  source: Joi.object({
    type: Joi.string().valid(...Object.values(SourceType)).required(),
    reference: Joi.string(),
    url: Joi.string().uri(),
    author: Joi.string(),
    year: Joi.number().integer().min(0),
    confidence: Joi.number().min(0).max(1).default(0.8),
    verified: Joi.boolean().default(false)
  }),
  media: Joi.object({
    images: Joi.array().items(
      Joi.object({
        url: Joi.string().uri().required(),
        caption: Joi.string(),
        type: Joi.string().valid('photo', 'diagram', 'illustration'),
        license: Joi.string()
      })
    ),
    videos: Joi.array().items(
      Joi.object({
        url: Joi.string().uri().required(),
        caption: Joi.string(),
        duration: Joi.number(),
        license: Joi.string()
      })
    ),
    audio: Joi.array().items(
      Joi.object({
        url: Joi.string().uri().required(),
        caption: Joi.string(),
        duration: Joi.number(),
        license: Joi.string()
      })
    )
  }).default({ images: [], videos: [], audio: [] }),
  vector: Joi.array().items(Joi.number()),
  createdAt: Joi.date().default(() => new Date()),
  updatedAt: Joi.date().default(() => new Date()),
  createdBy: Joi.string(),
  updatedBy: Joi.string()
});

/**
 * 根据节点类型获取特定类型节点的验证模式
 * @param {string} nodeType - 节点类型
 * @returns {Joi.ObjectSchema} 验证模式
 */
function getNodeSchemaByType(nodeType) {
  // 基础模式继承自通用知识节点模式
  let schema = knowledgeNodeSchema;
  
  // 根据节点类型扩展特定属性
  switch (nodeType) {
    case NodeType.DISEASE:
      schema = schema.keys({
        properties: Joi.object({
          icd10Code: Joi.string(),
          symptoms: Joi.array().items(Joi.string()),
          causes: Joi.array().items(Joi.string()),
          riskFactors: Joi.array().items(Joi.string()),
          complications: Joi.array().items(Joi.string()),
          preventions: Joi.array().items(Joi.string()),
          treatments: Joi.array().items(Joi.string()),
          prevalence: Joi.string(),
          prognosis: Joi.string(),
          tcmEtiology: Joi.string(),
          tcmPathogenesis: Joi.string(),
          tcmSyndromes: Joi.array().items(Joi.string())
        }).default({})
      });
      break;
      
    case NodeType.HERB:
      schema = schema.keys({
        properties: Joi.object({
          latinName: Joi.string(),
          family: Joi.string(),
          parts: Joi.array().items(Joi.string()),
          nature: Joi.string().valid('hot', 'warm', 'neutral', 'cool', 'cold'),
          taste: Joi.array().items(Joi.string().valid('sour', 'bitter', 'sweet', 'spicy', 'salty')),
          meridians: Joi.array().items(Joi.string()),
          functions: Joi.array().items(Joi.string()),
          indications: Joi.array().items(Joi.string()),
          contraindications: Joi.array().items(Joi.string()),
          dosage: Joi.string(),
          preparation: Joi.string(),
          toxicity: Joi.string(),
          activeCompounds: Joi.array().items(Joi.string()),
          modernResearch: Joi.string()
        }).default({})
      });
      break;
      
    case NodeType.FORMULA:
      schema = schema.keys({
        properties: Joi.object({
          composition: Joi.array().items(
            Joi.object({
              herb: Joi.string().required(),
              amount: Joi.string(),
              role: Joi.string().valid('君', '臣', '佐', '使')
            })
          ),
          functions: Joi.array().items(Joi.string()),
          indications: Joi.array().items(Joi.string()),
          contraindications: Joi.array().items(Joi.string()),
          administration: Joi.string(),
          modifications: Joi.array().items(
            Joi.object({
              condition: Joi.string().required(),
              change: Joi.string().required()
            })
          ),
          classicReference: Joi.string(),
          modernUsage: Joi.string()
        }).default({})
      });
      break;
      
    case NodeType.ACUPOINT:
      schema = schema.keys({
        properties: Joi.object({
          code: Joi.string(),
          meridian: Joi.string(),
          location: Joi.string().required(),
          functions: Joi.array().items(Joi.string()),
          indications: Joi.array().items(Joi.string()),
          needlingMethod: Joi.string(),
          needlingDepth: Joi.string(),
          contraindications: Joi.array().items(Joi.string()),
          anatomicalStructure: Joi.string(),
          extraMeridianPoints: Joi.boolean().default(false)
        }).default({})
      });
      break;
      
    case NodeType.SYNDROME:
      schema = schema.keys({
        properties: Joi.object({
          causes: Joi.array().items(Joi.string()),
          pathogenesis: Joi.string(),
          symptoms: Joi.array().items(Joi.string()),
          tonguePresentation: Joi.string(),
          pulsePresentation: Joi.string(),
          relatedOrgans: Joi.array().items(Joi.string()),
          relatedMeridians: Joi.array().items(Joi.string()),
          treatmentPrinciples: Joi.array().items(Joi.string()),
          relatedFormulas: Joi.array().items(Joi.string()),
          relatedAcupoints: Joi.array().items(Joi.string()),
          dietaryRecommendations: Joi.array().items(Joi.string()),
          lifestyleRecommendations: Joi.array().items(Joi.string())
        }).default({})
      });
      break;
      
    case NodeType.FOOD:
      schema = schema.keys({
        properties: Joi.object({
          category: Joi.string(),
          nature: Joi.string().valid('hot', 'warm', 'neutral', 'cool', 'cold'),
          taste: Joi.array().items(Joi.string().valid('sour', 'bitter', 'sweet', 'spicy', 'salty')),
          meridians: Joi.array().items(Joi.string()),
          functions: Joi.array().items(Joi.string()),
          indications: Joi.array().items(Joi.string()),
          contraindications: Joi.array().items(Joi.string()),
          nutritionalValue: Joi.object(),
          cookingMethods: Joi.array().items(Joi.string()),
          seasonality: Joi.string()
        }).default({})
      });
      break;
      
    case NodeType.CONSTITUTION:
      schema = schema.keys({
        properties: Joi.object({
          characteristics: Joi.array().items(
            Joi.object({
              category: Joi.string().required(),
              traits: Joi.array().items(Joi.string()).required()
            })
          ),
          tendencies: Joi.array().items(Joi.string()),
          recommendations: Joi.object({
            diet: Joi.array().items(Joi.string()),
            lifestyle: Joi.array().items(Joi.string()),
            exercise: Joi.array().items(Joi.string()),
            environment: Joi.array().items(Joi.string()),
            avoid: Joi.array().items(Joi.string())
          }),
          relatedDiseases: Joi.array().items(Joi.string())
        }).default({})
      });
      break;
      
    case NodeType.CONCEPT:
    case NodeType.THEORY:
      schema = schema.keys({
        properties: Joi.object({
          history: Joi.string(),
          principles: Joi.array().items(Joi.string()),
          applications: Joi.array().items(Joi.string()),
          relatedConcepts: Joi.array().items(Joi.string()),
          modernInterpretation: Joi.string(),
          classicReferences: Joi.array().items(Joi.string())
        }).default({})
      });
      break;
  }
  
  return schema;
}

/**
 * 创建知识节点
 * @param {Object} data - 知识节点数据
 * @returns {Object} 验证后的知识节点对象
 */
function createKnowledgeNode(data) {
  // 获取特定类型的验证模式
  const schema = getNodeSchemaByType(data.type);
  
  // 验证节点数据
  const { error, value } = schema.validate(data);
  if (error) {
    throw new Error(`知识节点验证失败: ${error.message}`);
  }
  
  return value;
}

/**
 * 更新知识节点
 * @param {Object} node - 已有知识节点
 * @param {Object} updates - 更新数据
 * @returns {Object} 更新后的知识节点
 */
function updateKnowledgeNode(node, updates) {
  if (!node || !updates) {
    throw new Error('更新知识节点需要提供有效的节点和更新数据');
  }
  
  // 合并更新数据
  const updatedNode = {
    ...node,
    ...updates,
    updatedAt: new Date()
  };
  
  // 如果更新了节点类型，使用新的类型验证模式
  const schema = getNodeSchemaByType(updatedNode.type);
  
  // 验证更新后的节点
  const { error, value } = schema.validate(updatedNode);
  if (error) {
    throw new Error(`知识节点更新验证失败: ${error.message}`);
  }
  
  return value;
}

/**
 * 验证知识节点ID
 * @param {string} id - 知识节点ID
 * @returns {boolean} 是否为有效ID
 */
function isValidNodeId(id) {
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidPattern.test(id);
}

/**
 * 生成用于向量搜索的文本表示
 * @param {Object} node - 知识节点
 * @returns {string} 节点的文本表示
 */
function generateNodeTextRepresentation(node) {
  if (!node || !node.name || !node.description) {
    throw new Error('生成节点文本表示需要提供包含名称和描述的有效节点');
  }
  
  // 基础文本表示
  let textParts = [
    `名称: ${node.name}`,
    `类型: ${getNodeTypeName(node.type)}`,
    `描述: ${node.description}`
  ];
  
  // 添加别名（如果有）
  if (node.aliases && node.aliases.length > 0) {
    textParts.push(`别名: ${node.aliases.join(', ')}`);
  }
  
  // 添加标签（如果有）
  if (node.tags && node.tags.length > 0) {
    textParts.push(`标签: ${node.tags.join(', ')}`);
  }
  
  // 添加特定类型的属性
  if (node.properties) {
    switch (node.type) {
      case NodeType.DISEASE:
        if (node.properties.symptoms && node.properties.symptoms.length > 0) {
          textParts.push(`症状: ${node.properties.symptoms.join(', ')}`);
        }
        if (node.properties.tcmEtiology) {
          textParts.push(`中医病因: ${node.properties.tcmEtiology}`);
        }
        break;
        
      case NodeType.HERB:
        if (node.properties.functions && node.properties.functions.length > 0) {
          textParts.push(`功效: ${node.properties.functions.join(', ')}`);
        }
        if (node.properties.indications && node.properties.indications.length > 0) {
          textParts.push(`适应症: ${node.properties.indications.join(', ')}`);
        }
        break;
        
      case NodeType.SYNDROME:
        if (node.properties.symptoms && node.properties.symptoms.length > 0) {
          textParts.push(`证候表现: ${node.properties.symptoms.join(', ')}`);
        }
        if (node.properties.treatmentPrinciples && node.properties.treatmentPrinciples.length > 0) {
          textParts.push(`治疗原则: ${node.properties.treatmentPrinciples.join(', ')}`);
        }
        break;
    }
  }
  
  return textParts.join('\n');
}

/**
 * 获取节点类型名称
 * @param {string} nodeType - 节点类型
 * @returns {string} 节点类型名称
 */
function getNodeTypeName(nodeType) {
  const nodeTypeNames = {
    [NodeType.CONCEPT]: '概念',
    [NodeType.ENTITY]: '实体',
    [NodeType.SYMPTOM]: '症状',
    [NodeType.DISEASE]: '疾病',
    [NodeType.TREATMENT]: '治疗方法',
    [NodeType.HERB]: '中药',
    [NodeType.FORMULA]: '方剂',
    [NodeType.ACUPOINT]: '穴位',
    [NodeType.MERIDIAN]: '经络',
    [NodeType.ORGAN]: '脏腑',
    [NodeType.SYNDROME]: '证型',
    [NodeType.DIAGNOSTIC_METHOD]: '诊断方法',
    [NodeType.CONSTITUTION]: '体质',
    [NodeType.FOOD]: '食物',
    [NodeType.LIFESTYLE]: '生活方式',
    [NodeType.RESEARCH]: '研究',
    [NodeType.THEORY]: '理论',
    [NodeType.PRACTITIONER]: '医家',
    [NodeType.BOOK]: '经典著作'
  };
  
  return nodeTypeNames[nodeType] || '未知类型';
}

module.exports = {
  NodeType,
  SourceType,
  knowledgeNodeSchema,
  getNodeSchemaByType,
  createKnowledgeNode,
  updateKnowledgeNode,
  isValidNodeId,
  generateNodeTextRepresentation,
  getNodeTypeName
}; 