import mongoose, { Document, Schema } from 'mongoose';
import { InquirySession, InquiryExchange, ExtractedSymptom, InquiryDiagnosis } from '../../models/inquiry.model';

/**
 * 问诊会话文档接口
 * 扩展MongoDB文档类型
 */
export interface InquirySessionDocument extends Document, Omit<InquirySession, 'id'> {
  // Document已经包含了_id
}

/**
 * 症状提取Schema
 */
const ExtractedSymptomSchema = new Schema({
  name: { type: String, required: true },
  location: { type: String },
  severity: { type: Number, min: 1, max: 10 },
  duration: { type: String },
  frequency: { type: String },
  characteristics: [String],
  aggravatingFactors: [String],
  relievingFactors: [String],
  associatedSymptoms: [String],
  confidence: { type: Number, min: 0, max: 1 }
}, { _id: false });

/**
 * 问诊交互Schema
 */
const InquiryExchangeSchema = new Schema({
  exchangeId: { type: String, required: true },
  timestamp: { type: Date, default: Date.now },
  question: { type: String, required: true },
  answer: { type: String, required: true },
  extractedSymptoms: [ExtractedSymptomSchema],
  intentType: { type: String },
  confidence: { type: Number, min: 0, max: 1 }
}, { _id: false });

/**
 * 诊断结果Schema
 */
const InquiryDiagnosisSchema = new Schema({
  diagnosisId: { type: String, required: true },
  timestamp: { type: Date, default: Date.now },
  tcmPatterns: [{
    pattern: { type: String, required: true },
    confidence: { type: Number, required: true, min: 0, max: 1 },
    relatedSymptoms: [String]
  }],
  mainSymptoms: [String],
  secondarySymptoms: [String],
  constitution: {
    primary: { type: String, required: true },
    secondary: [String],
    deviationLevel: { type: Number, min: 1, max: 5 }
  },
  recommendations: {
    diet: [String],
    lifestyle: [String],
    remedies: [String],
    others: [String]
  },
  precautions: [String],
  followUpQuestions: [String]
}, { _id: false });

/**
 * 问诊会话Schema
 */
const InquirySessionSchema = new Schema({
  sessionId: { type: String, required: true, unique: true },
  userId: { type: String, required: true, index: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now },
  status: { 
    type: String, 
    enum: ['active', 'completed', 'abandoned'], 
    default: 'active' 
  },
  patientInfo: {
    name: { type: String },
    age: { type: Number, min: 0, max: 150 },
    gender: { type: String, enum: ['男', '女', '其他'] },
    height: { type: Number, min: 0, max: 300 },
    weight: { type: Number, min: 0, max: 500 }
  },
  preferences: {
    useTCMTerminology: { type: Boolean, default: true },
    detailLevel: { type: Number, min: 1, max: 5, default: 3 },
    language: { type: String, default: 'zh_CN' }
  },
  exchanges: [InquiryExchangeSchema],
  diagnosis: InquiryDiagnosisSchema,
  metadata: { type: Schema.Types.Mixed }
}, {
  timestamps: true, // 自动添加createdAt和updatedAt字段
  versionKey: false // 禁用版本字段
});

// 添加索引
InquirySessionSchema.index({ 'sessionId': 1 });
InquirySessionSchema.index({ 'userId': 1, 'createdAt': -1 });
InquirySessionSchema.index({ 'status': 1 });

/**
 * 预处理钩子 - 在保存前更新updatedAt字段
 */
InquirySessionSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

/**
 * 模型方法 - 转换为API响应格式
 */
InquirySessionSchema.methods.toResponse = function(): InquirySession {
  const doc = this.toObject();
  return {
    id: doc.sessionId,
    userId: doc.userId,
    createdAt: doc.createdAt.toISOString(),
    updatedAt: doc.updatedAt.toISOString(),
    status: doc.status,
    patientInfo: doc.patientInfo,
    preferences: doc.preferences,
    exchanges: doc.exchanges,
    diagnosis: doc.diagnosis,
    metadata: doc.metadata
  };
};

// 创建并导出模型
export const InquirySessionModel = mongoose.model<InquirySessionDocument>('InquirySession', InquirySessionSchema);