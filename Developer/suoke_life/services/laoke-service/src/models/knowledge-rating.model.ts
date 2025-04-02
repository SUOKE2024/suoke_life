import mongoose, { Document, Schema } from 'mongoose';

/**
 * 知识评分接口
 */
export interface IKnowledgeRating extends Document {
  knowledgeId: string;
  userId: string;
  rating: number;
  feedback?: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 知识评分模式
 */
const KnowledgeRatingSchema = new Schema<IKnowledgeRating>({
  knowledgeId: {
    type: String,
    required: true,
    ref: 'Knowledge'
  },
  userId: {
    type: String,
    required: true
  },
  rating: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  },
  feedback: {
    type: String,
    trim: true
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
KnowledgeRatingSchema.index({ knowledgeId: 1, userId: 1 }, { unique: true });
KnowledgeRatingSchema.index({ knowledgeId: 1 });
KnowledgeRatingSchema.index({ userId: 1 });
KnowledgeRatingSchema.index({ rating: -1 });

// 创建模型
export const KnowledgeRatingModel = mongoose.model<IKnowledgeRating>('KnowledgeRating', KnowledgeRatingSchema); 