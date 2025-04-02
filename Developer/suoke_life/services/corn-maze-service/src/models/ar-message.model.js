/**
 * AR留言数据模型
 */
const mongoose = require('mongoose');

const arMessageSchema = new mongoose.Schema({
  userId: {
    type: String,
    required: true
  },
  text: {
    type: String,
    required: true,
    trim: true,
    maxLength: 500
  },
  imageUrl: {
    type: String,
    required: false
  },
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point'
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
      required: true
    }
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  expiresAt: {
    type: Date,
    required: true
  },
  likes: {
    type: Number,
    default: 0
  },
  likedBy: [String],
  replyTo: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'ARMessage',
    required: false
  },
  mazeId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Maze',
    required: false
  },
  isPublic: {
    type: Boolean,
    default: true
  },
  targetUsers: [String],
  tags: [String]
});

// 索引
arMessageSchema.index({ location: '2dsphere' });
arMessageSchema.index({ userId: 1 });
arMessageSchema.index({ createdAt: -1 });
arMessageSchema.index({ expiresAt: 1 });
arMessageSchema.index({ mazeId: 1 });
arMessageSchema.index({ tags: 1 });

/**
 * 检查留言是否过期
 * @returns {Boolean} 是否过期
 */
arMessageSchema.methods.isExpired = function() {
  return new Date() > this.expiresAt;
};

/**
 * 用户点赞
 * @param {String} userId - 用户ID
 * @returns {Boolean} 是否成功点赞
 */
arMessageSchema.methods.addLike = function(userId) {
  if (this.likedBy.includes(userId)) {
    return false;
  }
  
  this.likedBy.push(userId);
  this.likes = this.likedBy.length;
  return true;
};

/**
 * 用户取消点赞
 * @param {String} userId - 用户ID
 * @returns {Boolean} 是否成功取消点赞
 */
arMessageSchema.methods.removeLike = function(userId) {
  const index = this.likedBy.indexOf(userId);
  if (index === -1) {
    return false;
  }
  
  this.likedBy.splice(index, 1);
  this.likes = this.likedBy.length;
  return true;
};

/**
 * 检查留言是否对用户可见
 * @param {String} userId - 用户ID
 * @returns {Boolean} 是否可见
 */
arMessageSchema.methods.isVisibleTo = function(userId) {
  // 公开留言对所有人可见
  if (this.isPublic) {
    return true;
  }
  
  // 私有留言只对创建者和目标用户可见
  return this.userId === userId || this.targetUsers.includes(userId);
};

const ARMessage = mongoose.model('ARMessage', arMessageSchema);

module.exports = ARMessage; 