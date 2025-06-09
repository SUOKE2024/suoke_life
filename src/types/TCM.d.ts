/**
* * 索克生活 - 中医辨证类型定义
* Traditional Chinese Medicine (TCM) Type Definitions;
//
* - MCP时间戳服务类型
* - 中医辨证基础类型
* - 生物标志物数据类型
* - 四诊数据类型
* - 智能体辨证结果类型
// ==================== MCP时间戳服务类型 ====================
/**
* * MCP时间戳服务标准类型
* 确保时间数据的一致性和可追溯性
export interface MCPTimestamp {
}
};
  /** ISO 8601格式的时间戳    ;
  iso: string;
  /** Unix时间戳（毫秒）
  unix: number;
  /** 时区信息
  timezone: string;
  /** 时间戳来源
  source: "device | "server" | sensor" | "manual;"
  /** 时间戳精度等级
  precision: "second" | millisecond" | "microsecond;
  /** 是否经过NTP同步
  synchronized: boolean; */
} *///
*///
/**
* * 时间范围类型
export interface TimeRange {
};
};
  start: MCPTimestamp,
  end: MCPTimestamp;
  duration?: number; // 持续时间（毫秒）
}
// ==================== 中医基础类型 ====================
/**
* * 中医体质类型
export type TCMConstitution = | "qi-deficiency"      // 气虚质
  | yang-deficiency"    // 阳虚质"
  | "yin-deficiency     // 阴虚质"
  | "phlegm-dampness"    // 痰湿质
  | damp-heat"          // 湿热质"
  | "blood-stasis       // 血瘀质";
  | "qi-stagnation"      // 气郁质;
  | special-diathesis"  // 特禀质";
  | "balanced           // 平和质";
/**
* ;
* 中医证候类型;
export interface TCMSyndrome {
}
};
  /** 证候名称    ;
  name: string;
  /** 证候代码
  code: string;
  /** 证候分类
  category: "zang-fu" | qi-blood" | "six-channels | "wei-qi-ying-blood";
  /** 证候严重程度
  severity: mild" | "moderate | "severe";
  /** 置信度 (0-1)
  confidence: number;
  /** 相关症状
  symptoms: string[];
  /** 辨证时间
  diagnosedAt: MCPTimestamp; */
} *///
*///
/**
* * 中医五脏六腑状态
export interface TCMOrganState {
}
};
  /** 脏腑名称    ;
  organ: heart" | "liver | "spleen" | lung" | "kidney | "gallbladder" | stomach" | "small-intestine | "large-intestine" | bladder" | "triple-heater | "pericardium";
  /** 功能状态
  state: normal" | "hyperactive | "deficient" | stagnant;
  /** 状态评分 (0-100)
  score: number;
  /** 相关症状
  symptoms: string[];
  /** 评估时间
  assessedAt: MCPTimestamp;
} */
  ==================== 生物标志物增强类型 ==================== *///
*///
/**
* * 增强的生物标志物数据类型
* 集成MCP时间戳服务和中医辨证关联
export interface BiomarkerData {
}
};
  /** 标志物ID    ;
  id: string;
  /** 标志物名称
  name: string;
  /** 标志物类型
  type: "vital-sign | "biochemical" | hormonal" | "inflammatory | "metabolic" | genetic";
  /** 测量值
  value: number;
  /** 测量单位
  unit: string;
  /** MCP标准时间戳
  timestamp: MCPTimestamp;
  /** 参考范围
  referenceRange: {,
  min: number;
    max: number;
    optimal?: number;
  };
  /** 测量设备信息
  device?: {
    id: string,
  name: string;,
  model: string;
    calibrationDate?: MCPTimestamp;
  };
  /** 中医辨证关联
  tcmAssociation: {
    /** 关联的脏腑
    relatedOrgans: TCMOrganState[];
    /** 关联的证候
    relatedSyndromes: TCMSyndrome[];
    /** 中医意义解释
    tcmInterpretation: string;
    /** 对应的中医指标
    tcmIndicators: string[];
  };
  /** 数据质量指标
  quality: {
    /** 数据可靠性 (0-1)
    reliability: number;
    /** 是否异常值
    isOutlier: boolean;
    /** 数据来源
    source: "manual | "device" | lab" | "estimated;"
  };
  /** 趋势信息
  trend?: {
    direction: "increasing" | decreasing" | "stable,
  rate: number; // 变化率,
  significance: "significant" | moderate" | "minimal;
  };
} */
  ==================== 四诊数据类型 ==================== *///
*///
/**
* * 望诊数据
export interface InspectionData {
}
}
  /** 面色
  complexion: {,
  color: "red" | yellow" | "white | "black" | blue"";
    luster: "lustrous | "dull,
  description: string;
  };
  /** 舌诊
  tongue: {,
  body: {
      color: pale" | "red | "dark-red" | purple,
  texture: "tender | "normal" | old";,
  shape: "thin | "normal" | fat" | "cracked;"
    };
    coating: {,
  color: "white" | yellow" | "gray | "black";
      thickness: thin" | "thick,
  moisture: "moist" | dry" | "slippery;
    };
  };
  /** 精神状态
  spirit: "vigorous" | normal" | "listless | "restless";
  /** 体型
  bodyType: thin" | "normal | "fat" | muscular;
  /** 检查时间
  timestamp: MCPTimestamp; */
} *///
*///
/**
* * 闻诊数据
export interface AuscultationData {
}
}
  /** 声音   ;
  voice: {volume: "loud | "normal" | low",
  tone: "high | "normal" | low";,
  clarity: "clear | "hoarse" | weak";
  };
  /** 呼吸
  breathing: {,
  pattern: "normal | "short" | deep" | "irregular;"
    sound: "normal" | wheezing" | "rattling;
  };
  /** 气味
  odor?: {
    type: "normal" | sour" | "sweet | "fishy" | rotten,
  intensity: "mild | "moderate" | strong";
  };
  /** 检查时间
  timestamp: MCPTimestamp; */
} *///
*///
/**
* * 问诊数据
export interface InquiryData {
}
};
  /** 主诉    ;
  chiefComplaint: string;
  /** 现病史
  presentIllness: string;
  /** 既往史
  pastHistory: string[];
  /** 家族史
  familyHistory: string[];
  /** 个人史
  personalHistory: {,
  lifestyle: string;
    diet: string,
  sleep: string;,
  exercise: string,
  stress: string;
  };
  /** 症状评分
  symptoms: Array<{,
  name: string;
    severity: number; // 1-10,
  duration: string;,
  frequency: string;
  }>;
  /** 问诊时间
  timestamp: MCPTimestamp; */
} *///
*///
/**
* * 切诊数据
export interface PalpationData {
}
}
  /** 脉诊
  pulse: {/** 脉位    ,
  position: "superficial | "deep" | middle";
    /** 脉率
    rate: number; ///    分钟
    /** 脉律
    rhythm: "regular | "irregular" | intermittent"
    /** 脉力
    strength: "weak | "normal" | strong";
    /** 脉形
    shape: "thin | "thick" | long" | "short;"
    /** 脉势
    quality: "floating" | sinking" | "slow | "rapid" | slippery" | "rough | "wiry" | tight;
  };
  /** 按诊
  palpation: {
    /** 腹诊
    abdomen: {,
  tenderness: boolean;
      distension: boolean,
  masses: boolean;,
  temperature: "cold | "normal" | hot";
    };
    /** 穴位按压
    acupoints: Array<{,
  name: string;
      tenderness: boolean,
  sensitivity: number; // 1-10;
    }>
  };
  /** 检查时间
  timestamp: MCPTimestamp;
} */
  ==================== 五诊数据类型 ==================== *///
*///
/**
* * 算诊数据 - 第五诊
* 基于传统中医算诊理论的数字化实现
export interface CalculationData {
}
};
  /** 算诊ID    ;
  id: string;
  /** 患者基本信息
  patientInfo: {
    /** 出生时间（用于八字计算）
    birthTime: MCPTimestamp;
    /** 性别
    gender: "male | "female;
    /** 出生地经纬度（用于真太阳时计算）
    birthLocation?: {
      latitude: number,
  longitude: number;,
  timezone: string;
    };
  };
  /** 子午流注分析
  ziwuLiuzhu: {
    /** 当前时辰
    currentHour: {,
  earthlyBranch: string; // 地支
meridian: string; // 对应经络,
  organ: string; // 对应脏腑
    }
    /** 开穴时间
    openingPoints: Array<{,
  time: string;
      point: string,
  meridian: string;,
  function: string;
    }>;
    /** 治疗建议时间
    optimalTreatmentTime: {,
  start: MCPTimestamp;
      end: MCPTimestamp,
  reason: string;
    };
    /** 调养建议
    recommendations: string[];
  };
  /** 八字体质分析
  constitutionAnalysis: {
    /** 四柱八字
    fourPillars: {,
  year: { heavenly: string; earthly: string };
      month: { heavenly: string; earthly: string };
      day: { heavenly: string; earthly: string };
      hour: { heavenly: string; earthly: string };
    };
    /** 五行分析
    fiveElements: {,
  wood: number;
      fire: number,
  earth: number;,
  metal: number,
  water: number;
    };
    /** 体质类型
    constitutionType: TCMConstitution;
    /** 五行强弱
    elementStrength: {,
  strongest: string;
      weakest: string,
  balance: number; // 0-1，1为最平衡
    }
    /** 调理建议
    adjustmentAdvice: {,
  strengthen: string[]; // 需要加强的方面
reduce: string[]; // 需要减少的方面,
  methods: string[]; // 调理方法
    }
  };
  /** 八卦配属分析
  baguaAnalysis: {
    /** 本命卦
    natalHexagram: {,
  name: string;
      symbol: string,
  element: string;,
  direction: string;
    };
    /** 健康分析
    healthAnalysis: {,
  strengths: string[]; // 健康优势
weaknesses: string[]; // 健康弱点,
  risks: string[]; // 潜在风险
    }
    /** 方位指导
    directionalGuidance: {,
  favorable: string[]; // 有利方位
unfavorable: string[]; // 不利方位,
  livingAdvice: string[]; // 居住建议
    }
  };
  /** 五运六气分析
  wuyunLiuqi: {
    /** 年度运气
    annualQi: {,
  year: number;
      mainQi: string; // 主气,
  guestQi: string; // 客气,
  hostHeaven: string; // 司天,
  hostEarth: string; // 在泉
    }
    /** 疾病预测
    diseasePrediction: {,
  susceptibleDiseases: string[]; // 易患疾病
preventionMethods: string[]; // 预防方法,
  criticalPeriods: Array<{ // 关键时期,
  period: string,
  risk: low" | "medium | "high";,
  description: string;
      }>;
    };
    /** 调养指导
    seasonalGuidance: {,
  spring: string[];
      summer: string[],
  autumn: string[];,
  winter: string[];
    };
  };
  /** 综合算诊结果
  comprehensiveResult: {
    /** 整体健康评分
    overallScore: number; // 0-100;
    /** 主要健康风险
    primaryRisks: Array<{,
  risk: string;
      severity: low" | "medium | "high",
  probability: number; // 0-1;,
  prevention: string[];
    }>;
    /** 个性化调养方案
    personalizedPlan: {,
  immediate: string[]; // 即时调养
shortTerm: string[]; // 短期调养（1-3个月）,
  longTerm: string[] // 长期调养（3个月以上）
    }
    /** 最佳调养时机
    optimalTimings: Array<{,
  activity: string;
      timing: string,
  reason: string;
    }>;
  };
  /** 算诊置信度
  confidence: {,
  overall: number; // 0-1;
ziwuLiuzhu: number,
  constitution: number;,
  bagua: number,
  wuyunLiuqi: number;
  };
  /** 算诊时间
  timestamp: MCPTimestamp;
  /** 算诊师信息
  practitioner?: {
    id: string,
  name: string;,
  qualification: string;
  }; */
} *///
*///
/**
* * 五诊数据聚合类型
export interface FiveDiagnosesData {
}
};
  /** 望诊数据    ;
  inspection: InspectionData[];
  /** 闻诊数据
  auscultation: AuscultationData[];
  /** 问诊数据
  inquiry: InquiryData[];
  /** 切诊数据
  palpation: PalpationData[];
  /** 算诊数据
  calculation: CalculationData[];
} */
  ==================== 智能体辨证结果类型 ==================== *///
*///
/**
* * 智能体辨证结果
export interface AgentDiagnosisResult {
}
}
  /** 辨证智能体ID;
  agentId: xiaoai" | "xiaoke | "laoke" | soer""
  /** 辨证结果
  diagnosis: {/** 主要证候    ,
  primarySyndrome: TCMSyndrome;
    /** 次要证候
    secondarySyndromes: TCMSyndrome[];
    /** 体质判断
    constitution: TCMConstitution;
    /** 脏腑状态
    organStates: TCMOrganState[];
  };
  /** 治疗建议
  treatment: {
    /** 治法
    principle: string;
    /** 方药建议
    prescription?: {
      name: string,
  herbs: Array<{,
  name: string,
  dosage: string;,
  function: string;
      }>;
    };
    /** 针灸建议
    acupuncture?: {
      points: string[],
  method: string;,
  frequency: string;
    };
    /** 生活调理
    lifestyle: {,
  diet: string[];
      exercise: string[],
  sleep: string[];,
  emotion: string[];
    };
  };
  /** 辨证置信度
  confidence: number; // 0-1;
  /** 辨证时间
  timestamp: MCPTimestamp;
  /** 数据来源 - 更新为五诊
  dataSource: {
    inspection?: InspectionData;
    auscultation?: AuscultationData;
    inquiry?: InquiryData;
    palpation?: PalpationData;
    calculation?: CalculationData; // 新增算诊数据源
biomarkers?: BiomarkerData[];
  };
} */
  ==================== 健康数据聚合类型 ==================== *///
*///
/**
* * 综合健康数据
export interface ComprehensiveHealthData {
}
};
  /** 用户ID    ;
  userId: string;
  /** 数据时间范围
  timeRange: TimeRange;
  /** 生物标志物数据
  biomarkers: BiomarkerData[];
  /** 五诊数据 - 更新为五诊
  fiveDiagnoses: FiveDiagnosesData;
  /** 智能体辨证结果
  agentDiagnoses: AgentDiagnosisResult[];
  /** 数据完整性评分
  completenessScore: number; // 0-1;
  /** 最后更新时间
  lastUpdated: MCPTimestamp;
}
// ==================== 导出类型 ====================
export type {
  MCPTimestamp,
  TimeRange,
  TCMConstitution,
  TCMSyndrome,
  TCMOrganState,
  BiomarkerData,
  InspectionData,
  AuscultationData,
  InquiryData,
  PalpationData,
  CalculationData, // 新增算诊类型导出
FiveDiagnosesData, // 新增五诊聚合类型导出 */
AgentDiagnosisResult, *///
  ComprehensiveHealthData *  ;
};  */