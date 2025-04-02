import mongoose, { Schema, Document } from 'mongoose';
import { v4 as uuidv4 } from 'uuid';
import { 
  PulseType, 
  AbdominalFindingType, 
  TouchLocation,
  PulsePosition, 
  PulseDepth, 
  PulseCharacteristic, 
  PulseStrength,
  AbdominalRegion,
  AbdominalStatus
} from '../interfaces/touch-diagnosis.interface';

/**
 * 脉诊数据文档接口
 */
export interface IPulseDiagnosisData extends Document {
  location: TouchLocation;
  pulseType: PulseType;
  strength: number;
  rhythm: number;
  frequency: number;
  description?: string;
  timestamp: Date;
}

/**
 * 腹诊数据文档接口
 */
export interface IAbdominalDiagnosisData extends Document {
  location: TouchLocation;
  findingType: AbdominalFindingType;
  intensity: number;
  description?: string;
  timestamp: Date;
}

/**
 * 触诊分析文档接口
 */
export interface ITouchDiagnosisAnalysis extends Document {
  patientId: string;
  diagnosisId: string;
  pulseFindings: Schema.Types.ObjectId[] | IPulseDiagnosisData[];
  abdominalFindings: Schema.Types.ObjectId[] | IAbdominalDiagnosisData[];
  overallAssessment: string;
  diagnosisTime: Date;
  practitionerId: string;
  confidence: number;
  healthSuggestions: string[];
}

// 脉诊数据结构
export interface IPulseDiagnosis {
  position: PulsePosition;
  depth: PulseDepth;
  characteristics: PulseCharacteristic[];
  strength: PulseStrength;
  notes?: string;
}

// 腹诊数据结构
export interface IAbdominalDiagnosis {
  region: AbdominalRegion;
  status: AbdominalStatus[];
  tenderness?: boolean;
  temperature?: 'cold' | 'warm' | 'hot' | 'normal';
  tension?: 'tight' | 'loose' | 'normal';
  notes?: string;
}

// 触诊记录数据结构
export interface ITouchDiagnosis extends Document {
  _id: string;
  patientId: string;
  practitionerId: string;
  date: Date;
  pulseData?: IPulseDiagnosis[];
  abdominalData?: IAbdominalDiagnosis[];
  analysisResults?: {
    constitutionTypes: string[];
    healthImbalances: string[];
    recommendations: string[];
    severity: 'mild' | 'moderate' | 'severe';
    confidence: number;
  };
  createdAt: Date;
  updatedAt: Date;
}

// 脉诊数据Schema
const PulseDiagnosisDataSchema: Schema = new Schema({
  location: {
    type: String,
    required: true,
    enum: Object.values(TouchLocation)
  },
  pulseType: {
    type: String,
    required: true,
    enum: Object.values(PulseType)
  },
  strength: {
    type: Number,
    required: true,
    min: 0,
    max: 1
  },
  rhythm: {
    type: Number,
    required: true,
    min: 0,
    max: 1
  },
  frequency: {
    type: Number,
    required: true
  },
  description: {
    type: String
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

// 腹诊数据Schema
const AbdominalDiagnosisDataSchema: Schema = new Schema({
  location: {
    type: String,
    required: true,
    enum: Object.values(TouchLocation)
  },
  findingType: {
    type: String,
    required: true,
    enum: Object.values(AbdominalFindingType)
  },
  intensity: {
    type: Number,
    required: true,
    min: 0,
    max: 1
  },
  description: {
    type: String
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

// 脉诊数据Schema
const PulseDiagnosisSchema = new Schema<IPulseDiagnosis>({
  position: {
    type: String,
    required: true,
    enum: Object.values(PulsePosition)
  },
  depth: {
    type: String,
    required: true,
    enum: Object.values(PulseDepth)
  },
  characteristics: [{
    type: String,
    required: true,
    enum: Object.values(PulseCharacteristic)
  }],
  strength: {
    type: String,
    required: true,
    enum: Object.values(PulseStrength)
  },
  notes: {
    type: String
  }
}, { _id: false });

// 腹诊数据Schema
const AbdominalDiagnosisSchema = new Schema<IAbdominalDiagnosis>({
  region: {
    type: String,
    required: true,
    enum: Object.values(AbdominalRegion)
  },
  status: [{
    type: String,
    required: true,
    enum: Object.values(AbdominalStatus)
  }],
  tenderness: {
    type: Boolean,
    default: false
  },
  temperature: {
    type: String,
    enum: ['cold', 'warm', 'hot', 'normal'],
    default: 'normal'
  },
  tension: {
    type: String,
    enum: ['tight', 'loose', 'normal'],
    default: 'normal'
  },
  notes: {
    type: String
  }
}, { _id: false });

// 触诊分析Schema
const TouchDiagnosisAnalysisSchema: Schema = new Schema({
  patientId: {
    type: String,
    required: true,
    index: true
  },
  diagnosisId: {
    type: String,
    required: true,
    unique: true
  },
  pulseFindings: [{
    type: Schema.Types.ObjectId,
    ref: 'PulseDiagnosisData'
  }],
  abdominalFindings: [{
    type: Schema.Types.ObjectId,
    ref: 'AbdominalDiagnosisData'
  }],
  overallAssessment: {
    type: String,
    required: true
  },
  diagnosisTime: {
    type: Date,
    default: Date.now
  },
  practitionerId: {
    type: String,
    required: true
  },
  confidence: {
    type: Number,
    default: 0,
    min: 0,
    max: 100
  },
  healthSuggestions: {
    type: [String],
    default: []
  }
}, {
  timestamps: true
});

// 创建索引
TouchDiagnosisAnalysisSchema.index({ patientId: 1, diagnosisTime: -1 });

// 触诊记录Schema
const TouchDiagnosisSchema = new Schema<ITouchDiagnosis>({
  _id: {
    type: String,
    default: () => uuidv4()
  },
  patientId: {
    type: String,
    required: true,
    index: true
  },
  practitionerId: {
    type: String,
    required: true
  },
  date: {
    type: Date,
    default: Date.now
  },
  pulseData: [PulseDiagnosisSchema],
  abdominalData: [AbdominalDiagnosisSchema],
  analysisResults: {
    constitutionTypes: [String],
    healthImbalances: [String],
    recommendations: [String],
    severity: {
      type: String,
      enum: ['mild', 'moderate', 'severe']
    },
    confidence: {
      type: Number,
      min: 0,
      max: 1
    }
  }
}, {
  timestamps: true,
  versionKey: false
});

// 索引优化
TouchDiagnosisSchema.index({ patientId: 1, date: -1 });
TouchDiagnosisSchema.index({ createdAt: -1 });

// 创建模型
export const PulseDiagnosisData = mongoose.model<IPulseDiagnosisData>('PulseDiagnosisData', PulseDiagnosisDataSchema);
export const AbdominalDiagnosisData = mongoose.model<IAbdominalDiagnosisData>('AbdominalDiagnosisData', AbdominalDiagnosisDataSchema);
export const TouchDiagnosisAnalysis = mongoose.model<ITouchDiagnosisAnalysis>('TouchDiagnosisAnalysis', TouchDiagnosisAnalysisSchema);
export const TouchDiagnosisModel = mongoose.model<ITouchDiagnosis>('TouchDiagnosis', TouchDiagnosisSchema); 