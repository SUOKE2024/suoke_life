import mongoose, { Document, Schema } from 'mongoose';

/**
 * 健康科普教育内容模型接口
 */
export interface IHealthEducation extends Document {
  title: string;
  description: string;
  content: string;
  targetAudience: 'general' | 'children' | 'teenagers' | 'adults' | 'elderly' | 'pregnant' | 'chronic_patients' | 'healthcare_workers';
  educationalLevel: 'beginner' | 'intermediate' | 'advanced' | 'professional';
  format: 'article' | 'infographic' | 'video' | 'quiz' | 'interactive' | 'presentation' | 'guide';
  mediaResources: Array<{
    type: 'image' | 'video' | 'audio' | 'document' | 'link';
    url: string;
    description: string;
    thumbnail?: string;
  }>;
  learningObjectives: string[];
  keyTakeaways: string[];
  simplifiedExplanations: Array<{
    concept: string;
    simplifiedDescription: string;
    analogies: string[];
    visualRepresentation?: string;
  }>;
  interactiveElements: Array<{
    type: 'quiz' | 'assessment' | 'calculator' | 'decision_tree' | 'simulation';
    content: any;
    purpose: string;
  }>;
  citations: Array<{
    text: string;
    source: string;
    url?: string;
  }>;
  relatedContent: mongoose.Types.ObjectId[];
  categories: mongoose.Types.ObjectId[];
  tags: mongoose.Types.ObjectId[];
  complexity: 1 | 2 | 3 | 4 | 5;
  readingTime: number;
  createdAt: Date;
  updatedAt: Date;
  reviewStatus: 'reviewed' | 'pending_review';
  localization: Array<{
    language: string;
    title: string;
    content: string;
    description: string;
  }>;
}

const mediaResourceSchema = new Schema({
  type: { 
    type: String, 
    enum: ['image', 'video', 'audio', 'document', 'link'],
    required: true 
  },
  url: { type: String, required: true },
  description: { type: String, required: true },
  thumbnail: { type: String }
});

const simplifiedExplanationSchema = new Schema({
  concept: { type: String, required: true },
  simplifiedDescription: { type: String, required: true },
  analogies: [{ type: String }],
  visualRepresentation: { type: String }
});

const interactiveElementSchema = new Schema({
  type: { 
    type: String, 
    enum: ['quiz', 'assessment', 'calculator', 'decision_tree', 'simulation'],
    required: true 
  },
  content: { type: Schema.Types.Mixed, required: true },
  purpose: { type: String, required: true }
});

const citationSchema = new Schema({
  text: { type: String, required: true },
  source: { type: String, required: true },
  url: { type: String }
});

const localizationSchema = new Schema({
  language: { type: String, required: true },
  title: { type: String, required: true },
  content: { type: String, required: true },
  description: { type: String, required: true }
});

const healthEducationSchema = new Schema({
  title: { type: String, required: true, index: true },
  description: { type: String, required: true },
  content: { type: String, required: true },
  targetAudience: { 
    type: String, 
    enum: ['general', 'children', 'teenagers', 'adults', 'elderly', 'pregnant', 'chronic_patients', 'healthcare_workers'],
    required: true 
  },
  educationalLevel: { 
    type: String, 
    enum: ['beginner', 'intermediate', 'advanced', 'professional'],
    required: true 
  },
  format: { 
    type: String, 
    enum: ['article', 'infographic', 'video', 'quiz', 'interactive', 'presentation', 'guide'],
    required: true 
  },
  mediaResources: [mediaResourceSchema],
  learningObjectives: [{ type: String, required: true }],
  keyTakeaways: [{ type: String, required: true }],
  simplifiedExplanations: [simplifiedExplanationSchema],
  interactiveElements: [interactiveElementSchema],
  citations: [citationSchema],
  relatedContent: [{ type: Schema.Types.ObjectId, ref: 'HealthEducation' }],
  categories: [{ type: Schema.Types.ObjectId, ref: 'Category' }],
  tags: [{ type: Schema.Types.ObjectId, ref: 'Tag' }],
  complexity: { 
    type: Number, 
    required: true,
    min: 1,
    max: 5
  },
  readingTime: { type: Number, required: true }, // In minutes
  reviewStatus: { 
    type: String, 
    enum: ['reviewed', 'pending_review'],
    default: 'pending_review'
  },
  localization: [localizationSchema],
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// 添加文本索引以支持全文搜索
healthEducationSchema.index({
  title: 'text',
  description: 'text',
  content: 'text',
  'simplifiedExplanations.concept': 'text',
  'simplifiedExplanations.simplifiedDescription': 'text',
  'keyTakeaways': 'text'
});

// 添加索引以支持按目标受众和教育级别查询
healthEducationSchema.index({ targetAudience: 1, educationalLevel: 1, format: 1 });
healthEducationSchema.index({ complexity: 1 });

// 更新时自动更新updatedAt字段
healthEducationSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

export default mongoose.model<IHealthEducation>('HealthEducation', healthEducationSchema);