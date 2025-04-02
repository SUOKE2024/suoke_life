import mongoose, { Schema, Document } from 'mongoose';

export interface IBlogComment extends Document {
  blog: string;
  author: string;
  content: string;
  parentComment?: string;
  likeCount: number;
  isApproved: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const BlogCommentSchema: Schema = new Schema({
  blog: {
    type: Schema.Types.ObjectId,
    ref: 'Blog',
    required: true
  },
  author: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  content: {
    type: String,
    required: true,
    trim: true,
    maxlength: 1000
  },
  parentComment: {
    type: Schema.Types.ObjectId,
    ref: 'BlogComment'
  },
  likeCount: {
    type: Number,
    default: 0
  },
  isApproved: {
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

// 创建索引以提高查询性能
BlogCommentSchema.index({ blog: 1 });
BlogCommentSchema.index({ author: 1 });
BlogCommentSchema.index({ parentComment: 1 });
BlogCommentSchema.index({ createdAt: -1 });

export const BlogCommentModel = mongoose.model<IBlogComment>('BlogComment', BlogCommentSchema); 