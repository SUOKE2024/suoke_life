/**
 * 知识版本历史模型
 */

import mongoose, { Schema } from 'mongoose';
import { IKnowledgeVersion } from '../interfaces/knowledge.interface';

// 创建知识版本Schema
const KnowledgeVersionSchema: Schema = new Schema(
  {
    knowledgeId: {
      type: Schema.Types.ObjectId,
      ref: 'Knowledge',
      required: true,
      index: true,
    },
    version: {
      type: Number,
      required: true,
    },
    title: {
      type: String,
      required: true,
      trim: true,
    },
    content: {
      type: String,
      required: true,
    },
    summary: {
      type: String,
      trim: true,
    },
    categories: [{
      type: Schema.Types.ObjectId,
      ref: 'Category',
    }],
    tags: [{
      type: Schema.Types.ObjectId,
      ref: 'Tag',
    }],
    createdBy: {
      type: String,
      trim: true,
    },
    comment: {
      type: String,
      trim: true,
    },
  },
  {
    timestamps: true,
    versionKey: false,
  }
);

// 创建复合索引确保每个知识条目的版本是唯一的
KnowledgeVersionSchema.index({ knowledgeId: 1, version: 1 }, { unique: true });

// 创建并导出模型
const KnowledgeVersionModel = mongoose.model<IKnowledgeVersion>(
  'KnowledgeVersion', 
  KnowledgeVersionSchema
);

export default KnowledgeVersionModel;