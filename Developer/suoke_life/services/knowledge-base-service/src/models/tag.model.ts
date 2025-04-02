/**
 * 知识标签模型
 */

import mongoose, { Schema } from 'mongoose';
import { ITag } from '../interfaces/knowledge.interface';

// 创建标签Schema
const TagSchema: Schema = new Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
      unique: true,
      index: true,
    },
    description: {
      type: String,
      trim: true,
    },
    color: {
      type: String,
    },
    knowledgeCount: {
      type: Number,
      default: 0,
    },
  },
  {
    timestamps: true,
    versionKey: false,
  }
);

// 索引配置
TagSchema.index({ name: 'text' });
TagSchema.index({ knowledgeCount: -1 });

// 创建并导出模型
const TagModel = mongoose.model<ITag>('Tag', TagSchema);

export default TagModel;