/**
 * 克鲁斯卡尔算法迷宫生成
 * 使用最小生成树算法生成迷宫，通过随机打乱边来生成迷宫结构
 */
const { shuffleArray } = require('../../utils/arrayUtils');
const logger = require('../../utils/logger');

/**
 * 使用克鲁斯卡尔算法生成迷宫
 * @param {Object} config - 迷宫配置
 * @returns {Object} 生成的迷宫结构
 */
const generateMaze = (config) => {
  const {
    width = 15,
    height = 15,
    seed = Date.now().toString(),
    extraConnections = 0 // 添加额外连接，使迷宫更加开放
  } = config;
  
  // 确保尺寸为奇数
  const gridWidth = width % 2 === 0 ? width + 1 : width;
  const gridHeight = height % 2 === 0 ? height + 1 : height;
  
  // 初始化随机数生成器
  const random = seedRandom(seed);
  
  // 创建初始网格 (全墙)
  const grid = Array(gridHeight).fill().map(() => Array(gridWidth).fill(1));
  
  // 为克鲁斯卡尔算法准备数据
  // 我们只在奇数坐标上建立单元格并连接它们
  const cellWidth = Math.floor(gridWidth / 2);
  const cellHeight = Math.floor(gridHeight / 2);
  
  // 初始化单元格集合 (每个单元格一开始属于自己的集合)
  const cellSets = new Map();
  
  // 为每个单元格创建集合
  for (let y = 0; y < cellHeight; y++) {
    for (let x = 0; x < cellWidth; x++) {
      const cellId = y * cellWidth + x;
      cellSets.set(cellId, new Set([cellId]));
      
      // 在网格中创建对应的通道
      const gridX = x * 2 + 1;
      const gridY = y * 2 + 1;
      grid[gridY][gridX] = 0; // 0 表示通道
    }
  }
  
  // 创建边列表 (边连接相邻单元格)
  const edges = [];
  
  // 添加水平边
  for (let y = 0; y < cellHeight; y++) {
    for (let x = 0; x < cellWidth - 1; x++) {
      const cell1 = y * cellWidth + x;
      const cell2 = y * cellWidth + (x + 1);
      edges.push({
        cell1,
        cell2,
        gridX: x * 2 + 2, // 连接两个单元格的墙的网格坐标
        gridY: y * 2 + 1
      });
    }
  }
  
  // 添加垂直边
  for (let y = 0; y < cellHeight - 1; y++) {
    for (let x = 0; x < cellWidth; x++) {
      const cell1 = y * cellWidth + x;
      const cell2 = (y + 1) * cellWidth + x;
      edges.push({
        cell1,
        cell2,
        gridX: x * 2 + 1,
        gridY: y * 2 + 2
      });
    }
  }
  
  // 随机打乱边列表
  const shuffledEdges = shuffleArray(edges, random);
  
  // 实现克鲁斯卡尔算法
  shuffledEdges.forEach(edge => {
    const { cell1, cell2, gridX, gridY } = edge;
    
    // 获取两个单元格的集合
    const set1 = findSet(cellSets, cell1);
    const set2 = findSet(cellSets, cell2);
    
    // 如果两个单元格不在同一个集合中，则连接它们
    if (set1 !== set2) {
      // 移除墙壁，创建通道
      grid[gridY][gridX] = 0;
      
      // 合并集合
      mergeSets(cellSets, cell1, cell2);
    }
  });
  
  // 添加额外的连接 (如果需要)
  if (extraConnections > 0) {
    // 找出所有可以打通的墙
    const potentialWalls = [];
    
    // 只考虑内部墙 (非边界)
    for (let y = 1; y < gridHeight - 1; y++) {
      for (let x = 1; x < gridWidth - 1; x++) {
        // 只处理墙
        if (grid[y][x] === 1) {
          // 检查是否是可以打通的墙 (两侧都是通道)
          if ((grid[y-1][x] === 0 && grid[y+1][x] === 0) || 
              (grid[y][x-1] === 0 && grid[y][x+1] === 0)) {
            potentialWalls.push({ x, y });
          }
        }
      }
    }
    
    // 随机打通一些墙
    const wallsToRemove = Math.min(extraConnections, potentialWalls.length);
    const shuffledWalls = shuffleArray(potentialWalls, random);
    
    for (let i = 0; i < wallsToRemove; i++) {
      const { x, y } = shuffledWalls[i];
      grid[y][x] = 0;
    }
  }
  
  // 设置起点和终点
  const startX = 1;
  const startY = 1;
  const endX = gridWidth - 2;
  const endY = gridHeight - 2;
  
  // 确保起点和终点是通道
  grid[startY][startX] = 0;
  grid[endY][endX] = 0;
  
  // 返回生成的迷宫
  return {
    grid,
    width: gridWidth,
    height: gridHeight,
    startPosition: { x: startX, y: startY },
    endPosition: { x: endX, y: endY }
  };
};

/**
 * 查找单元格所属的集合
 * @param {Map} cellSets - 单元格集合映射
 * @param {number} cellId - 单元格ID
 * @returns {Set} 单元格所属的集合
 */
const findSet = (cellSets, cellId) => {
  for (const [_, set] of cellSets.entries()) {
    if (set.has(cellId)) {
      return set;
    }
  }
  return null;
};

/**
 * 合并两个单元格的集合
 * @param {Map} cellSets - 单元格集合映射
 * @param {number} cell1 - 第一个单元格ID
 * @param {number} cell2 - 第二个单元格ID
 */
const mergeSets = (cellSets, cell1, cell2) => {
  const set1 = findSet(cellSets, cell1);
  const set2 = findSet(cellSets, cell2);
  
  if (set1 === set2) return;
  
  // 合并集合
  const mergedSet = new Set([...set1, ...set2]);
  
  // 更新所有包含在合并集合中的单元格
  for (const cellId of mergedSet) {
    cellSets.set(cellId, mergedSet);
  }
};

/**
 * 创建一个基于种子的伪随机数生成器
 * @param {string} seed - 随机种子
 * @returns {Function} 随机数生成函数
 */
const seedRandom = (seed) => {
  // 简单的伪随机数生成器
  let s = hash(seed);
  
  return function() {
    s = Math.sin(s) * 10000;
    return s - Math.floor(s);
  };
};

/**
 * 简单的字符串哈希函数
 * @param {string} str - 要哈希的字符串
 * @returns {number} 哈希值
 */
const hash = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // 转换为32位整数
  }
  return hash;
};

module.exports = {
  generateMaze
}; 