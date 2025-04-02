import mongoose, { Schema, Document } from 'mongoose';
import { 
  DiagnosisType, 
  YinYangBalance, 
  FiveElement, 
  ConstitutionType 
} from '../interfaces/four-diagnosis.interface';

/**
 * 单项诊断数据文档接口
 */
export interface IDiagnosisAnalysis extends Document {
  diagnosisType: DiagnosisType;
  timestamp: Date;
  findings: string[];
  overallAssessment: string;
  confidence: number;
  rawData?: any;
}

/**
 * 五行分析结果文档接口
 */
export interface IFiveElementsAnalysis extends Document {
  wood: number;
  fire: number;
  earth: number;
  metal: number;
  water: number;
  dominantElement: FiveElement;
  deficientElement: FiveElement;
}

/**
 * 阴阳平衡分析结果文档接口
 */
export interface IYinYangAnalysis extends Document {
  yin: number;
  yang: number;
  balance: YinYangBalance;
}

/**
 * 脏腑分析结果文档接口
 */
export interface IOrganAnalysis extends Document {
  heart: number;
  liver: number;
  spleen: number;
  lung: number;
  kidney: number;
  stomach: number;
  gallbladder: number;
  anomalies: string[];
}

/**
 * 身体状况分析结果文档接口
 */
export interface IBodyConditionAnalysis extends Document {
  yinYang: Schema.Types.ObjectId | IYinYangAnalysis;
  fiveElements: Schema.Types.ObjectId | IFiveElementsAnalysis;
  organs: Schema.Types.ObjectId | IOrganAnalysis;
  energyLevel: number;
  constitutionType: ConstitutionType | string;
}

/**
 * 四诊合参综合分析结果文档接口
 */
export interface IIntegratedAssessment extends Document {
  timestamp: Date;
  summary: string;
  bodyCondition: Schema.Types.ObjectId | IBodyConditionAnalysis;
  healthSuggestions: string[];
  diagnosticConfidence: number;
}

/**
 * 四诊合参数据文档接口
 */
export interface IFourDiagnosisData extends Document {
  patientId: string;
  diagnosisId: string;
  timestamp: Date;
  looking: Schema.Types.ObjectId | IDiagnosisAnalysis;
  smell: Schema.Types.ObjectId | IDiagnosisAnalysis;
  inquiry: Schema.Types.ObjectId | IDiagnosisAnalysis;
  touch: Schema.Types.ObjectId | IDiagnosisAnalysis;
  integratedAssessment: Schema.Types.ObjectId | IIntegratedAssessment;
  diagnosisNotes: string[];
  diagnosisWeights: {
    looking: number;
    smell: number;
    inquiry: number;
    touch: number;
  };
  version: number;
  validationStatus: string;
  diagnosisCount: number;
  isEligibleForIntegratedAnalysis(): boolean;
}

/**
 * 诊断数据集合Schema
 */
export interface IDiagnosisDocument extends Document {
  patientId: string;
  timestamp: Date;
  looking?: {
    data: any;
    timestamp: Date;
    overallAssessment: string;
  };
  smell?: {
    data: any;
    timestamp: Date;
    overallAssessment: string;
  };
  inquiry?: {
    data: any;
    timestamp: Date;
    overallAssessment: string;
  };
  touch?: {
    data: any;
    timestamp: Date;
    overallAssessment: string;
  };
  integrated: {
    timestamp: Date;
    summary: string;
    bodyCondition: {
      balance: {
        yinYang: {
          yinValue: number;
          yangValue: number;
          balance: YinYangBalance;
          description: string;
        };
        fiveElements: {
          wood: number;
          fire: number;
          earth: number;
          metal: number;
          water: number;
          dominantElement: FiveElement;
          deficientElement: FiveElement;
          imbalances: string[];
        };
        organs: {
          heart: number;
          liver: number;
          spleen: number;
          lung: number;
          kidney: number;
          stomach: number;
          gallbladder: number;
          anomalies: string[];
        };
      };
      energyLevel: number;
      constitutionType: ConstitutionType;
    };
    healthSuggestions: {
      category: string;
      content: string;
      priority: string;
      reasoningBasis: string;
    }[];
    diagnosticConfidence: number;
    usedDiagnostics: DiagnosisType[];
  };
  meta: {
    createdAt: Date;
    updatedAt: Date;
    version: number;
    source: string;
    integrationStatus: 'pending' | 'completed' | 'failed';
    validDiagnosticCount: number;       // 添加的诊断数量统计
    hasConflictingDiagnoses: boolean;   // 添加的冲突诊断标记
    diagnosisQualityScore: number;      // 添加的诊断质量评分
  };
  validDiagnosticCount: number;         // 虚拟属性
  isEligibleForIntegratedAnalysis: boolean; // 虚拟属性
  getDiagnosticTypes(): DiagnosisType[]; // 方法
}

// 诊断分析数据 Schema
const DiagnosisAnalysisSchema: Schema = new Schema({
  diagnosisType: {
    type: String,
    required: true,
    enum: Object.values(DiagnosisType)
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  findings: {
    type: [String],
    default: []
  },
  overallAssessment: {
    type: String,
    default: ''
  },
  confidence: {
    type: Number,
    default: 0
  },
  rawData: {
    type: Schema.Types.Mixed
  }
});

// 五行分析结果 Schema
const FiveElementsAnalysisSchema: Schema = new Schema({
  wood: {
    type: Number,
    default: 0
  },
  fire: {
    type: Number,
    default: 0
  },
  earth: {
    type: Number,
    default: 0
  },
  metal: {
    type: Number,
    default: 0
  },
  water: {
    type: Number,
    default: 0
  },
  dominantElement: {
    type: String,
    enum: Object.values(FiveElement),
    default: FiveElement.EARTH
  },
  deficientElement: {
    type: String,
    enum: Object.values(FiveElement),
    default: FiveElement.METAL
  }
});

// 阴阳平衡分析结果 Schema
const YinYangAnalysisSchema: Schema = new Schema({
  yin: {
    type: Number,
    default: 50
  },
  yang: {
    type: Number,
    default: 50
  },
  balance: {
    type: String,
    enum: Object.values(YinYangBalance),
    default: YinYangBalance.BALANCED
  }
});

// 脏腑分析结果 Schema
const OrganAnalysisSchema: Schema = new Schema({
  heart: {
    type: Number,
    default: 0
  },
  liver: {
    type: Number,
    default: 0
  },
  spleen: {
    type: Number,
    default: 0
  },
  lung: {
    type: Number,
    default: 0
  },
  kidney: {
    type: Number,
    default: 0
  },
  stomach: {
    type: Number,
    default: 0
  },
  gallbladder: {
    type: Number,
    default: 0
  },
  anomalies: {
    type: [String],
    default: []
  }
});

// 身体状况分析结果 Schema
const BodyConditionAnalysisSchema: Schema = new Schema({
  balance: {
    yinYang: YinYangAnalysisSchema,
    fiveElements: FiveElementsAnalysisSchema,
    organs: OrganAnalysisSchema
  },
  energyLevel: {
    type: Number,
    default: 50
  },
  constitutionType: {
    type: String,
    enum: Object.values(ConstitutionType),
    default: ConstitutionType.BALANCED
  }
});

// 四诊合参综合分析结果 Schema
const IntegratedAssessmentSchema: Schema = new Schema({
  timestamp: {
    type: Date,
    default: Date.now
  },
  summary: {
    type: String,
    required: true
  },
  bodyCondition: BodyConditionAnalysisSchema,
  healthSuggestions: {
    type: [String],
    default: []
  },
  diagnosticConfidence: {
    type: Number,
    default: 0
  }
});

// 四诊合参数据 Schema，添加验证
const FourDiagnosisDataSchema: Schema = new Schema({
  patientId: {
    type: String,
    required: [true, '患者ID不能为空'],
    index: true
  },
  diagnosisId: {
    type: String,
    required: [true, '诊断ID不能为空'],
    unique: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  looking: {
    type: Schema.Types.ObjectId,
    ref: 'DiagnosisAnalysis'
  },
  smell: {
    type: Schema.Types.ObjectId,
    ref: 'DiagnosisAnalysis'
  },
  inquiry: {
    type: Schema.Types.ObjectId,
    ref: 'DiagnosisAnalysis'
  },
  touch: {
    type: Schema.Types.ObjectId,
    ref: 'DiagnosisAnalysis'
  },
  integratedAssessment: {
    type: Schema.Types.ObjectId,
    ref: 'IntegratedAssessment'
  },
  diagnosisNotes: [String],
  diagnosisWeights: {
    looking: { type: Number, default: 0.25 },
    smell: { type: Number, default: 0.25 },
    inquiry: { type: Number, default: 0.25 },
    touch: { type: Number, default: 0.25 }
  },
  version: {
    type: Number,
    default: 1
  },
  validationStatus: {
    type: String,
    enum: ['pending', 'validated', 'invalid'],
    default: 'pending'
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// 添加索引
FourDiagnosisDataSchema.index({ patientId: 1, timestamp: -1 });
FourDiagnosisDataSchema.index({ diagnosisId: 1 }, { unique: true });

// 添加虚拟属性来计算有效诊断数量
FourDiagnosisDataSchema.virtual('diagnosisCount').get(function(this: any) {
  let count = 0;
  if (this.looking) count++;
  if (this.smell) count++;
  if (this.inquiry) count++;
  if (this.touch) count++;
  return count;
});

// 添加方法来检查数据是否足够做综合分析
FourDiagnosisDataSchema.methods.isEligibleForIntegratedAnalysis = function(this: any) {
  // 至少需要2种诊断数据才能进行四诊合参
  return this.diagnosisCount >= 2;
};

// 添加前置钩子进行数据验证
FourDiagnosisDataSchema.pre('save', function(this: any, next) {
  // 确保至少有一种诊断数据
  const hasDiagnosis = !!(this.looking || this.smell || this.inquiry || this.touch);
  
  if (!hasDiagnosis) {
    const error = new Error('四诊数据必须至少包含一种诊断数据');
    return next(error);
  }
  
  next();
});

// 创建模型
export const DiagnosisAnalysis = mongoose.model<IDiagnosisAnalysis>('DiagnosisAnalysis', DiagnosisAnalysisSchema);
export const FiveElementsAnalysis = mongoose.model<IFiveElementsAnalysis>('FiveElementsAnalysis', FiveElementsAnalysisSchema);
export const YinYangAnalysis = mongoose.model<IYinYangAnalysis>('YinYangAnalysis', YinYangAnalysisSchema);
export const OrganAnalysis = mongoose.model<IOrganAnalysis>('OrganAnalysis', OrganAnalysisSchema);
export const BodyConditionAnalysis = mongoose.model<IBodyConditionAnalysis>('BodyConditionAnalysis', BodyConditionAnalysisSchema);
export const IntegratedAssessment = mongoose.model<IIntegratedAssessment>('IntegratedAssessment', IntegratedAssessmentSchema);
export const FourDiagnosisData = mongoose.model<IFourDiagnosisData>('FourDiagnosisData', FourDiagnosisDataSchema);

// 定义Schema
const DiagnosisSchema: Schema = new Schema({
  patientId: {
    type: String,
    required: [true, '患者ID是必需的'],
    index: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  looking: {
    data: {
      type: Schema.Types.Mixed
    },
    timestamp: {
      type: Date
    },
    overallAssessment: {
      type: String
    }
  },
  smell: {
    data: {
      type: Schema.Types.Mixed
    },
    timestamp: {
      type: Date
    },
    overallAssessment: {
      type: String
    }
  },
  inquiry: {
    data: {
      type: Schema.Types.Mixed
    },
    timestamp: {
      type: Date
    },
    overallAssessment: {
      type: String
    }
  },
  touch: {
    data: {
      type: Schema.Types.Mixed
    },
    timestamp: {
      type: Date
    },
    overallAssessment: {
      type: String
    }
  },
  integrated: {
    timestamp: {
      type: Date
    },
    summary: {
      type: String
    },
    bodyCondition: {
      balance: {
        yinYang: {
          yinValue: {
            type: Number
          },
          yangValue: {
            type: Number
          },
          balance: {
            type: String,
            enum: Object.values(YinYangBalance)
          },
          description: {
            type: String
          }
        },
        fiveElements: {
          wood: {
            type: Number,
            min: 0,
            max: 100
          },
          fire: {
            type: Number,
            min: 0,
            max: 100
          },
          earth: {
            type: Number,
            min: 0,
            max: 100
          },
          metal: {
            type: Number,
            min: 0,
            max: 100
          },
          water: {
            type: Number,
            min: 0,
            max: 100
          },
          dominantElement: {
            type: String,
            enum: Object.values(FiveElement)
          },
          deficientElement: {
            type: String,
            enum: Object.values(FiveElement)
          },
          imbalances: [{
            type: String
          }]
        },
        organs: {
          heart: {
            type: Number,
            min: 0,
            max: 100
          },
          liver: {
            type: Number,
            min: 0,
            max: 100
          },
          spleen: {
            type: Number,
            min: 0,
            max: 100
          },
          lung: {
            type: Number,
            min: 0,
            max: 100
          },
          kidney: {
            type: Number,
            min: 0,
            max: 100
          },
          stomach: {
            type: Number,
            min: 0,
            max: 100
          },
          gallbladder: {
            type: Number,
            min: 0,
            max: 100
          },
          anomalies: [{
            type: String
          }]
        }
      },
      energyLevel: {
        type: Number,
        min: 0,
        max: 100
      },
      constitutionType: {
        type: String,
        enum: Object.values(ConstitutionType)
      }
    },
    healthSuggestions: [{
      category: {
        type: String
      },
      content: {
        type: String
      },
      priority: {
        type: String,
        enum: ['high', 'medium', 'low']
      },
      reasoningBasis: {
        type: String
      }
    }],
    diagnosticConfidence: {
      type: Number,
      min: 0,
      max: 100
    },
    usedDiagnostics: [{
      type: String,
      enum: Object.values(DiagnosisType)
    }]
  },
  meta: {
    createdAt: {
      type: Date,
      default: Date.now
    },
    updatedAt: {
      type: Date,
      default: Date.now
    },
    version: {
      type: Number,
      default: 1
    },
    source: {
      type: String,
      default: 'system'
    },
    integrationStatus: {
      type: String,
      enum: ['pending', 'completed', 'failed'],
      default: 'pending'
    },
    validDiagnosticCount: {
      type: Number,
      default: 0
    },
    hasConflictingDiagnoses: {
      type: Boolean,
      default: false
    },
    diagnosisQualityScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    }
  }
}, {
  timestamps: true
});

// 添加前置钩子，确保至少有一种诊断数据类型
DiagnosisSchema.pre('validate', function(next) {
  const diagnosis = this as IDiagnosisDocument;
  const hasDiagnosticData = diagnosis.looking || diagnosis.smell || 
                            diagnosis.inquiry || diagnosis.touch;
  
  if (!hasDiagnosticData) {
    return next(new Error('需要至少一种诊断数据类型'));
  }
  
  // 计算有效诊断数量
  let count = 0;
  if (diagnosis.looking && diagnosis.looking.data) count++;
  if (diagnosis.smell && diagnosis.smell.data) count++;
  if (diagnosis.inquiry && diagnosis.inquiry.data) count++;
  if (diagnosis.touch && diagnosis.touch.data) count++;
  
  diagnosis.meta.validDiagnosticCount = count;
  
  // 设置更新时间
  diagnosis.meta.updatedAt = new Date();
  
  next();
});

// 虚拟属性：获取有效诊断数量
DiagnosisSchema.virtual('validDiagnosticCount').get(function(this: IDiagnosisDocument) {
  return this.meta.validDiagnosticCount;
});

// 虚拟属性：是否符合综合分析条件
DiagnosisSchema.virtual('isEligibleForIntegratedAnalysis').get(function(this: IDiagnosisDocument) {
  // 至少需要一种诊断类型且状态不是失败
  return this.meta.validDiagnosticCount > 0 && this.meta.integrationStatus !== 'failed';
});

// 获取所有可用的诊断类型
DiagnosisSchema.methods.getDiagnosticTypes = function(this: IDiagnosisDocument): DiagnosisType[] {
  const types: DiagnosisType[] = [];
  
  if (this.looking && this.looking.data) types.push(DiagnosisType.LOOKING);
  if (this.smell && this.smell.data) types.push(DiagnosisType.SMELL);
  if (this.inquiry && this.inquiry.data) types.push(DiagnosisType.INQUIRY);
  if (this.touch && this.touch.data) types.push(DiagnosisType.TOUCH);
  
  return types;
};

// 计算诊断质量评分
DiagnosisSchema.methods.calculateQualityScore = function(this: IDiagnosisDocument): number {
  let score = 0;
  const diagnosticWeights = {
    [DiagnosisType.LOOKING]: 25,
    [DiagnosisType.SMELL]: 15,
    [DiagnosisType.INQUIRY]: 30,
    [DiagnosisType.TOUCH]: 30,
  };
  
  const types = this.getDiagnosticTypes();
  types.forEach(type => {
    score += diagnosticWeights[type] || 0;
  });
  
  // 如果有冲突的诊断，降低评分
  if (this.meta.hasConflictingDiagnoses) {
    score *= 0.8;
  }
  
  // 如果所有四诊都可用，给予额外加分
  if (types.length === 4) {
    score += 10;
  }
  
  // 确保最终分数在0-100之间
  return Math.min(100, Math.max(0, score));
};

// 检测诊断冲突
DiagnosisSchema.methods.detectConflicts = function(this: IDiagnosisDocument): {
  hasConflicts: boolean;
  conflicts: any[];
} {
  const conflicts = [];
  let hasConflicts = false;
  
  // 如果有多种诊断类型，检查它们之间是否存在潜在冲突
  const types = this.getDiagnosticTypes();
  if (types.length > 1) {
    // 实际项目中这里应该实现复杂的冲突检测逻辑
    // 例如，检查望诊和切诊的结果是否一致，等等
    
    // 简单示例：检查不同诊断类型的评估结论中的关键词是否冲突
    const hotTerms = ['火', '热', '阳盛', '燥'];
    const coldTerms = ['寒', '凉', '阴盛', '湿'];
    
    let hasHotSigns = false;
    let hasColdSigns = false;
    
    types.forEach(type => {
      const assessment = this[type]?.overallAssessment || '';
      
      // 检查是否包含热性关键词
      hotTerms.forEach(term => {
        if (assessment.includes(term)) {
          hasHotSigns = true;
        }
      });
      
      // 检查是否包含寒性关键词
      coldTerms.forEach(term => {
        if (assessment.includes(term)) {
          hasColdSigns = true;
        }
      });
    });
    
    // 如果同时存在寒性和热性特征，标记为冲突
    if (hasHotSigns && hasColdSigns) {
      hasConflicts = true;
      conflicts.push({
        type: '寒热冲突',
        description: '诊断中同时存在寒性和热性特征，可能需要进一步分析。'
      });
    }
  }
  
  return { hasConflicts, conflicts };
};

// 更新钩子，用于执行质量评分和冲突检测
DiagnosisSchema.pre('save', async function(next) {
  const diagnosis = this as IDiagnosisDocument;
  
  // 计算诊断质量评分
  diagnosis.meta.diagnosisQualityScore = diagnosis.calculateQualityScore();
  
  // 检测诊断冲突
  const { hasConflicts } = diagnosis.detectConflicts();
  diagnosis.meta.hasConflictingDiagnoses = hasConflicts;
  
  next();
});

// 创建并导出模型
export const Diagnosis = mongoose.model<IDiagnosisDocument>('Diagnosis', DiagnosisSchema); 