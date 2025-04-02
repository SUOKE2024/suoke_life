/**
 * 迷宫数据模型
 */
const mongoose = require('mongoose');
const { MAZE_DIFFICULTY } = require('../utils/constants');

// 迷宫元素坐标schema
const positionSchema = new mongoose.Schema({
  x: { type: Number, required: true },
  y: { type: Number, required: true }
}, { _id: false });

// 宝藏位置schema
const treasurePositionSchema = new mongoose.Schema({
  x: { type: Number, required: true },
  y: { type: Number, required: true },
  treasureId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Treasure',
    required: false
  },
  collected: {
    type: Boolean,
    default: false
  },
  collectedBy: [{
    userId: { type: String },
    timestamp: { type: Date, default: Date.now }
  }]
}, { _id: false });

// 迷宫生成配置schema
const generationConfigSchema = new mongoose.Schema({
  algorithm: {
    type: String,
    enum: ['recursive_backtracking', 'kruskal', 'prim', 'eller', 'binary_tree', 'hunt_and_kill'],
    default: 'recursive_backtracking'
  },
  corridorBias: {
    type: Number,
    min: 0,
    max: 1,
    default: 0.5
  },
  branchingFactor: {
    type: Number,
    min: 0,
    max: 1,
    default: 0.75
  },
  deadEndRemovalRate: {
    type: Number,
    min: 0,
    max: 1,
    default: 0.2
  },
  extraConnections: {
    type: Number,
    min: 0,
    default: 0
  },
  seed: {
    type: String
  },
  minPathLength: {
    type: Number,
    min: 5,
    default: 10
  }
}, { _id: false });

const mazeSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true,
    index: true
  },
  description: {
    type: String,
    required: false,
    trim: true
  },
  difficulty: {
    type: Number,
    required: true,
    enum: Object.values(MAZE_DIFFICULTY),
    default: MAZE_DIFFICULTY.MEDIUM,
    index: true
  },
  width: {
    type: Number,
    required: true,
    min: 5,
    max: 100
  },
  height: {
    type: Number,
    required: true,
    min: 5,
    max: 100
  },
  grid: {
    type: [[Number]],
    required: true
  },
  // 轻量级网格数据 - 用于快速传输
  compressedGrid: {
    type: String
  },
  startPosition: {
    type: positionSchema,
    required: true
  },
  endPosition: {
    type: positionSchema,
    required: true
  },
  treasurePositions: [treasurePositionSchema],
  // 障碍物位置
  obstaclePositions: [positionSchema],
  // 特殊区域
  specialZones: [{
    type: { type: String, required: true },
    position: positionSchema,
    radius: { type: Number, default: 1 },
    effects: [String],
    metadata: { type: mongoose.Schema.Types.Mixed }
  }],
  isActive: {
    type: Boolean,
    default: true,
    index: true
  },
  seasonId: {
    type: String,
    required: true,
    index: true
  },
  // 生成配置
  generationConfig: {
    type: generationConfigSchema,
    default: () => ({})
  },
  // 迷宫解决的最短路径长度
  shortestPathLength: {
    type: Number,
    min: 0
  },
  // 可用的入口点
  entrances: [positionSchema],
  // 迷宫主题
  theme: {
    type: String,
    default: 'default'
  },
  // 访问统计
  stats: {
    totalVisits: { type: Number, default: 0 },
    completionCount: { type: Number, default: 0 },
    averageCompletionTime: { type: Number, default: 0 },
    treasuresCollected: { type: Number, default: 0 }
  },
  // 版本和修订控制
  version: {
    type: Number,
    default: 1
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  updatedAt: {
    type: Date,
    default: Date.now,
    index: true
  }
}, {
  timestamps: { createdAt: 'createdAt', updatedAt: 'updatedAt' },
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// 索引
mazeSchema.index({ name: 1 });
mazeSchema.index({ difficulty: 1 });
mazeSchema.index({ isActive: 1 });
mazeSchema.index({ seasonId: 1 });
mazeSchema.index({ isActive: 1, difficulty: 1 });
mazeSchema.index({ isActive: 1, seasonId: 1 });
mazeSchema.index({ isActive: 1, difficulty: 1, seasonId: 1 });
mazeSchema.index({ 'treasurePositions.treasureId': 1 });
mazeSchema.index({ createdAt: -1 });
mazeSchema.index({ updatedAt: -1 });

// 虚拟字段 - 宝藏数量
mazeSchema.virtual('treasureCount').get(function() {
  return this.treasurePositions ? this.treasurePositions.length : 0;
});

// 虚拟字段 - 难度描述
mazeSchema.virtual('difficultyText').get(function() {
  const difficultyMap = {
    1: '简单',
    2: '中等',
    3: '困难',
    4: '专家',
    5: '大师'
  };
  return difficultyMap[this.difficulty] || '未知';
});

// 虚拟字段 - 与其他集合的关系
mazeSchema.virtual('activeTeams', {
  ref: 'Team',
  localField: '_id',
  foreignField: 'currentMazeId',
  options: { match: { isActive: true } },
  count: true
});

/**
 * 创建压缩的网格表示
 * @return {String} 压缩后的网格字符串
 */
mazeSchema.methods.createCompressedGrid = function() {
  // 使用行程编码 (RLE) 压缩网格
  if (!this.grid || !this.grid.length) return '';
  
  const flatGrid = this.grid.flat();
  let compressed = '';
  let count = 1;
  let current = flatGrid[0];
  
  for (let i = 1; i < flatGrid.length; i++) {
    if (flatGrid[i] === current) {
      count++;
    } else {
      compressed += `${count}${current}`;
      current = flatGrid[i];
      count = 1;
    }
  }
  
  compressed += `${count}${current}`;
  return compressed;
};

/**
 * 解压缩网格数据
 * @param {String} compressed - 压缩的网格字符串
 * @return {Array} 解压后的网格数组
 */
mazeSchema.statics.decompressGrid = function(compressed, width, height) {
  if (!compressed || !width || !height) return null;
  
  const flatGrid = [];
  let i = 0;
  
  while (i < compressed.length) {
    let countStr = '';
    
    // 读取计数部分
    while (i < compressed.length && !isNaN(parseInt(compressed[i]))) {
      countStr += compressed[i];
      i++;
    }
    
    // 读取值部分
    const value = parseInt(compressed[i]);
    const count = parseInt(countStr);
    
    // 添加到展平的网格
    for (let j = 0; j < count; j++) {
      flatGrid.push(value);
    }
    
    i++;
  }
  
  // 将展平的网格重构为二维数组
  const grid = [];
  for (let y = 0; y < height; y++) {
    const row = [];
    for (let x = 0; x < width; x++) {
      row.push(flatGrid[y * width + x]);
    }
    grid.push(row);
  }
  
  return grid;
};

/**
 * 检查迷宫是否有效
 * @returns {Boolean} 是否有效
 */
mazeSchema.methods.isValid = function() {
  // 检查起点和终点是否在网格范围内
  if (this.startPosition.x < 0 || this.startPosition.x >= this.width ||
      this.startPosition.y < 0 || this.startPosition.y >= this.height ||
      this.endPosition.x < 0 || this.endPosition.x >= this.width ||
      this.endPosition.y < 0 || this.endPosition.y >= this.height) {
    return false;
  }
  
  // 检查起点和终点是否为通道单元
  if (this.grid[this.startPosition.y][this.startPosition.x] !== 0 ||
      this.grid[this.endPosition.y][this.endPosition.x] !== 0) {
    return false;
  }
  
  // 检查路径可达性（可以有多种实现方式，下面是简化版）
  // 使用广度优先搜索验证起点和终点是否连通
  return this.isPathExists(this.startPosition, this.endPosition);
};

/**
 * 检查两点之间是否存在路径
 * @param {Object} start - 起点坐标
 * @param {Object} end - 终点坐标
 * @returns {Boolean} 是否存在路径
 */
mazeSchema.methods.isPathExists = function(start, end) {
  // 广度优先搜索
  const queue = [{ x: start.x, y: start.y }];
  const visited = Array(this.height).fill().map(() => Array(this.width).fill(false));
  visited[start.y][start.x] = true;
  
  // 移动方向：上、右、下、左
  const directions = [
    { x: 0, y: -1 },
    { x: 1, y: 0 },
    { x: 0, y: 1 },
    { x: -1, y: 0 }
  ];
  
  while (queue.length > 0) {
    const current = queue.shift();
    
    // 到达终点
    if (current.x === end.x && current.y === end.y) {
      return true;
    }
    
    // 探索四个方向
    for (const dir of directions) {
      const newX = current.x + dir.x;
      const newY = current.y + dir.y;
      
      // 检查边界
      if (newX < 0 || newX >= this.width || newY < 0 || newY >= this.height) {
        continue;
      }
      
      // 检查是否是通道且未访问过
      if (this.grid[newY][newX] === 0 && !visited[newY][newX]) {
        visited[newY][newX] = true;
        queue.push({ x: newX, y: newY });
      }
    }
  }
  
  // 未找到路径
  return false;
};

/**
 * 添加宝藏
 * @param {Number} x - X坐标
 * @param {Number} y - Y坐标
 * @param {String} treasureId - 宝藏ID
 */
mazeSchema.methods.addTreasure = function(x, y, treasureId) {
  // 检查坐标是否有效
  if (x < 0 || x >= this.width || y < 0 || y >= this.height) {
    throw new Error('无效的宝藏坐标');
  }
  
  // 检查位置是否已经有宝藏
  const existingTreasure = this.treasurePositions.find(
    t => t.x === x && t.y === y
  );
  
  if (existingTreasure) {
    throw new Error('该位置已存在宝藏');
  }
  
  // 检查格子是否是通道
  if (this.grid[y][x] !== 0) {
    throw new Error('宝藏只能放置在通道上');
  }
  
  // 添加宝藏
  this.treasurePositions.push({
    x,
    y,
    treasureId
  });
};

/**
 * 在保存前处理
 */
mazeSchema.pre('save', function(next) {
  // 创建压缩网格
  if (this.isModified('grid')) {
    this.compressedGrid = this.createCompressedGrid();
    
    // 计算最短路径长度
    // 这里可以实现一个A*或Dijkstra算法
    // 简化版: 使用曼哈顿距离作为启发式估计
    this.shortestPathLength = Math.abs(this.endPosition.x - this.startPosition.x) +
                            Math.abs(this.endPosition.y - this.startPosition.y);
  }
  
  next();
});

/**
 * 添加统计方法
 */
mazeSchema.methods.incrementVisits = function() {
  this.stats.totalVisits += 1;
  return this.save();
};

mazeSchema.methods.recordCompletion = function(completionTime) {
  this.stats.completionCount += 1;
  
  // 更新平均完成时间
  const currentTotal = this.stats.averageCompletionTime * (this.stats.completionCount - 1);
  this.stats.averageCompletionTime = (currentTotal + completionTime) / this.stats.completionCount;
  
  return this.save();
};

mazeSchema.methods.recordTreasureCollection = function(count = 1) {
  this.stats.treasuresCollected += count;
  return this.save();
};

// 创建索引时的选项
mazeSchema.set('autoIndex', process.env.NODE_ENV !== 'production');

const Maze = mongoose.model('Maze', mazeSchema);

module.exports = Maze;
