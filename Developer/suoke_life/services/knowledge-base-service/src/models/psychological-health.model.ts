/**
 * 心理健康知识模型定义
 */
import mongoose, { Schema } from 'mongoose';
import { MentalHealthData } from '../interfaces/mental-health.interface';

const ResourceSchema = new Schema({
  type: { type: String, required: true },
  name: { type: String, required: true },
  description: { type: String, required: true },
  url: { type: String }
}, { _id: false });

const ReferenceSchema = new Schema({
  author: { type: String, required: true },
  title: { type: String, required: true },
  source: { type: String, required: true },
  year: { type: Number, required: true },
  url: { type: String }
}, { _id: false });

// 心理健康知识模式定义
const PsychologicalHealthSchema = new Schema<MentalHealthData>({
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
  issueType: { 
    type: String, 
    required: true,
    index: true
  },
  symptoms: { 
    type: [String], 
    default: [] 
  },
  possibleCauses: { 
    type: [String], 
    default: [] 
  },
  interventionMethods: { 
    type: [String], 
    default: [],
    index: true
  },
  treatmentMethods: { 
    type: [String], 
    default: [] 
  },
  selfHelpMeasures: { 
    type: [String], 
    default: [] 
  },
  targetAgeGroups: { 
    type: [String], 
    default: [],
    index: true
  },
  resources: { 
    type: [ResourceSchema], 
    default: [] 
  },
  applicableScenarios: { 
    type: [String], 
    default: [] 
  },
  expectedOutcomes: { 
    type: [String], 
    default: [] 
  },
  expertAdvice: { 
    type: String 
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
PsychologicalHealthSchema.index({ 
  title: 'text', 
  description: 'text', 
  content: 'text',
  keywords: 'text',
  symptoms: 'text',
  treatmentMethods: 'text'
});

// 在更新前更新版本号
PsychologicalHealthSchema.pre('findOneAndUpdate', function(next) {
  // @ts-ignore - 更新版本号
  this.set({ version: this.version + 1 });
  next();
});

const PsychologicalHealthModel = mongoose.model<MentalHealthData>(
  'PsychologicalHealth', 
  PsychologicalHealthSchema
);

export default PsychologicalHealthModel;