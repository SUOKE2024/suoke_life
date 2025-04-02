/**
 * 宝藏数据模型
 */
const mongoose = require('mongoose');
const { REWARD_TYPES, REWARD_RARITY, AR_MARKER_TYPES } = require('../utils/constants');

const treasureSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true,
    trim: true
  },
  rewardType: {
    type: String,
    required: true,
    enum: Object.values(REWARD_TYPES)
  },
  rarity: {
    type: Number,
    required: true,
    enum: Object.values(REWARD_RARITY),
    default: REWARD_RARITY.COMMON
  },
  value: {
    type: Number,
    required: true,
    min: 1
  },
  quantity: {
    type: Number,
    required: true,
    min: 1,
    default: 1
  },
  imageUrl: {
    type: String,
    required: false
  },
  arMarker: {
    type: {
      type: String,
      enum: Object.values(AR_MARKER_TYPES),
      default: AR_MARKER_TYPES.TREASURE
    },
    markerId: {
      type: String,
      required: true
    },
    modelUrl: {
      type: String,
      required: false
    }
  },
  // 新增AR增强字段
  interactionType: {
    type: String,
    enum: ['simple', 'gesture', 'puzzle', 'ar_animation'],
    default: 'simple'
  },
  recognitionData: {
    imageSignatures: [String],
    objectModels: [String],
    soundSignatures: [String]
  },
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point'
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
      default: [0, 0]
    }
  },
  gestureName: String,
  puzzleData: mongoose.Schema.Types.Mixed,
  animationAsset: String,
  effectsEnabled: {
    sound: { type: Boolean, default: true },
    particles: { type: Boolean, default: true },
    haptic: { type: Boolean, default: true }
  },
  unlockRequirements: [{
    type: { type: String, enum: ['item', 'achievement', 'team', 'time'] },
    value: mongoose.Schema.Types.Mixed
  }],
  // 社交功能字段
  sharable: { 
    type: Boolean,
    default: false
  },
  // 原有字段
  discoveredBy: [{
    userId: {
      type: String,
      required: true
    },
    discoveredAt: {
      type: Date,
      default: Date.now
    },
    mazeId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Maze',
      required: true
    }
  }],
  validFrom: {
    type: Date,
    required: false
  },
  validTo: {
    type: Date,
    required: false
  },
  seasonId: {
    type: String,
    required: true
  },
  isLimited: {
    type: Boolean,
    default: false
  },
  limitedQuantity: {
    type: Number,
    required: false
  },
  remainingQuantity: {
    type: Number,
    required: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'createdAt', updatedAt: 'updatedAt' }
});

// 索引
treasureSchema.index({ name: 1 });
treasureSchema.index({ rewardType: 1 });
treasureSchema.index({ rarity: 1 });
treasureSchema.index({ 'arMarker.markerId': 1 });
treasureSchema.index({ seasonId: 1 });
// 新增索引
treasureSchema.index({ 'recognitionData.imageSignatures': 1 });
treasureSchema.index({ location: '2dsphere' });
treasureSchema.index({ interactionType: 1 });

/**
 * 检查宝藏是否可用
 * @returns {Boolean} 是否可用
 */
treasureSchema.methods.isAvailable = function() {
  const now = new Date();
  
  // 检查时间有效性
  if (this.validFrom && now < this.validFrom) {
    return false;
  }
  
  if (this.validTo && now > this.validTo) {
    return false;
  }
  
  // 检查数量限制
  if (this.isLimited && this.remainingQuantity <= 0) {
    return false;
  }
  
  return true;
};

/**
 * 标记被发现
 * @param {String} userId - 用户ID
 * @param {String} mazeId - 迷宫ID
 * @returns {Boolean} 是否成功标记
 */
treasureSchema.methods.markDiscovered = function(userId, mazeId) {
  // 检查是否已被该用户发现
  const alreadyDiscovered = this.discoveredBy.some(
    d => d.userId === userId && d.mazeId.toString() === mazeId.toString()
  );
  
  if (alreadyDiscovered) {
    return false;
  }
  
  // 添加发现记录
  this.discoveredBy.push({
    userId,
    mazeId,
    discoveredAt: new Date()
  });
  
  // 更新剩余数量
  if (this.isLimited && this.remainingQuantity > 0) {
    this.remainingQuantity -= 1;
  }
  
  return true;
};

/**
 * 检查宝藏是否可分享
 * @returns {Boolean} 是否可分享
 */
treasureSchema.methods.isSharable = function() {
  return this.sharable === true;
};

const Treasure = mongoose.model('Treasure', treasureSchema);

module.exports = Treasure;
