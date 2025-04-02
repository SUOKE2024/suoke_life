import mongoose, { Document, Schema } from 'mongoose';

/**
 * 方言接口
 */
export interface IDialect extends Document {
  code: string;
  name: string;
  region: string;
  description: string;
  isActive: boolean;
  supportLevel: string;
  features: string[];
  modelPath?: string;
  accuracy?: number;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 方言模式
 */
const DialectSchema = new Schema<IDialect>({
  code: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  region: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true,
    trim: true
  },
  isActive: {
    type: Boolean,
    default: true
  },
  supportLevel: {
    type: String,
    enum: ['full', 'partial', 'basic'],
    default: 'basic'
  },
  features: [{
    type: String,
    enum: ['recognition', 'synthesis', 'translation']
  }],
  modelPath: {
    type: String,
    trim: true
  },
  accuracy: {
    type: Number,
    min: 0,
    max: 100
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
DialectSchema.index({ code: 1 }, { unique: true });
DialectSchema.index({ region: 1 });
DialectSchema.index({ isActive: 1 });
DialectSchema.index({ supportLevel: 1 });

// 创建模型
export const DialectModel = mongoose.model<IDialect>('Dialect', DialectSchema); 