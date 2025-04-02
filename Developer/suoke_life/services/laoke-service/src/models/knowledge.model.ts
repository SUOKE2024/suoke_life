import mongoose, { Document, Schema } from 'mongoose';

/**
 * 知识内容接口
 */
export interface IKnowledge extends Document {
  title: string;
  summary: string;
  content: string;
  category: mongoose.Types.ObjectId;
  tags: string[];
  mediaUrls: string[];
  viewCount: number;
  createdBy: string;
  collaborators: string[];
  featured: boolean;
  published: boolean;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 知识内容模式
 */
const KnowledgeSchema = new Schema<IKnowledge>({
  title: {
    type: String,
    required: true,
    trim: true
  },
  summary: {
    type: String,
    required: true,
    trim: true
  },
  content: {
    type: String,
    required: true
  },
  category: {
    type: Schema.Types.ObjectId,
    ref: 'KnowledgeCategory',
    required: true
  },
  tags: [{
    type: String,
    trim: true
  }],
  mediaUrls: [{
    type: String,
    trim: true
  }],
  viewCount: {
    type: Number,
    default: 0
  },
  createdBy: {
    type: String,
    required: true
  },
  collaborators: [{
    type: String
  }],
  featured: {
    type: Boolean,
    default: false
  },
  published: {
    type: Boolean,
    default: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

/**
 * 索引
 */
KnowledgeSchema.index({ title: 'text', summary: 'text', content: 'text', tags: 'text' });
KnowledgeSchema.index({ category: 1 });
KnowledgeSchema.index({ tags: 1 });
KnowledgeSchema.index({ createdBy: 1 });
KnowledgeSchema.index({ featured: 1 });
KnowledgeSchema.index({ published: 1 });
KnowledgeSchema.index({ createdAt: -1 });
KnowledgeSchema.index({ viewCount: -1 });

// 创建模型
export const KnowledgeModel = mongoose.model<IKnowledge>('Knowledge', KnowledgeSchema);