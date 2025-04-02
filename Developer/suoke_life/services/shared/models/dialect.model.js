/**
 * 方言模型定义
 * 用于存储和管理方言相关信息
 */

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

/**
 * 方言定义模式
 */
const dialectSchema = new Schema({
  // 方言代码（唯一标识）
  code: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    index: true
  },
  
  // 方言名称
  name: {
    type: String,
    required: true,
    trim: true
  },
  
  // 方言地区
  region: {
    province: { type: String, required: true },
    city: { type: String },
    county: { type: [String] }
  },
  
  // 使用人口数量（估计）
  speakerCount: {
    type: Number,
    default: 0
  },
  
  // 方言特征描述
  features: {
    phonetic: { type: [String] }, // 语音特征
    vocabulary: { type: [String] }, // 词汇特征
    grammar: { type: [String] }  // 语法特征
  },
  
  // 方言状态
  status: {
    type: String,
    enum: ['active', 'inactive', 'development'],
    default: 'development'
  },
  
  // 方言识别支持级别
  supportLevel: {
    type: Number,
    min: 0,
    max: 5,
    default: 0,
    description: '0=不支持, 1=基础识别, 2=基本翻译, 3=普通对话, 4=地方文化理解, 5=完全支持'
  },
  
  // 样本数量统计
  sampleStats: {
    total: { type: Number, default: 0 },
    verified: { type: Number, default: 0 },
    pending: { type: Number, default: 0 },
    duration: { type: Number, default: 0 } // 总时长(秒)
  },
  
  // 训练模型信息
  models: [{
    version: String,
    accuracy: Number,
    trainedAt: Date,
    parameters: Schema.Types.Mixed,
    performance: {
      wer: Number, // 词错误率
      cer: Number  // 字错误率
    }
  }],
  
  // 元数据
  metadata: {
    description: String,
    history: String,
    culturalNotes: [String],
    references: [String]
  },
  
  // 系统时间戳
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'createdAt', updatedAt: 'updatedAt' },
  collection: 'dialects',
  versionKey: false
});

// 索引优化
dialectSchema.index({ 'region.province': 1 });
dialectSchema.index({ status: 1, supportLevel: 1 });

/**
 * 方言样本模式
 */
const dialectSampleSchema = new Schema({
  // 关联的方言
  dialectCode: {
    type: String,
    required: true,
    ref: 'Dialect',
    index: true
  },
  
  // 音频URL
  audioUrl: {
    type: String,
    required: true
  },
  
  // 转写文本
  transcription: {
    type: String,
    required: true
  },
  
  // 标准普通话翻译
  standardTranslation: {
    type: String
  },
  
  // 发言者信息
  speakerInfo: {
    gender: {
      type: String,
      enum: ['male', 'female', 'other', 'unknown'],
      default: 'unknown'
    },
    ageGroup: {
      type: String,
      enum: ['child', 'youth', 'adult', 'elder', 'unknown'],
      default: 'unknown'
    },
    isNativeSpeaker: {
      type: Boolean,
      default: true
    }
  },
  
  // 音频特征
  audioFeatures: {
    duration: Number,         // 时长（秒）
    snr: Number,              // 信噪比
    sampleRate: Number,       // 采样率
    channels: Number,         // 通道数
    format: String,           // 文件格式
    fileSize: Number          // 文件大小（字节）
  },
  
  // 样本质量
  qualityScore: {
    type: Number,
    min: 0,
    max: 1,
    default: 0.5
  },
  
  // 来源信息
  source: {
    method: {
      type: String,
      enum: ['user-upload', 'field-recording', 'public-media', 'research-partner'],
      default: 'user-upload'
    },
    location: {
      province: String,
      city: String,
      district: String,
      coordinates: {
        latitude: Number,
        longitude: Number
      }
    },
    contributor: {
      type: Schema.Types.ObjectId,
      ref: 'User'
    },
    projectId: String,
    collectedAt: {
      type: Date,
      default: Date.now
    }
  },
  
  // 验证状态
  verificationStatus: {
    type: String,
    enum: ['pending', 'verified', 'rejected'],
    default: 'pending'
  },
  
  // 标签
  tags: {
    type: [String],
    default: []
  },
  
  // 系统时间戳
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'createdAt', updatedAt: 'updatedAt' },
  collection: 'dialect_samples',
  versionKey: false
});

// 索引优化
dialectSampleSchema.index({ dialectCode: 1, verificationStatus: 1 });
dialectSampleSchema.index({ qualityScore: -1 });
dialectSampleSchema.index({ 'source.method': 1 });
dialectSampleSchema.index({ 'source.contributor': 1 });

/**
 * 方言挑战活动模式
 */
const dialectChallengeSchema = new Schema({
  title: {
    type: String,
    required: true
  },
  
  description: {
    type: String,
    required: true
  },
  
  // 包含的方言
  dialectCodes: {
    type: [String],
    required: true,
    validate: [arr => arr.length > 0, '至少需要一种方言']
  },
  
  // 时间范围
  startDate: {
    type: Date,
    required: true
  },
  
  endDate: {
    type: Date,
    required: true
  },
  
  // 奖励积分
  rewardPoints: {
    type: Number,
    required: true,
    min: 0
  },
  
  // 最小样本要求
  minSamplesRequired: {
    type: Number,
    default: 1,
    min: 1
  },
  
  // 样本质量阈值
  qualityThreshold: {
    type: Number,
    default: 0.6,
    min: 0,
    max: 1
  },
  
  // 挑战状态
  status: {
    type: String,
    enum: ['upcoming', 'active', 'completed', 'cancelled'],
    default: 'upcoming'
  },
  
  // 参与者
  participants: [{
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User'
    },
    joinedAt: {
      type: Date,
      default: Date.now
    },
    submittedSamples: {
      type: Number,
      default: 0
    },
    acceptedSamples: {
      type: Number,
      default: 0
    },
    pointsEarned: {
      type: Number,
      default: 0
    }
  }],
  
  // 系统时间戳
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'createdAt', updatedAt: 'updatedAt' },
  collection: 'dialect_challenges',
  versionKey: false
});

// 索引优化
dialectChallengeSchema.index({ status: 1 });
dialectChallengeSchema.index({ startDate: 1, endDate: 1 });
dialectChallengeSchema.index({ 'participants.userId': 1 });

// 创建模型
const Dialect = mongoose.model('Dialect', dialectSchema);
const DialectSample = mongoose.model('DialectSample', dialectSampleSchema);
const DialectChallenge = mongoose.model('DialectChallenge', dialectChallengeSchema);

module.exports = {
  Dialect,
  DialectSample,
  DialectChallenge
};