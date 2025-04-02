import mongoose, { Document, Schema } from 'mongoose';

/**
 * 精准医学知识模型接口
 */
export interface IPrecisionMedicine extends Document {
  title: string;
  description: string;
  content: string;
  geneticMarkers: Array<{
    name: string;
    description: string;
    associatedConditions: string[];
    researchSupport: 'high' | 'medium' | 'low' | 'preliminary';
  }>;
  personalizedRecommendations: {
    nutrition: string[];
    exercise: string[];
    lifestyle: string[];
    supplements: string[];
  };
  riskAssessment: {
    conditions: Array<{
      name: string;
      probability: number;
      preventionStrategies: string[];
    }>;
  };
  scientificReferences: Array<{
    title: string;
    authors: string[];
    journal: string;
    year: number;
    doi?: string;
    url?: string;
  }>;
  categories: mongoose.Types.ObjectId[];
  tags: mongoose.Types.ObjectId[];
  medicalSpecialty: string[];
  createdAt: Date;
  updatedAt: Date;
  isVerified: boolean;
  verificationLevel: 'expert' | 'research' | 'clinical' | 'preliminary';
  knowledgeType: string;
}

const geneticMarkerSchema = new Schema({
  name: { type: String, required: true },
  description: { type: String, required: true },
  associatedConditions: [{ type: String }],
  researchSupport: { 
    type: String, 
    enum: ['high', 'medium', 'low', 'preliminary'],
    required: true 
  }
});

const personalizedRecommendationsSchema = new Schema({
  nutrition: [{ type: String }],
  exercise: [{ type: String }],
  lifestyle: [{ type: String }],
  supplements: [{ type: String }]
});

const conditionSchema = new Schema({
  name: { type: String, required: true },
  probability: { type: Number, required: true, min: 0, max: 1 },
  preventionStrategies: [{ type: String }]
});

const riskAssessmentSchema = new Schema({
  conditions: [conditionSchema]
});

const scientificReferenceSchema = new Schema({
  title: { type: String, required: true },
  authors: [{ type: String, required: true }],
  journal: { type: String, required: true },
  year: { type: Number, required: true },
  doi: { type: String },
  url: { type: String }
});

const precisionMedicineSchema = new Schema({
  title: { type: String, required: true, index: true },
  description: { type: String, required: true },
  content: { type: String, required: true },
  geneticMarkers: [geneticMarkerSchema],
  personalizedRecommendations: personalizedRecommendationsSchema,
  riskAssessment: riskAssessmentSchema,
  scientificReferences: [scientificReferenceSchema],
  categories: [{ type: Schema.Types.ObjectId, ref: 'Category' }],
  tags: [{ type: Schema.Types.ObjectId, ref: 'Tag' }],
  medicalSpecialty: [{ type: String }],
  isVerified: { type: Boolean, default: false },
  verificationLevel: { 
    type: String, 
    enum: ['expert', 'research', 'clinical', 'preliminary'],
    default: 'preliminary'
  },
  knowledgeType: { type: String, default: 'precision-medicine' },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// 添加文本索引以支持全文搜索
precisionMedicineSchema.index({
  title: 'text',
  description: 'text',
  content: 'text',
  'geneticMarkers.name': 'text',
  'geneticMarkers.description': 'text',
  'riskAssessment.conditions.name': 'text'
});

// 更新时自动更新updatedAt字段
precisionMedicineSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

export default mongoose.model<IPrecisionMedicine>('PrecisionMedicine', precisionMedicineSchema);