export interface KnowledgeNode {
  id: string;
  type: string;
  name: string;
  content: string;
  domain: string;
  tags: string[];
  metadata: Record<string, any>;
  vector?: number[];
  createdAt: Date;
  updatedAt: Date;
}

export interface KnowledgeRelation {
  id: string;
  type: string;
  fromNode: string;
  toNode: string;
  properties: Record<string, any>;
  weight: number;
  createdAt: Date;
  updatedAt: Date;
}

export enum KnowledgeDomain {
  TCM_BASIC = "中医基础理论",
  TCM_FORMULA = "方剂学",
  TCM_HERB = "中药学",
  TCM_DIAGNOSIS = "诊断学",
  TCM_CONSTITUTION = "体质学说",
  TCM_DIET = "食疗学",
  TCM_ACUPUNCTURE = "针灸学",
  TCM_MASSAGE = "气功推拿",
  MODERN_HEALTH = "现代健康"
}

export enum RelationType {
  CONTAINS = "包含",
  BELONGS_TO = "属于",
  ACTS_ON = "作用于",
  RELIEVES = "缓解",
  AGGRAVATES = "加重",
  RELATED = "相关",
  INHERITS = "继承",
  ANTAGONIZES = "拮抗",
  COMPATIBLE = "配伍",
  TREATS = "主治",
  EFFECTS = "功效",
  INDICATION = "适应证",
  CONTRAINDICATION = "禁忌证",
  ORIGIN = "产地",
  PRESERVATION = "养护",
  SYNDROME_METHOD = "证-法关系",
  METHOD_FORMULA = "法-方关系",
  FORMULA_HERB = "方-药关系",
  SYMPTOM_SYNDROME = "症-证关系",
  ORGAN_MANIFESTATION = "脏-象关系",
  YIN_YANG = "阴阳关系",
  FIVE_ELEMENTS = "五行关系",
  MERIDIAN_CONNECTION = "经络联系",
  CONSTITUTION_RELATED = "体质相关"
}