/**
 * 任务模型
 * 用于管理老克NPC发布的任务及其进度
 */
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// 任务步骤模式
const questStepSchema = new Schema({
  // 步骤标题
  title: {
    type: String,
    required: true
  },
  
  // 步骤描述
  description: {
    type: String,
    required: true
  },
  
  // 步骤序号
  order: {
    type: Number,
    required: true
  },
  
  // 完成条件
  completionCriteria: {
    type: {
      type: String,
      enum: ['location', 'scan', 'collection', 'interaction', 'gesture', 'time', 'custom'],
      required: true
    },
    data: Schema.Types.Mixed,
    required: true
  },
  
  // 完成状态
  completed: {
    type: Boolean,
    default: false
  },
  
  // 完成时间
  completedAt: {
    type: Date
  },
  
  // 超时时间，如果设置了时间限制
  timeout: {
    type: Date
  },
  
  // 步骤提示
  hints: [{
    text: String,
    unlocked: {
      type: Boolean,
      default: false
    }
  }]
});

// 奖励模式
const rewardSchema = new Schema({
  // 奖励类型
  type: {
    type: String,
    enum: ['points', 'item', 'treasure', 'knowledge', 'plantSeed', 'currency'],
    required: true
  },
  
  // 奖励数量
  amount: {
    type: Number,
    default: 1
  },
  
  // 奖励详情
  details: Schema.Types.Mixed,
  
  // 是否已颁发
  awarded: {
    type: Boolean,
    default: false
  },
  
  // 颁发时间
  awardedAt: {
    type: Date
  }
});

// 任务主模式
const questSchema = new Schema({
  // 用户ID
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  
  // 任务标题
  title: {
    type: String,
    required: true
  },
  
  // 任务描述
  description: {
    type: String,
    required: true
  },
  
  // 任务类型
  type: {
    type: String,
    enum: ['standard', 'daily', 'story', 'special', 'tutorial', 'seasonal'],
    default: 'standard'
  },
  
  // 任务状态
  status: {
    type: String,
    enum: ['pending', 'active', 'in_progress', 'completed', 'failed', 'expired'],
    default: 'pending'
  },
  
  // 任务进度 (0-100)
  progress: {
    type: Number,
    default: 0,
    min: 0,
    max: 100
  },
  
  // 任务步骤
  steps: [questStepSchema],
  
  // 任务奖励
  rewards: [rewardSchema],
  
  // 任务难度
  difficulty: {
    type: String,
    enum: ['beginner', 'easy', 'normal', 'hard', 'expert'],
    default: 'normal'
  },
  
  // 截止日期
  deadline: {
    type: Date
  },
  
  // 是否重复任务
  repeatable: {
    type: Boolean,
    default: false
  },
  
  // 重复间隔（天）
  repeatInterval: {
    type: Number
  },
  
  // 关联NPC ID
  npcId: {
    type: String,
    default: 'laoke'
  },
  
  // 任务区域限制
  locationRestriction: {
    enabled: {
      type: Boolean,
      default: false
    },
    mazeId: {
      type: Schema.Types.ObjectId,
      ref: 'Maze'
    },
    radius: {
      type: Number,
      default: 100 // 米
    },
    center: {
      type: {
        type: String,
        enum: ['Point'],
        default: 'Point'
      },
      coordinates: {
        type: [Number],
        default: [0, 0]
      }
    }
  },
  
  // 前置任务要求
  prerequisites: [{
    questId: {
      type: Schema.Types.ObjectId,
      ref: 'Quest'
    },
    requiredStatus: {
      type: String,
      enum: ['active', 'in_progress', 'completed'],
      default: 'completed'
    }
  }],
  
  // 任务标签
  tags: [String],
  
  // 任务元数据
  metadata: Schema.Types.Mixed
}, {
  timestamps: true
});

// 索引优化
questSchema.index({ userId: 1, status: 1 });
questSchema.index({ 'locationRestriction.center.coordinates': '2dsphere' });
questSchema.index({ createdAt: -1 });
questSchema.index({ deadline: 1 });
questSchema.index({ tags: 1 });

// 虚拟属性：是否过期
questSchema.virtual('isExpired').get(function() {
  if (!this.deadline) return false;
  return new Date() > this.deadline;
});

// 方法：计算进度
questSchema.methods.calculateProgress = function() {
  if (this.steps.length === 0) return 0;
  
  const completedSteps = this.steps.filter(step => step.completed).length;
  const progressPercent = (completedSteps / this.steps.length) * 100;
  
  this.progress = Math.round(progressPercent);
  return this.progress;
};

// 方法：完成步骤
questSchema.methods.completeStep = async function(stepOrder) {
  const step = this.steps.find(s => s.order === stepOrder);
  if (!step) return false;
  
  step.completed = true;
  step.completedAt = new Date();
  
  // 重新计算总进度
  this.calculateProgress();
  
  // 检查是否所有步骤都已完成
  const allCompleted = this.steps.every(s => s.completed);
  if (allCompleted) {
    this.status = 'completed';
  } else if (this.status === 'pending' || this.status === 'active') {
    this.status = 'in_progress';
  }
  
  await this.save();
  return true;
};

// 方法：颁发奖励
questSchema.methods.awardRewards = async function() {
  if (this.status !== 'completed') return false;
  
  const pendingRewards = this.rewards.filter(r => !r.awarded);
  for (const reward of pendingRewards) {
    reward.awarded = true;
    reward.awardedAt = new Date();
  }
  
  await this.save();
  return pendingRewards;
};

// 静态方法：获取活跃任务
questSchema.statics.getActiveQuests = function(userId) {
  return this.find({
    userId,
    status: { $in: ['active', 'in_progress'] }
  }).sort({ deadline: 1 }).lean();
};

// 静态方法：获取即将过期的任务
questSchema.statics.getExpiringQuests = function(hours = 24) {
  const expiryThreshold = new Date();
  expiryThreshold.setHours(expiryThreshold.getHours() + hours);
  
  return this.find({
    deadline: { $lt: expiryThreshold, $gt: new Date() },
    status: { $in: ['active', 'in_progress'] }
  }).lean();
};

// 预保存钩子
questSchema.pre('save', function(next) {
  // 自动计算进度
  if (this.isModified('steps')) {
    this.calculateProgress();
  }
  
  // 检查过期状态
  if (this.deadline && new Date() > this.deadline && 
      ['active', 'in_progress'].includes(this.status)) {
    this.status = 'expired';
  }
  
  next();
});

const Quest = mongoose.model('Quest', questSchema);

module.exports = Quest; 