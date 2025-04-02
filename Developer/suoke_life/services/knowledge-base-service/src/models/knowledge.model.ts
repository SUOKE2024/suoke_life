/**
 * 知识条目模型
 */

import mongoose, { Schema } from 'mongoose';
import { IKnowledge } from '../interfaces/knowledge.interface';

// 导入mongoose-paginate-v2插件类型
import { PaginateModel } from 'mongoose-paginate-v2';

// 创建知识条目Schema
const KnowledgeSchema: Schema = new Schema(
  {
    title: {
      type: String,
      required: true,
      trim: true,
      index: true,
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
      required: true,
      index: true,
    }],
    tags: [{
      type: Schema.Types.ObjectId,
      ref: 'Tag',
      index: true,
    }],
    source: {
      type: String,
      trim: true,
    },
    author: {
      type: String,
      trim: true,
    },
    publishedAt: {
      type: Date,
      index: true,
    },
    status: {
      type: String,
      enum: ['draft', 'published', 'archived'],
      default: 'draft',
      index: true,
    },
    version: {
      type: Number,
      default: 1,
    },
    metadata: {
      type: Schema.Types.Mixed,
    },
    vectorId: {
      type: String,
      index: true,
    },
    keywords: [{
      type: String,
      index: true,
    }],
    viewCount: {
      type: Number,
      default: 0,
    },
    relations: {
      relatedKnowledge: [{
        type: Schema.Types.ObjectId,
        ref: 'Knowledge',
      }],
      prerequisites: [{
        type: Schema.Types.ObjectId,
        ref: 'Knowledge',
      }],
      nextSteps: [{
        type: Schema.Types.ObjectId,
        ref: 'Knowledge',
      }],
    },
  },
  {
    timestamps: true,
    versionKey: false,
  }
);

// 索引配置
KnowledgeSchema.index({ title: 'text', content: 'text', summary: 'text', keywords: 'text' });
KnowledgeSchema.index({ createdAt: -1 });
KnowledgeSchema.index({ updatedAt: -1 });

// 导入分页插件
import mongoosePaginate from 'mongoose-paginate-v2';
KnowledgeSchema.plugin(mongoosePaginate);

// 创建并导出模型
const KnowledgeModel = mongoose.model<IKnowledge, PaginateModel<IKnowledge>>(
  'Knowledge',
  KnowledgeSchema
);

export default KnowledgeModel;