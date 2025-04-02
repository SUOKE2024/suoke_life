import mongoose, { Schema, Document } from 'mongoose';
import { TongueDiagnosisResult, TongueFeatures } from '../diagnosis/tongue.model';

/**
 * 舌诊数据库文档接口
 * 扩展TongueDiagnosisResult并添加MongoDB文档特性
 */
export interface TongueDiagnosisDocument extends TongueDiagnosisResult, Document {
  /**
   * 创建时间
   */
  createdAt: Date;
  
  /**
   * 更新时间
   */
  updatedAt: Date;
  
  /**
   * 用户ID
   */
  userId?: string;
}

// 舌头特征模式
const TongueFeaturesSchema = new Schema<TongueFeatures>({
  tongueColor: { type: String, required: true },
  tongueShape: { type: String, required: true },
  tongueCoating: { type: String, required: true },
  moisture: { type: String, required: true },
  cracks: { type: Boolean, default: false },
  spots: { type: Boolean, default: false },
  teethMarks: { type: Boolean, default: false },
  deviation: { type: Boolean, default: false }
}, { _id: false });

// 中医辨证结果模式
const TCMImplicationSchema = new Schema({
  concept: { type: String, required: true },
  confidence: { type: Number, required: true }
}, { _id: false });

// 舌诊结果数据库模式
const TongueDiagnosisSchema = new Schema<TongueDiagnosisDocument>({
  diagnosisId: { 
    type: String, 
    required: true, 
    unique: true,
    index: true 
  },
  sessionId: { 
    type: String, 
    required: true,
    index: true 
  },
  userId: { 
    type: String,
    index: true 
  },
  timestamp: { 
    type: String, 
    required: true 
  },
  features: { 
    type: TongueFeaturesSchema, 
    required: true 
  },
  tcmImplications: [TCMImplicationSchema],
  recommendations: [String],
  metadata: {
    type: Schema.Types.Mixed,
    default: {}
  }
}, {
  timestamps: true, // 自动添加createdAt和updatedAt字段
  collection: 'tongue_diagnoses' // 指定集合名称
});

// 创建并导出模型
export const TongueDiagnosisModel = mongoose.model<TongueDiagnosisDocument>(
  'TongueDiagnosis', 
  TongueDiagnosisSchema
); 