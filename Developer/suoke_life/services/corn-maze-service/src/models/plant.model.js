/**
 * 玉米植物数据模型
 */
const mongoose = require('mongoose');
const { CORN_GROWTH_STAGES, GAME_PHASES } = require('../utils/constants');

const plantSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  userId: {
    type: String,
    required: true
  },
  nickname: {
    type: String,
    required: false,
    trim: true
  },
  growthStage: {
    type: Number,
    required: true,
    enum: Object.values(CORN_GROWTH_STAGES),
    default: CORN_GROWTH_STAGES.SEED
  },
  health: {
    type: Number,
    required: true,
    min: 0,
    max: 100,
    default: 100
  },
  waterLevel: {
    type: Number,
    required: true,
    min: 0,
    max: 100,
    default: 50
  },
  nutrientLevel: {
    type: Number,
    required: true,
    min: 0,
    max: 100,
    default: 50
  },
  location: {
    x: { type: Number, required: true },
    y: { type: Number, required: true },
    plotId: { type: String, required: true }
  },
  careHistory: [{
    action: {
      type: String,
      enum: ['water', 'fertilize', 'treat', 'prune', 'harvest'],
      required: true
    },
    timestamp: {
      type: Date,
      default: Date.now
    },
    performedBy: {
      type: String,
      required: true
    },
    details: {
      type: String,
      required: false
    }
  }],
  plantedAt: {
    type: Date,
    required: true,
    default: Date.now
  },
  lastWateredAt: {
    type: Date,
    required: false
  },
  lastFertilizedAt: {
    type: Date,
    required: false
  },
  harvested: {
    type: Boolean,
    default: false
  },
  harvestedAt: {
    type: Date,
    required: false
  },
  yield: {
    type: Number,
    required: false,
    min: 0
  },
  seasonId: {
    type: String,
    required: true
  },
  gamePhase: {
    type: String,
    required: true,
    enum: Object.values(GAME_PHASES),
    default: GAME_PHASES.PLANTING
  },
  isActive: {
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
}, {
  timestamps: { createdAt: 'createdAt', updatedAt: 'updatedAt' }
});

// 索引
plantSchema.index({ userId: 1 });
plantSchema.index({ 'location.plotId': 1 });
plantSchema.index({ growthStage: 1 });
plantSchema.index({ seasonId: 1 });
plantSchema.index({ gamePhase: 1 });

/**
 * 浇水
 * @param {String} userId - 执行用户ID
 * @param {String} details - 详细信息
 * @returns {Boolean} 是否成功
 */
plantSchema.methods.water = function(userId, details = '') {
  // 检查植物是否可以浇水
  if (this.harvested || !this.isActive) {
    return false;
  }
  
  // 添加浇水记录
  this.careHistory.push({
    action: 'water',
    performedBy: userId,
    timestamp: new Date(),
    details
  });
  
  // 更新水分等级和最后浇水时间
  this.waterLevel = Math.min(100, this.waterLevel + 30);
  this.lastWateredAt = new Date();
  
  return true;
};

/**
 * 施肥
 * @param {String} userId - 执行用户ID
 * @param {String} details - 详细信息
 * @returns {Boolean} 是否成功
 */
plantSchema.methods.fertilize = function(userId, details = '') {
  // 检查植物是否可以施肥
  if (this.harvested || !this.isActive) {
    return false;
  }
  
  // 添加施肥记录
  this.careHistory.push({
    action: 'fertilize',
    performedBy: userId,
    timestamp: new Date(),
    details
  });
  
  // 更新营养等级和最后施肥时间
  this.nutrientLevel = Math.min(100, this.nutrientLevel + 30);
  this.lastFertilizedAt = new Date();
  
  return true;
};

/**
 * 收获
 * @param {String} userId - 执行用户ID
 * @param {Number} yield - 产量
 * @returns {Boolean} 是否成功
 */
plantSchema.methods.harvest = function(userId, yield = 1) {
  // 检查植物是否可以收获
  if (this.harvested || !this.isActive || this.growthStage !== CORN_GROWTH_STAGES.MATURITY) {
    return false;
  }
  
  // 添加收获记录
  this.careHistory.push({
    action: 'harvest',
    performedBy: userId,
    timestamp: new Date(),
    details: `收获了${yield}个玉米`
  });
  
  // 更新收获状态
  this.harvested = true;
  this.harvestedAt = new Date();
  this.yield = yield;
  
  return true;
};

/**
 * 生长
 * @returns {Boolean} 是否成功生长
 */
plantSchema.methods.grow = function() {
  // 检查是否可以生长
  if (this.harvested || !this.isActive || this.growthStage === CORN_GROWTH_STAGES.MATURITY) {
    return false;
  }
  
  // 检查健康状况
  if (this.health < 30 || this.waterLevel < 20 || this.nutrientLevel < 20) {
    // 健康状况不佳，无法生长
    return false;
  }
  
  // 更新生长阶段
  this.growthStage = Math.min(CORN_GROWTH_STAGES.MATURITY, this.growthStage + 1);
  
  // 消耗资源
  this.waterLevel = Math.max(0, this.waterLevel - 20);
  this.nutrientLevel = Math.max(0, this.nutrientLevel - 15);
  
  return true;
};

/**
 * 更新状态
 * @returns {Boolean} 是否成功更新
 */
plantSchema.methods.updateStatus = function() {
  const now = new Date();
  const lastWatered = this.lastWateredAt || this.plantedAt;
  const lastFertilized = this.lastFertilizedAt || this.plantedAt;
  
  // 计算时间差（天）
  const daysSinceWatered = Math.floor((now - lastWatered) / (1000 * 60 * 60 * 24));
  const daysSinceFertilized = Math.floor((now - lastFertilized) / (1000 * 60 * 60 * 24));
  
  // 更新水分和营养
  if (daysSinceWatered > 0) {
    this.waterLevel = Math.max(0, this.waterLevel - (daysSinceWatered * 10));
  }
  
  if (daysSinceFertilized > 0) {
    this.nutrientLevel = Math.max(0, this.nutrientLevel - (daysSinceFertilized * 5));
  }
  
  // 更新健康状况
  if (this.waterLevel < 20 || this.nutrientLevel < 20) {
    this.health = Math.max(0, this.health - 10);
  } else {
    this.health = Math.min(100, this.health + 5);
  }
  
  return true;
};

const Plant = mongoose.model('Plant', plantSchema);

module.exports = Plant;
