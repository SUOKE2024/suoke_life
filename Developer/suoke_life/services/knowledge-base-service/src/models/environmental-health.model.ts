/**
 * 环境健康知识模型定义
 */
import mongoose, { Schema } from 'mongoose';
import { EnvironmentalHealthData } from '../interfaces/environmental-health.interface';

const MonitoringIndicatorSchema = new Schema({
  name: { type: String, required: true },
  unit: { type: String, required: true },
  safeRange: { type: String, required: true },
  description: { type: String, required: true }
}, { _id: false });

const ReferenceSchema = new Schema({
  author: { type: String, required: true },
  title: { type: String, required: true },
  source: { type: String, required: true },
  year: { type: Number, required: true },
  url: { type: String }
}, { _id: false });

const PolicySchema = new Schema({
  name: { type: String, required: true },
  issuer: { type: String, required: true },
  year: { type: Number, required: true },
  description: { type: String, required: true },
  url: { type: String }
}, { _id: false });

// 环境健康知识模式定义
const EnvironmentalHealthSchema = new Schema<EnvironmentalHealthData>({
  title: { 
    type: String, 
    required: true, 
    trim: true,
    index: true
  },
  description: { 
    type: String, 
    required: true 
  },
  content: { 
    type: String, 
    required: true 
  },
  environmentType: { 
    type: String, 
    required: true,
    index: true
  },
  pollutantType: { 
    type: [String], 
    default: [],
    index: true
  },
  healthImpacts: { 
    type: [String], 
    default: [] 
  },
  riskLevel: { 
    type: Number, 
    required: true,
    min: 1,
    max: 5,
    index: true
  },
  vulnerableGroups: { 
    type: [String], 
    default: [] 
  },
  protectiveMeasures: { 
    type: [String], 
    default: [] 
  },
  preventiveAdvice: { 
    type: [String], 
    default: [] 
  },
  relatedDiseases: { 
    type: [String], 
    default: [] 
  },
  regionSpecific: { 
    type: [String], 
    default: [],
    index: true
  },
  seasonalEffects: { 
    type: [String], 
    default: [] 
  },
  monitoringIndicators: { 
    type: [MonitoringIndicatorSchema], 
    default: [] 
  },
  keywords: { 
    type: [String], 
    default: [],
    index: true
  },
  references: { 
    type: [ReferenceSchema], 
    default: [] 
  },
  relatedPolicies: {
    type: [PolicySchema],
    default: []
  },
  relatedKnowledge: [{ 
    type: Schema.Types.ObjectId, 
    ref: 'Knowledge' 
  }],
  tags: [{ 
    type: Schema.Types.ObjectId, 
    ref: 'Tag' 
  }],
  categories: [{ 
    type: Schema.Types.ObjectId, 
    ref: 'Category' 
  }],
  createdAt: { 
    type: Date, 
    default: Date.now,
    index: true
  },
  updatedAt: { 
    type: Date, 
    default: Date.now,
    index: true
  },
  createdBy: { 
    type: String 
  },
  version: { 
    type: Number, 
    default: 1,
    required: true
  }
}, { 
  timestamps: true,
  versionKey: false
});

// 创建全文搜索索引
EnvironmentalHealthSchema.index({ 
  title: 'text', 
  description: 'text', 
  content: 'text',
  keywords: 'text',
  healthImpacts: 'text',
  pollutantType: 'text'
});

// 在更新前更新版本号
EnvironmentalHealthSchema.pre('findOneAndUpdate', function(next) {
  // @ts-ignore - 更新版本号
  this.set({ version: this.version + 1 });
  next();
});

const EnvironmentalHealthModel = mongoose.model<EnvironmentalHealthData>(
  'EnvironmentalHealth', 
  EnvironmentalHealthSchema
);

export default EnvironmentalHealthModel;