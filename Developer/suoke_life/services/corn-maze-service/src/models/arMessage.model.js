/**
 * AR消息模型
 * 用于管理AR留言功能
 */
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const arMessageSchema = new Schema({
  // 用户ID
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  
  // 消息内容
  content: {
    type: String,
    required: true,
    maxlength: 500
  },
  
  // 位置信息
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point'
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
      required: true
    },
    altitude: {
      type: Number,
      default: 0
    },
    accuracy: {
      type: Number,
      default: 10
    }
  },
  
  // 可见性
  visibility: {
    type: String,
    enum: ['private', 'team', 'public'],
    default: 'public'
  },
  
  // 相关团队
  teams: [{
    teamId: {
      type: Schema.Types.ObjectId,
      ref: 'Team'
    }
  }],
  
  // 媒体附件
  media: [{
    type: {
      type: String,
      enum: ['image', 'audio', 'video', 'model3d'],
      required: true
    },
    url: {
      type: String,
      required: true
    },
    thumbnailUrl: String,
    duration: Number,
    size: Number
  }],
  
  // 过期时间
  expires: {
    type: Date,
    default: function() {
      // 默认24小时后过期
      const date = new Date();
      date.setHours(date.getHours() + 24);
      return date;
    },
    index: true
  },
  
  // 样式
  style: {
    color: {
      type: String,
      default: '#35BB78' // 索克绿
    },
    size: {
      type: Number,
      default: 1.0
    },
    animation: {
      type: String,
      enum: ['none', 'pulse', 'bounce', 'fade', 'rotate'],
      default: 'none'
    },
    font: {
      type: String,
      default: 'default'
    }
  },
  
  // 相关宝藏ID
  relatedTreasureId: {
    type: Schema.Types.ObjectId,
    ref: 'Treasure',
    index: true
  },
  
  // 固定到AR空间
  isPinned: {
    type: Boolean,
    default: false
  },
  
  // 互动统计
  interactions: {
    views: {
      type: Number,
      default: 0
    },
    likes: {
      type: Number,
      default: 0
    },
    shares: {
      type: Number,
      default: 0
    }
  },
  
  // 设备信息
  device: {
    type: {
      type: String,
      enum: ['mobile', 'ar_headset', 'web'],
      default: 'mobile'
    },
    osVersion: String,
    appVersion: String
  },
  
  // 回复功能
  replies: [{
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User'
    },
    content: {
      type: String,
      required: true,
      maxlength: 200
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  }]
}, {
  timestamps: true
});

// 索引优化
arMessageSchema.index({ 'location.coordinates': '2dsphere' });
arMessageSchema.index({ createdAt: -1 });
arMessageSchema.index({ 'replies.createdAt': -1 });
arMessageSchema.index({ userId: 1, createdAt: -1 });

// 虚拟属性：是否过期
arMessageSchema.virtual('isExpired').get(function() {
  return new Date() > this.expires;
});

// 虚拟属性：年龄（分钟）
arMessageSchema.virtual('ageInMinutes').get(function() {
  return Math.floor((Date.now() - this.createdAt) / (1000 * 60));
});

// 方法：增加查看次数
arMessageSchema.methods.increaseViews = async function() {
  this.interactions.views += 1;
  return await this.save();
};

// 方法：添加回复
arMessageSchema.methods.addReply = async function(userId, content) {
  this.replies.push({
    userId,
    content,
    createdAt: new Date()
  });
  
  return await this.save();
};

// 方法：删除回复
arMessageSchema.methods.removeReply = async function(replyId) {
  this.replies = this.replies.filter(reply => reply._id.toString() !== replyId.toString());
  return await this.save();
};

// 静态方法：获取热门消息
arMessageSchema.statics.getPopularMessages = function(limit = 10) {
  return this.find({
    visibility: 'public',
    expires: { $gt: new Date() }
  })
  .sort({ 'interactions.views': -1, createdAt: -1 })
  .limit(limit)
  .populate('userId', 'username avatar')
  .lean();
};

// 静态方法：获取用户消息
arMessageSchema.statics.getUserMessages = function(userId, limit = 20) {
  return this.find({ userId })
    .sort({ createdAt: -1 })
    .limit(limit)
    .lean();
};

// 预保存钩子
arMessageSchema.pre('save', function(next) {
  // 检查团队可见性
  if (this.visibility === 'team' && (!this.teams || this.teams.length === 0)) {
    this.visibility = 'public'; // 如果设置为团队可见但没有团队，则改为公开
  }
  
  next();
});

// 设置模型
const ARMessage = mongoose.model('ARMessage', arMessageSchema);

module.exports = ARMessage; 