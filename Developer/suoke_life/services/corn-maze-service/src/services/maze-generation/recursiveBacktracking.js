/**
 * 递归回溯迷宫生成算法
 * 使用深度优先搜索方式生成完美迷宫（没有环路的迷宫）
 */
const { shuffleArray } = require('../../utils/arrayUtils');
const logger = require('../../utils/logger');

/**
 * 使用递归回溯算法生成迷宫
 * @param {Object} config - 迷宫配置
 * @returns {Object} 生成的迷宫结构
 */
const generateMaze = (config) => {
  const {
    width = 15,
    height = 15,
    seed = Date.now().toString(),
    corridorBias = 0.5, // 0: 倾向于水平走廊, 1: 倾向于垂直走廊
    branchingFactor = 0.75 // 分支因子，值越高分支越多
  } = config;
  
  // 确保尺寸为奇数，以便有墙壁和通道的正确分布
  const gridWidth = width % 2 === 0 ? width + 1 : width;
  const gridHeight = height % 2 === 0 ? height + 1 : height;
  
  // 初始化随机数生成器
  const random = seedRandom(seed);
  
  // 创建初始网格 (全墙)
  const grid = Array(gridHeight).fill().map(() => Array(gridWidth).fill(1));
  
  // 设置起点 (通常在左上角附近)
  const startX = 1;
  const startY = 1;
  grid[startY][startX] = 0; // 0 表示通道
  
  // 初始化已访问单元格
  const visited = new Set();
  visited.add(`${startX},${startY}`);
  
  // 方向数组: 上、右、下、左
  let dirs = [
    [0, -2], // 上
    [2, 0],  // 右
    [0, 2],  // 下
    [-2, 0]  // 左
  ];
  
  // 根据走廊偏好调整方向顺序的概率
  if (corridorBias !== 0.5) {
    // 根据bias调整方向排序，让垂直或水平通道更有可能先被选择
    const horizontalPriority = corridorBias < 0.5;
    
    if (horizontalPriority) {
      // 如果bias低，优先水平方向 (左和右)
      dirs = [[2, 0], [-2, 0], [0, -2], [0, 2]];
    } else {
      // 如果bias高，优先垂直方向 (上和下)
      dirs = [[0, -2], [0, 2], [2, 0], [-2, 0]];
    }
  }
  
  // 回溯堆栈
  const stack = [[startX, startY]];
  
  // 深度优先搜索生成迷宫
  while (stack.length > 0) {
    // 当前单元格
    const [x, y] = stack[stack.length - 1];
    
    // 获取随机打乱的方向列表
    const shuffledDirs = shuffleArray([...dirs], random);
    
    // 寻找未访问的邻居
    let found = false;
    
    for (const [dx, dy] of shuffledDirs) {
      const nx = x + dx;
      const ny = y + dy;
      
      // 检查边界
      if (nx < 1 || nx >= gridWidth - 1 || ny < 1 || ny >= gridHeight - 1) {
        continue;
      }
      
      // 检查是否已访问
      if (visited.has(`${nx},${ny}`)) {
        continue;
      }
      
      // 使用分支因子来决定是否继续
      if (random() > branchingFactor) {
        continue;
      }
      
      // 开通通道
      grid[y + dy/2][x + dx/2] = 0; // 中间的墙变成通道
      grid[ny][nx] = 0; // 目标单元格变成通道
      
      // 标记为已访问
      visited.add(`${nx},${ny}`);
      
      // 添加到堆栈
      stack.push([nx, ny]);
      found = true;
      break;
    }
    
    // 如果没有找到未访问的邻居，回溯
    if (!found) {
      stack.pop();
    }
  }
  
  // 设置终点 (通常在右下角附近)
  const endX = gridWidth - 2;
  const endY = gridHeight - 2;
  grid[endY][endX] = 0;
  
  // 确保起点和终点周围是开放的
  ensureOpenArea(grid, startX, startY);
  ensureOpenArea(grid, endX, endY);
  
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
 * 确保指定点周围是开放的区域
 * @param {Array<Array<number>>} grid - 迷宫网格
 * @param {number} x - X坐标
 * @param {number} y - Y坐标
 */
const ensureOpenArea = (grid, x, y) => {
  const height = grid.length;
  const width = grid[0].length;
  
  // 检查周围的8个相邻单元格
  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      const nx = x + dx;
      const ny = y + dy;
      
      // 确保在边界内
      if (nx >= 1 && nx < width - 1 && ny >= 1 && ny < height - 1) {
        // 有50%的几率将墙变成通道
        if (grid[ny][nx] === 1 && Math.random() > 0.5) {
          grid[ny][nx] = 0;
        }
      }
    }
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