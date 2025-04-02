/**
 * NPC交互模型
 * 用于记录用户与NPC的交互历史
 */
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const npcInteractionSchema = new Schema({
  // 用户ID
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  
  // NPC ID
  npcId: {
    type: String,
    required: true,
    index: true,
    default: 'laoke'
  },
  
  // 用户消息
  userMessage: {
    type: String,
    required: true
  },
  
  // NPC回复
  npcResponse: {
    type: String,
    required: true
  },
  
  // 会话ID，用于关联同一个对话中的多条交互
  sessionId: {
    type: String,
    index: true
  },
  
  // 情感分析
  sentiment: {
    type: String,
    enum: ['positive', 'neutral', 'negative'],
    default: 'neutral'
  },
  
  // NPC触发的动作列表
  actions: [{
    type: {
      type: String,
      enum: ['quest', 'reward', 'hint', 'knowledge', 'item'],
      required: true
    },
    data: Schema.Types.Mixed,
    executed: {
      type: Boolean,
      default: false
    }
  }],
  
  // 交互位置信息
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point'
    },
    coordinates: {
      type: [Number],
      default: [0, 0]
    },
    mazeId: {
      type: Schema.Types.ObjectId,
      ref: 'Maze'
    },
    section: String
  },
  
  // 交互时的设备信息
  device: {
    type: {
      type: String,
      enum: ['mobile', 'ar_headset', 'web'],
      default: 'mobile'
    },
    osVersion: String,
    appVersion: String
  },
  
  // 上下文数据
  context: Schema.Types.Mixed
}, {
  timestamps: true
});

// 索引优化
npcInteractionSchema.index({ createdAt: -1 });
npcInteractionSchema.index({ 'location.coordinates': '2dsphere' });
npcInteractionSchema.index({ userId: 1, createdAt: -1 });

// 方法：判断交互是否需要后续动作
npcInteractionSchema.methods.hasActionsPending = function() {
  return this.actions.some(action => !action.executed);
};

// 方法：标记动作为已执行
npcInteractionSchema.methods.markActionExecuted = async function(actionIndex) {
  if (actionIndex >= 0 && actionIndex < this.actions.length) {
    this.actions[actionIndex].executed = true;
    return await this.save();
  }
  return this;
};

// 静态方法：获取用户最近交互
npcInteractionSchema.statics.getRecentUserInteractions = function(userId, limit = 10) {
  return this.find({ userId })
    .sort({ createdAt: -1 })
    .limit(limit)
    .lean();
};

// 静态方法：获取特定区域的交互
npcInteractionSchema.statics.getInteractionsByLocation = function(coordinates, maxDistance = 100) {
  return this.find({
    'location.coordinates': {
      $near: {
        $geometry: {
          type: 'Point',
          coordinates: coordinates
        },
        $maxDistance: maxDistance
      }
    }
  }).lean();
};

const NPCInteraction = mongoose.model('NPCInteraction', npcInteractionSchema);

module.exports = NPCInteraction; 