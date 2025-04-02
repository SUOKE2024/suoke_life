import mongoose, { Schema, Document } from 'mongoose';
import { SmellDiagnosisType, SmellType, TcmAspect } from '../../interfaces/smell-diagnosis.interface';

/**
 * 气味分析结果模式
 */
export interface SmellAnalysisResultDocument extends Document {
  userId: string;
  smellType: SmellType;
  intensity: number;
  description: string;
  relatedConditions: string[];
  confidence: number;
  rawData?: any;
  metadata?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

const SmellAnalysisResultSchema = new Schema({
  userId: { type: String, required: true, index: true },
  smellType: { 
    type: String, 
    required: true, 
    enum: Object.values(SmellType),
    default: SmellType.NORMAL 
  },
  intensity: { type: Number, required: true, min: 0, max: 10 },
  description: { type: String, required: true },
  relatedConditions: { type: [String], default: [] },
  confidence: { type: Number, required: true, min: 0, max: 1 },
  rawData: { type: Schema.Types.Mixed },
  metadata: { type: Schema.Types.Mixed }
}, { timestamps: true });

/**
 * 中医理论意义模式
 */
const TcmImplicationSchema = new Schema({
  aspect: { 
    type: String, 
    required: true, 
    enum: Object.values(TcmAspect) 
  },
  description: { type: String, required: true },
  significance: { type: Number, required: true, min: 0, max: 10 }
}, { _id: false });

/**
 * 闻诊分析结果模式
 */
export interface SmellDiagnosisResultDocument extends Document {
  userId: string;
  requestId: string;
  diagnosisType: SmellDiagnosisType;
  analysisResults: Schema.Types.ObjectId[] | SmellAnalysisResultDocument[];
  tcmImplications: {
    aspect: TcmAspect;
    description: string;
    significance: number;
  }[];
  recommendations: string[];
  confidence: number;
  metadata?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

const SmellDiagnosisResultSchema = new Schema({
  userId: { type: String, required: true, index: true },
  requestId: { type: String, required: true, unique: true },
  diagnosisType: { 
    type: String, 
    required: true, 
    enum: Object.values(SmellDiagnosisType),
    default: SmellDiagnosisType.BREATH
  },
  analysisResults: [{ type: Schema.Types.ObjectId, ref: 'SmellAnalysisResult' }],
  tcmImplications: [TcmImplicationSchema],
  recommendations: [String],
  confidence: { type: Number, required: true, min: 0, max: 1 },
  metadata: { type: Schema.Types.Mixed }
}, { timestamps: true });

// 创建索引
SmellDiagnosisResultSchema.index({ createdAt: 1 });
SmellDiagnosisResultSchema.index({ userId: 1, createdAt: -1 });
SmellDiagnosisResultSchema.index({ diagnosisType: 1, userId: 1 });

// 创建模型
export const SmellAnalysisResultModel = mongoose.model<SmellAnalysisResultDocument>(
  'SmellAnalysisResult', SmellAnalysisResultSchema
);

export const SmellDiagnosisResultModel = mongoose.model<SmellDiagnosisResultDocument>(
  'SmellDiagnosisResult', SmellDiagnosisResultSchema
);