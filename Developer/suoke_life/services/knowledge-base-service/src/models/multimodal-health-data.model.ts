import mongoose, { Document, Schema } from 'mongoose';

/**
 * 多模态健康数据模型接口
 */
export interface IMultimodalHealthData extends Document {
  userId: mongoose.Types.ObjectId;
  dataType: 'image' | 'audio' | 'video' | 'text' | 'mixed';
  category: 'tongue_diagnosis' | 'skin_analysis' | 'voice_analysis' | 'gait_analysis' | 'facial_analysis' | 'other';
  collectionTime: Date;
  deviceInfo?: {
    deviceName: string;
    deviceModel: string;
    osVersion: string;
    appVersion: string;
  };
  metadata: {
    captureSettings?: Record<string, any>;
    environmentalFactors?: Record<string, any>;
    userState?: Record<string, any>;
    processingParameters?: Record<string, any>;
  };
  mediaData: {
    storageType: 'url' | 'base64' | 'file' | 'blob_reference';
    contentType: string;
    data: string;
    thumbnailUrl?: string;
    size?: number;
  };
  analysisResults: {
    processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
    processingTime?: number;
    features: Array<{
      name: string;
      value: any;
      confidence: number;
      unit?: string;
      normalRange?: {
        min: number;
        max: number;
      };
    }>;
    classifications: Array<{
      category: string;
      confidence: number;
      description: string;
    }>;
    conditions: Array<{
      name: string;
      probability: number;
      severityLevel?: 'mild' | 'moderate' | 'severe';
      relatedFeatures: string[];
    }>;
    textualSummary: string;
    recommendations: string[];
    aiModelInfo?: {
      modelName: string;
      modelVersion: string;
      parameters: Record<string, any>;
    };
  };
  healthCorrelations: Array<{
    metricName: string;
    correlationStrength: number;
    direction: 'positive' | 'negative';
    description: string;
    confidenceLevel: number;
  }>;
  tags: string[];
  isVerified: boolean;
  verifiedBy?: mongoose.Types.ObjectId;
  createdAt: Date;
  updatedAt: Date;
}

const deviceInfoSchema = new Schema({
  deviceName: { type: String },
  deviceModel: { type: String },
  osVersion: { type: String },
  appVersion: { type: String }
});

const metadataSchema = new Schema({
  captureSettings: { type: Map, of: Schema.Types.Mixed },
  environmentalFactors: { type: Map, of: Schema.Types.Mixed },
  userState: { type: Map, of: Schema.Types.Mixed },
  processingParameters: { type: Map, of: Schema.Types.Mixed }
});

const mediaDataSchema = new Schema({
  storageType: { 
    type: String, 
    enum: ['url', 'base64', 'file', 'blob_reference'],
    required: true 
  },
  contentType: { type: String, required: true },
  data: { type: String, required: true },
  thumbnailUrl: { type: String },
  size: { type: Number }
});

const featureSchema = new Schema({
  name: { type: String, required: true },
  value: { type: Schema.Types.Mixed, required: true },
  confidence: { type: Number, required: true, min: 0, max: 1 },
  unit: { type: String },
  normalRange: {
    min: { type: Number },
    max: { type: Number }
  }
});

const classificationSchema = new Schema({
  category: { type: String, required: true },
  confidence: { type: Number, required: true, min: 0, max: 1 },
  description: { type: String }
});

const conditionSchema = new Schema({
  name: { type: String, required: true },
  probability: { type: Number, required: true, min: 0, max: 1 },
  severityLevel: { 
    type: String, 
    enum: ['mild', 'moderate', 'severe'] 
  },
  relatedFeatures: [{ type: String }]
});

const aiModelInfoSchema = new Schema({
  modelName: { type: String, required: true },
  modelVersion: { type: String, required: true },
  parameters: { type: Map, of: Schema.Types.Mixed }
});

const analysisResultsSchema = new Schema({
  processingStatus: { 
    type: String, 
    enum: ['pending', 'processing', 'completed', 'failed'],
    required: true,
    default: 'pending'
  },
  processingTime: { type: Number },
  features: [featureSchema],
  classifications: [classificationSchema],
  conditions: [conditionSchema],
  textualSummary: { type: String },
  recommendations: [{ type: String }],
  aiModelInfo: aiModelInfoSchema
});

const healthCorrelationSchema = new Schema({
  metricName: { type: String, required: true },
  correlationStrength: { type: Number, required: true, min: -1, max: 1 },
  direction: { 
    type: String, 
    enum: ['positive', 'negative'],
    required: true 
  },
  description: { type: String, required: true },
  confidenceLevel: { type: Number, required: true, min: 0, max: 1 }
});

const multimodalHealthDataSchema = new Schema({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  dataType: { 
    type: String, 
    enum: ['image', 'audio', 'video', 'text', 'mixed'],
    required: true 
  },
  category: { 
    type: String, 
    enum: ['tongue_diagnosis', 'skin_analysis', 'voice_analysis', 'gait_analysis', 'facial_analysis', 'other'],
    required: true 
  },
  collectionTime: { type: Date, required: true },
  deviceInfo: deviceInfoSchema,
  metadata: metadataSchema,
  mediaData: mediaDataSchema,
  analysisResults: analysisResultsSchema,
  healthCorrelations: [healthCorrelationSchema],
  tags: [{ type: String }],
  isVerified: { type: Boolean, default: false },
  verifiedBy: { type: Schema.Types.ObjectId, ref: 'User' },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// 创建复合索引支持用户和数据类型的高效查询
multimodalHealthDataSchema.index({ userId: 1, dataType: 1, category: 1 });
// 创建时间范围索引以支持时间序列查询
multimodalHealthDataSchema.index({ userId: 1, collectionTime: 1 });
// 创建处理状态索引
multimodalHealthDataSchema.index({ 'analysisResults.processingStatus': 1 });

// 更新时自动更新updatedAt字段
multimodalHealthDataSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

export default mongoose.model<IMultimodalHealthData>('MultimodalHealthData', multimodalHealthDataSchema);