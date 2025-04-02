import mongoose, { Document, Schema } from 'mongoose';
import { DiagnosisResult, TCMPattern, ConstitutionAnalysis, HealthRecommendation } from '../../models/diagnosis.model';

/**
 * 诊断结果文档接口
 */
export interface DiagnosisResultDocument extends Document, Omit<DiagnosisResult, 'diagnosisId'> {
  // Document已经包含了_id
}

/**
 * TCM证型模式
 */
const TCMPatternSchema = new Schema({
  name: { type: String, required: true },
  confidence: { type: Number, required: true, min: 0, max: 1 },
  description: { type: String },
  relatedSymptoms: [String]
}, { _id: false });

/**
 * 症状分类模式
 */
const CategorizedSymptomSchema = new Schema({
  name: { type: String, required: true },
  category: { 
    type: String, 
    enum: ['主症', '次症', '兼症', '既往症'],
    required: true 
  },
  severity: { type: Number, min: 1, max: 10 },
  duration: { type: String },
  description: { type: String }
}, { _id: false });

/**
 * 体质分析模式
 */
const ConstitutionAnalysisSchema = new Schema({
  primaryType: { 
    type: String, 
    enum: ['平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质'],
    required: true 
  },
  secondaryTypes: [{
    type: String,
    enum: ['平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质']
  }],
  description: { type: String },
  deviationLevel: { type: Number, min: 1, max: 10 },
  scoreDetails: { type: Map, of: Number }
}, { _id: false });

/**
 * 健康建议模式
 */
const HealthRecommendationSchema = new Schema({
  type: { 
    type: String,
    enum: ['饮食调理', '生活方式', '运动建议', '中药食材', '针灸穴位', '推拿按摩', '气功冥想', '预防保健', '其他建议'],
    required: true 
  },
  content: { type: String, required: true },
  reason: { type: String },
  priority: { type: Number, min: 1, max: 5 },
  implementationPeriod: { type: String },
  expectedOutcome: { type: String }
}, { _id: false });

/**
 * 预警指标模式
 */
const WarningIndicatorSchema = new Schema({
  level: { 
    type: String, 
    enum: ['low', 'medium', 'high'],
    required: true 
  },
  content: { type: String, required: true },
  suggestedAction: { type: String, required: true }
}, { _id: false });

/**
 * 诊断结果模式
 */
const DiagnosisResultSchema = new Schema({
  diagnosisId: { type: String, required: true, unique: true },
  sessionId: { type: String, required: true, index: true },
  userId: { type: String, required: true, index: true },
  timestamp: { type: Date, default: Date.now },
  tcmPatterns: [TCMPatternSchema],
  categorizedSymptoms: [CategorizedSymptomSchema],
  constitutionAnalysis: { type: ConstitutionAnalysisSchema, required: true },
  recommendations: [HealthRecommendationSchema],
  summary: { type: String, required: true },
  followUpQuestions: [String],
  warningIndicators: [WarningIndicatorSchema],
  confidence: { type: Number, required: true, min: 0, max: 1 },
  metadata: { type: Schema.Types.Mixed }
}, {
  timestamps: true,
  versionKey: false
});

// 添加索引
DiagnosisResultSchema.index({ 'diagnosisId': 1 });
DiagnosisResultSchema.index({ 'userId': 1, 'timestamp': -1 });
DiagnosisResultSchema.index({ 'sessionId': 1 });
DiagnosisResultSchema.index({ 'constitutionAnalysis.primaryType': 1 });

/**
 * 模型方法 - 转换为API响应格式
 */
DiagnosisResultSchema.methods.toResponse = function(): DiagnosisResult {
  const doc = this.toObject();
  
  // 转换时间格式
  doc.timestamp = doc.timestamp.toISOString();
  
  // 删除MongoDB特定字段
  delete doc._id;
  delete doc.__v;
  delete doc.createdAt;
  delete doc.updatedAt;
  
  return doc as DiagnosisResult;
};

// 创建并导出模型
export const DiagnosisResultModel = mongoose.model<DiagnosisResultDocument>('DiagnosisResult', DiagnosisResultSchema);