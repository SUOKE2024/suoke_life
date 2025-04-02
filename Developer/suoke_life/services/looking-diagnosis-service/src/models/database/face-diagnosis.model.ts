import mongoose, { Schema, Document } from 'mongoose';
import { FaceDiagnosisResult, FaceFeatures } from '../../services/face-analysis/face-analysis.service';

/**
 * 面诊数据库文档接口
 * 扩展FaceDiagnosisResult并添加MongoDB文档特性
 */
export interface FaceDiagnosisDocument extends FaceDiagnosisResult, Document {
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

// 面色区域评分模式
const FaceRegionsSchema = new Schema({
  forehead: { type: Number, required: true },
  nose: { type: Number, required: true },
  leftCheek: { type: Number, required: true },
  rightCheek: { type: Number, required: true },
  mouth: { type: Number, required: true },
  chin: { type: Number, required: true }
}, { _id: false });

// 面色特征模式
const FaceFeaturesSchema = new Schema<FaceFeatures>({
  faceColor: { type: String, required: true },
  luster: { type: String, required: true },
  moisture: { type: String, required: true },
  regions: { type: FaceRegionsSchema, required: true }
}, { _id: false });

// 中医辨证结果模式
const TCMImplicationSchema = new Schema({
  concept: { type: String, required: true },
  confidence: { type: Number, required: true }
}, { _id: false });

// 面诊结果数据库模式
const FaceDiagnosisSchema = new Schema<FaceDiagnosisDocument>({
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
    type: FaceFeaturesSchema, 
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
  collection: 'face_diagnoses' // 指定集合名称
});

// 创建并导出模型
export const FaceDiagnosisModel = mongoose.model<FaceDiagnosisDocument>(
  'FaceDiagnosis', 
  FaceDiagnosisSchema
); 