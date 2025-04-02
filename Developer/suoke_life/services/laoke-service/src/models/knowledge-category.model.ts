import mongoose, { Document, Schema } from 'mongoose';

/**
 * 知识分类接口
 */
export interface IKnowledgeCategory extends Document {
  name: string;
  description: string;
  icon: string;
  color: string;
  order: number;
  parentId: mongoose.Types.ObjectId | null;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 知识分类模式
 */
const KnowledgeCategorySchema = new Schema<IKnowledgeCategory>({
  name: {
    type: String,
    required: true,
    trim: true,
    unique: true
  },
  description: {
    type: String,
    required: true,
    trim: true
  },
  icon: {
    type: String,
    trim: true,
    default: 'folder-open'
  },
  color: {
    type: String,
    trim: true,
    default: '#35BB78' // 索克绿
  },
  order: {
    type: Number,
    default: 0
  },
  parentId: {
    type: Schema.Types.ObjectId,
    ref: 'KnowledgeCategory',
    default: null
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
KnowledgeCategorySchema.index({ name: 1 }, { unique: true });
KnowledgeCategorySchema.index({ order: 1 });
KnowledgeCategorySchema.index({ parentId: 1 });

// 创建模型
export const KnowledgeCategoryModel = mongoose.model<IKnowledgeCategory>('KnowledgeCategory', KnowledgeCategorySchema); 