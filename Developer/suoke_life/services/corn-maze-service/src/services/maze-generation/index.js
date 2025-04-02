/**
 * 迷宫生成算法索引
 * 提供不同的迷宫生成算法及相关工具
 */
const recursiveBacktracking = require('./recursiveBacktracking');
const kruskal = require('./kruskal');
const logger = require('../../utils/logger');

// 支持的迷宫生成算法
const ALGORITHMS = {
  RECURSIVE_BACKTRACKING: 'recursive_backtracking',
  KRUSKAL: 'kruskal',
  // 以下算法将在后续实现
  PRIM: 'prim',
  ELLER: 'eller',
  BINARY_TREE: 'binary_tree',
  HUNT_AND_KILL: 'hunt_and_kill',
  GROWING_TREE: 'growing_tree',
  CELLULAR_AUTOMATON: 'cellular_automaton'
};

/**
 * 使用指定算法生成迷宫
 * @param {Object} config - 迷宫配置
 * @returns {Object} 生成的迷宫结构
 */
const generateMaze = (config) => {
  const { algorithm = ALGORITHMS.RECURSIVE_BACKTRACKING } = config;
  
  logger.info(`使用 ${algorithm} 算法生成迷宫`);
  
  switch (algorithm.toLowerCase()) {
    case ALGORITHMS.RECURSIVE_BACKTRACKING:
      return recursiveBacktracking.generateMaze(config);
    case ALGORITHMS.KRUSKAL:
      return kruskal.generateMaze(config);
    // 其他算法将在后续实现
    default:
      logger.warn(`未知的迷宫生成算法: ${algorithm}，使用递归回溯算法代替`);
      return recursiveBacktracking.generateMaze(config);
  }
};

/**
 * 分析迷宫复杂度
 * @param {Array<Array<number>>} grid - 迷宫网格
 * @returns {Object} 复杂度分析结果
 */
const analyzeMazeComplexity = (grid) => {
  const height = grid.length;
  const width = grid[0].length;
  
  // 计算总单元格数
  const totalCells = width * height;
  
  // 计算通道单元格数
  let pathCells = 0;
  let deadEnds = 0;
  let junctions = 0;
  
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      if (grid[y][x] === 0) { // 通道
        pathCells++;
        
        // 计算相邻通道数
        let openNeighbors = 0;
        if (grid[y-1][x] === 0) openNeighbors++;
        if (grid[y+1][x] === 0) openNeighbors++;
        if (grid[y][x-1] === 0) openNeighbors++;
        if (grid[y][x+1] === 0) openNeighbors++;
        
        // 判断死胡同和交叉点
        if (openNeighbors === 1) {
          deadEnds++;
        } else if (openNeighbors > 2) {
          junctions++;
        }
      }
    }
  }
  
  // 计算各种指标
  const wallCells = totalCells - pathCells;
  const deadEndRatio = deadEnds / pathCells;
  const junctionRatio = junctions / pathCells;
  const openness = pathCells / totalCells;
  
  // 估算复杂度等级 (1-5)
  const complexityScore = Math.min(5, Math.max(1, Math.round(
    1 + (deadEndRatio * 2) + (junctionRatio * 3) - (openness * 2)
  )));
  
  return {
    totalCells,
    pathCells,
    wallCells,
    deadEnds,
    junctions,
    deadEndRatio,
    junctionRatio,
    openness,
    complexityScore
  };
};

/**
 * 找到迷宫的最短路径
 * @param {Array<Array<number>>} grid - 迷宫网格
 * @param {Object} start - 起点坐标 {x, y}
 * @param {Object} end - 终点坐标 {x, y}
 * @returns {Array<Object>|null} 最短路径坐标数组或null(无路径)
 */
const findShortestPath = (grid, start, end) => {
  const height = grid.length;
  const width = grid[0].length;
  
  // 使用广度优先搜索
  const queue = [{ x: start.x, y: start.y, path: [{ x: start.x, y: start.y }] }];
  const visited = Array(height).fill().map(() => Array(width).fill(false));
  visited[start.y][start.x] = true;
  
  // 方向数组: 上、右、下、左
  const dirs = [
    [0, -1], // 上
    [1, 0],  // 右
    [0, 1],  // 下
    [-1, 0]  // 左
  ];
  
  while (queue.length > 0) {
    const { x, y, path } = queue.shift();
    
    // 到达终点
    if (x === end.x && y === end.y) {
      return path;
    }
    
    // 探索四个方向
    for (const [dx, dy] of dirs) {
      const nx = x + dx;
      const ny = y + dy;
      
      // 检查边界
      if (nx < 0 || nx >= width || ny < 0 || ny >= height) {
        continue;
      }
      
      // 检查是否是通道且未访问过
      if (grid[ny][nx] === 0 && !visited[ny][nx]) {
        visited[ny][nx] = true;
        const newPath = [...path, { x: nx, y: ny }];
        queue.push({ x: nx, y: ny, path: newPath });
      }
    }
  }
  
  // 无法到达终点
  return null;
};

/**
 * 消除迷宫的死胡同
 * @param {Array<Array<number>>} grid - 迷宫网格
 * @param {number} removalRate - 消除率 (0-1)
 * @returns {Array<Array<number>>} 处理后的迷宫网格
 */
const removeDeadEnds = (grid, removalRate = 0.3) => {
  const height = grid.length;
  const width = grid[0].length;
  
  // 复制网格，避免修改原始数据
  const newGrid = [];
  for (let y = 0; y < height; y++) {
    newGrid[y] = [...grid[y]];
  }
  
  // 查找死胡同
  const deadEnds = [];
  
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      if (newGrid[y][x] === 0) { // 通道
        // 计算相邻通道数
        let openNeighbors = 0;
        let wallDirs = [];
        
        if (newGrid[y-1][x] === 0) openNeighbors++;
        else wallDirs.push([0, -1]);
        
        if (newGrid[y+1][x] === 0) openNeighbors++;
        else wallDirs.push([0, 1]);
        
        if (newGrid[y][x-1] === 0) openNeighbors++;
        else wallDirs.push([-1, 0]);
        
        if (newGrid[y][x+1] === 0) openNeighbors++;
        else wallDirs.push([1, 0]);
        
        // 判断死胡同
        if (openNeighbors === 1) {
          deadEnds.push({ x, y, wallDirs });
        }
      }
    }
  }
  
  // 随机消除一些死胡同
  const numToRemove = Math.floor(deadEnds.length * removalRate);
  const shuffledDeadEnds = deadEnds.sort(() => Math.random() - 0.5);
  
  for (let i = 0; i < numToRemove && i < shuffledDeadEnds.length; i++) {
    const { x, y, wallDirs } = shuffledDeadEnds[i];
    const [dx, dy] = wallDirs[Math.floor(Math.random() * wallDirs.length)];
    
    // 确保不破坏外墙
    const nx = x + dx;
    const ny = y + dy;
    if (nx > 0 && nx < width - 1 && ny > 0 && ny < height - 1) {
      newGrid[ny][nx] = 0; // 打通墙，消除死胡同
    }
  }
  
  return newGrid;
};

module.exports = {
  ALGORITHMS,
  generateMaze,
  analyzeMazeComplexity,
  findShortestPath,
  removeDeadEnds
}; 