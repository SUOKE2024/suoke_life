/**
 * 知识分类模型
 */

import mongoose, { Schema } from 'mongoose';
import { ICategory } from '../interfaces/knowledge.interface';

// 创建分类Schema
const CategorySchema: Schema = new Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
      index: true,
    },
    description: {
      type: String,
      trim: true,
    },
    parentId: {
      type: Schema.Types.ObjectId,
      ref: 'Category',
      index: true,
    },
    path: [{
      type: Schema.Types.ObjectId,
      ref: 'Category',
    }],
    level: {
      type: Number,
      default: 0,
      index: true,
    },
    icon: {
      type: String,
    },
    color: {
      type: String,
    },
    order: {
      type: Number,
      default: 0,
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
CategorySchema.index({ name: 'text' });

// 前置钩子：创建或更新时，如果有父分类，设置路径和级别
CategorySchema.pre('save', async function(next) {
  if (this.isModified('parentId')) {
    if (!this.parentId) {
      // 顶级分类
      this.path = [];
      this.level = 0;
    } else {
      const parent = await mongoose.model('Category').findById(this.parentId);
      if (parent) {
        this.path = [...(parent.path || []), parent._id];
        this.level = this.path.length;
      }
    }
  }
  next();
});

// 创建并导出模型
const CategoryModel = mongoose.model<ICategory>('Category', CategorySchema);

export default CategoryModel;