/**
 * 传统文化知识模型
 */
import mongoose, { Document, Schema } from 'mongoose';
import { KnowledgeEntry } from './knowledge-entry.model';

// 文化体系枚举
export enum CulturalSystem {
  YIJING = 'yijing',
  TAOISM = 'taoism',
  BUDDHISM = 'buddhism',
  PHYSIOGNOMY = 'physiognomy',
  FENGSHUI = 'fengshui',
  CLASSICS = 'classics',
  OTHER = 'other'
}

// 传统文化知识接口
export interface TraditionalCultureKnowledge extends KnowledgeEntry {
  culturalSystem: CulturalSystem;
  historicalPeriod?: string;
  originalText?: string;
  interpretation?: string;
}

// 传统文化知识文档接口
export interface TraditionalCultureKnowledgeDocument extends TraditionalCultureKnowledge, Document {}

// 传统文化知识模式
const traditionalCultureKnowledgeSchema = new Schema<TraditionalCultureKnowledgeDocument>(
  {
    title: { type: String, required: true, index: true },
    content: { type: String, required: true },
    summary: { type: String },
    categories: [{ type: Schema.Types.ObjectId, ref: 'Category', required: true }],
    tags: [{ type: Schema.Types.ObjectId, ref: 'Tag' }],
    culturalSystem: { 
      type: String, 
      required: true, 
      enum: Object.values(CulturalSystem),
      index: true
    },
    historicalPeriod: { type: String, index: true },
    originalText: { type: String },
    interpretation: { type: String },
    vectorized: { type: Boolean, default: false },
    source: { type: String },
    attributes: { type: Map, of: Schema.Types.Mixed },
    createdBy: { type: Schema.Types.ObjectId, ref: 'User' },
    updatedBy: { type: Schema.Types.ObjectId, ref: 'User' }
  },
  {
    timestamps: true,
    collection: 'traditional_culture_knowledge'
  }
);

// 创建全文搜索索引
traditionalCultureKnowledgeSchema.index(
  { title: 'text', content: 'text', summary: 'text', originalText: 'text', interpretation: 'text' },
  { 
    weights: {
      title: 10,
      summary: 5,
      content: 3,
      originalText: 2,
      interpretation: 1
    },
    name: 'traditional_culture_text_index'
  }
);

// 导出模型
export const TraditionalCultureKnowledgeModel = (mongoose.models.TraditionalCultureKnowledge as mongoose.Model<TraditionalCultureKnowledgeDocument>) || 
  mongoose.model<TraditionalCultureKnowledgeDocument>('TraditionalCultureKnowledge', traditionalCultureKnowledgeSchema);