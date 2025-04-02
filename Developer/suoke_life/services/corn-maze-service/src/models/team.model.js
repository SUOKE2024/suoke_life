/**
 * 团队模型
 * 用于管理多人游戏的团队数据
 */
const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const shortid = require('shortid');
const { TEAM_STATUS } = require('../utils/constants');

// 玩家状态模式
const playerStatusSchema = new Schema({
  userId: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  position: {
    x: {
      type: Number,
      default: 0
    },
    y: {
      type: Number,
      default: 0
    }
  },
  isActive: {
    type: Boolean,
    default: true
  },
  isLeader: {
    type: Boolean,
    default: false
  },
  lastActivity: {
    type: Date,
    default: Date.now
  },
  joinedAt: {
    type: Date,
    default: Date.now
  },
  treasuresFound: {
    type: [String],
    default: []
  },
  score: {
    type: Number,
    default: 0
  },
  avatar: {
    type: String,
    default: null
  }
}, { _id: false });

// 团队邀请模式
const invitationSchema = new Schema({
  code: {
    type: String,
    required: true,
    default: () => shortid.generate()
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  expiresAt: {
    type: Date,
    required: true
  },
  usedBy: {
    type: [String],
    default: []
  },
  maxUses: {
    type: Number,
    default: 5
  }
}, { _id: false });

// 团队游戏进度模式
const progressSchema = new Schema({
  startedAt: {
    type: Date,
    default: null
  },
  completedAt: {
    type: Date,
    default: null
  },
  currentObjective: {
    type: String,
    default: null
  },
  treasuresFound: {
    type: Number,
    default: 0
  },
  totalTreasures: {
    type: Number,
    default: 0
  },
  visitedLocations: {
    type: [String],
    default: []
  },
  specialEventsCompleted: {
    type: [String],
    default: []
  },
  hints: {
    used: {
      type: Number,
      default: 0
    },
    available: {
      type: Number,
      default: 3
    }
  }
}, { _id: false });

// 团队设置模式
const settingsSchema = new Schema({
  isPrivate: {
    type: Boolean,
    default: false
  },
  allowJoinRequests: {
    type: Boolean,
    default: true
  },
  maxPlayers: {
    type: Number,
    default: 5,
    min: 1,
    max: 10
  },
  difficulty: {
    type: String,
    enum: ['easy', 'medium', 'hard'],
    default: 'medium'
  },
  enableVoiceChat: {
    type: Boolean,
    default: true
  }
}, { _id: false });

// 主团队模式
const teamSchema = new Schema({
  name: {
    type: String,
    required: true,
    trim: true,
    maxlength: 30
  },
  code: {
    type: String,
    required: true,
    unique: true,
    default: () => shortid.generate().toUpperCase()
  },
  status: {
    type: String,
    enum: Object.values(TEAM_STATUS),
    default: TEAM_STATUS.WAITING
  },
  mazeId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Maze',
    required: true
  },
  seasonId: {
    type: String,
    default: null,
    index: true
  },
  players: {
    type: [playerStatusSchema],
    default: []
  },
  invitations: {
    type: [invitationSchema],
    default: []
  },
  progress: {
    type: progressSchema,
    default: () => ({})
  },
  settings: {
    type: settingsSchema,
    default: () => ({})
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
  collection: 'teams',
  timestamps: true,
  // 配置选择性索引
  collation: { locale: 'zh', strength: 2 }
});

// 索引
teamSchema.index({ code: 1 }, { unique: true });
teamSchema.index({ mazeId: 1 });
teamSchema.index({ status: 1 });
teamSchema.index({ 'players.userId': 1 });
teamSchema.index({ createdAt: -1 });
teamSchema.index({ updatedAt: -1 });
teamSchema.index({ mazeId: 1, status: 1 });
teamSchema.index({ mazeId: 1, status: 1, createdAt: -1 });
teamSchema.index({ 'players.userId': 1, status: 1 });
teamSchema.index({ 'invitations.code': 1 });

// 虚拟属性：团队规模
teamSchema.virtual('size').get(function() {
  return this.players.filter(player => player.isActive).length;
});

// 虚拟属性：团队领导者
teamSchema.virtual('leader').get(function() {
  return this.players.find(player => player.isLeader) || null;
});

// 虚拟属性：是否已满
teamSchema.virtual('isFull').get(function() {
  const activePlayers = this.players.filter(player => player.isActive).length;
  return activePlayers >= this.settings.maxPlayers;
});

// 虚拟属性：游戏时长(分钟)
teamSchema.virtual('duration').get(function() {
  if (!this.progress.startedAt) {
    return 0;
  }
  
  const endTime = this.progress.completedAt || new Date();
  const durationMs = endTime - this.progress.startedAt;
  return Math.round(durationMs / (1000 * 60));
});

// 方法：添加新玩家
teamSchema.methods.addPlayer = function(playerData) {
  const isFirstPlayer = this.players.length === 0;
  
  // 如果团队已满，则拒绝添加
  if (this.isFull) {
    throw new Error('团队已满');
  }
  
  // 检查用户是否已在团队中
  const existingPlayerIndex = this.players.findIndex(p => p.userId === playerData.userId);
  
  if (existingPlayerIndex >= 0) {
    // 如果用户存在但不活跃，则重新激活
    if (!this.players[existingPlayerIndex].isActive) {
      this.players[existingPlayerIndex].isActive = true;
      this.players[existingPlayerIndex].lastActivity = new Date();
      return this.players[existingPlayerIndex];
    }
    throw new Error('玩家已在团队中');
  }
  
  // 创建新玩家对象
  const newPlayer = {
    ...playerData,
    isLeader: isFirstPlayer, // 第一个加入的玩家成为队长
    joinedAt: new Date(),
    lastActivity: new Date(),
    isActive: true,
    treasuresFound: [],
    score: 0
  };
  
  // 添加到团队
  this.players.push(newPlayer);
  
  return newPlayer;
};

// 方法：移除玩家
teamSchema.methods.removePlayer = function(userId) {
  const playerIndex = this.players.findIndex(p => p.userId === userId);
  
  if (playerIndex < 0) {
    throw new Error('玩家不在团队中');
  }
  
  // 如果是队长，需要转移队长身份
  if (this.players[playerIndex].isLeader && this.players.length > 1) {
    // 找到第一个不是离开玩家的活跃玩家
    const newLeaderIndex = this.players.findIndex(p => p.userId !== userId && p.isActive);
    
    if (newLeaderIndex >= 0) {
      this.players[newLeaderIndex].isLeader = true;
    }
  }
  
  // 移除玩家
  this.players.splice(playerIndex, 1);
  
  // 如果没有玩家了，可以考虑自动解散团队
  if (this.players.length === 0) {
    this.status = TEAM_STATUS.DISBANDED;
  }
  
  return this;
};

// 方法：标记玩家为不活跃
teamSchema.methods.deactivatePlayer = function(userId) {
  const player = this.players.find(p => p.userId === userId);
  
  if (!player) {
    throw new Error('玩家不在团队中');
  }
  
  player.isActive = false;
  
  // 如果是队长且有其他活跃玩家，转移队长身份
  if (player.isLeader) {
    const activePlayer = this.players.find(p => p.userId !== userId && p.isActive);
    
    if (activePlayer) {
      player.isLeader = false;
      activePlayer.isLeader = true;
    }
  }
  
  return player;
};

// 方法：更新玩家位置
teamSchema.methods.updatePlayerPosition = function(userId, position) {
  const player = this.players.find(p => p.userId === userId);
  
  if (!player) {
    throw new Error('玩家不在团队中');
  }
  
  player.position = position;
  player.lastActivity = new Date();
  
  return player;
};

// 方法：记录玩家找到的宝藏
teamSchema.methods.recordTreasureFound = function(userId, treasureId) {
  const player = this.players.find(p => p.userId === userId);
  
  if (!player) {
    throw new Error('玩家不在团队中');
  }
  
  // 确保不重复添加
  if (!player.treasuresFound.includes(treasureId)) {
    player.treasuresFound.push(treasureId);
    player.score += 10; // 每个宝藏加10分
    
    // 更新团队进度
    this.progress.treasuresFound++;
  }
  
  return player;
};

// 方法：创建新邀请
teamSchema.methods.createInvitation = function(maxUses = 5, expiresInMinutes = 60) {
  const expiresAt = new Date();
  expiresAt.setMinutes(expiresAt.getMinutes() + expiresInMinutes);
  
  const invitation = {
    code: shortid.generate().toUpperCase(),
    createdAt: new Date(),
    expiresAt,
    usedBy: [],
    maxUses
  };
  
  this.invitations.push(invitation);
  
  return invitation;
};

// 方法：验证邀请码
teamSchema.methods.validateInvitation = function(code, userId) {
  // 清理过期邀请
  this.invitations = this.invitations.filter(inv => inv.expiresAt > new Date());
  
  const invitation = this.invitations.find(inv => inv.code === code);
  
  if (!invitation) {
    throw new Error('无效的邀请码');
  }
  
  if (invitation.expiresAt < new Date()) {
    throw new Error('邀请码已过期');
  }
  
  if (invitation.usedBy.length >= invitation.maxUses) {
    throw new Error('邀请码已达到最大使用次数');
  }
  
  // 标记此用户已使用此邀请码
  if (!invitation.usedBy.includes(userId)) {
    invitation.usedBy.push(userId);
  }
  
  return true;
};

// 方法：开始游戏
teamSchema.methods.startGame = function() {
  if (this.players.length === 0) {
    throw new Error('团队没有玩家');
  }
  
  if (this.status === TEAM_STATUS.IN_PROGRESS) {
    throw new Error('游戏已经开始');
  }
  
  this.status = TEAM_STATUS.IN_PROGRESS;
  this.progress.startedAt = new Date();
  
  return this;
};

// 方法：完成游戏
teamSchema.methods.completeGame = function() {
  if (this.status !== TEAM_STATUS.IN_PROGRESS) {
    throw new Error('游戏未在进行中');
  }
  
  this.status = TEAM_STATUS.COMPLETED;
  this.progress.completedAt = new Date();
  
  return this;
};

// 方法：使用提示
teamSchema.methods.useHint = function() {
  if (this.progress.hints.available <= 0) {
    throw new Error('没有可用的提示');
  }
  
  this.progress.hints.used++;
  this.progress.hints.available--;
  
  return this.progress.hints;
};

// 方法：获取团队排行榜数据
teamSchema.methods.getLeaderboardData = function() {
  return {
    id: this._id,
    name: this.name,
    players: this.players.length,
    score: this.players.reduce((sum, player) => sum + player.score, 0),
    treasuresFound: this.progress.treasuresFound,
    duration: this.duration,
    completedAt: this.progress.completedAt
  };
};

// 查询助手：获取活跃团队
teamSchema.statics.getActiveTeams = function(mazeId = null) {
  const query = { 
    status: { $in: [TEAM_STATUS.WAITING, TEAM_STATUS.IN_PROGRESS] }
  };
  
  if (mazeId) {
    query.mazeId = mazeId;
  }
  
  return this.find(query)
    .sort({ createdAt: -1 });
};

// 查询助手：通过邀请码查找团队
teamSchema.statics.findByInvitationCode = function(code) {
  return this.findOne({ 
    'invitations.code': code,
    status: { $in: [TEAM_STATUS.WAITING, TEAM_STATUS.IN_PROGRESS] }
  });
};

// 查询助手：获取用户的团队
teamSchema.statics.findByUserId = function(userId) {
  return this.find({ 
    'players.userId': userId,
    status: { $ne: TEAM_STATUS.DISBANDED }
  })
  .sort({ updatedAt: -1 });
};

// 查询助手：获取排行榜
teamSchema.statics.getLeaderboard = function(mazeId, limit = 10) {
  return this.find({
    mazeId: mazeId,
    status: TEAM_STATUS.COMPLETED,
    'progress.completedAt': { $ne: null }
  })
  .sort({ 'progress.treasuresFound': -1, duration: 1 })
  .limit(limit)
  .lean()
  .select('name players.name progress.treasuresFound progress.startedAt progress.completedAt');
};

// 中间件：保存前
teamSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  
  // 清理过期的邀请
  this.invitations = this.invitations.filter(inv => inv.expiresAt > new Date());
  
  next();
});

// 设置索引和缓冲策略
teamSchema.set('autoIndex', process.env.NODE_ENV !== 'production');
teamSchema.set('toJSON', {
  virtuals: true,
  transform: (doc, ret) => {
    delete ret.__v;
    return ret;
  }
});

module.exports = mongoose.model('Team', teamSchema);
