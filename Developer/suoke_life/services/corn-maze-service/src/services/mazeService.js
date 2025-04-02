/**
 * 迷宫服务
 * 提供迷宫生成、管理和查询功能
 */
const Maze = require('../models/maze.model');
const { createError } = require('../middlewares/errorHandler');
const logger = require('../utils/logger');
const { MAZE_DIFFICULTY } = require('../utils/constants');
const { getRedisClient } = require('../config/redis');
const mazeGenerator = require('./maze-generation');

// 缓存配置
const CACHE_TTL = {
  LIST: 300, // 列表缓存5分钟
  DETAIL: 600, // 详情缓存10分钟
  STATS: 60 // 统计数据缓存1分钟
};

/**
 * 尝试从缓存获取数据
 * @param {String} key - 缓存键
 * @returns {Promise<Object|null>} 缓存数据或null
 */
const getFromCache = async (key) => {
  try {
    const redisClient = getRedisClient();
    const cachedData = await redisClient.get(key);
    
    if (cachedData) {
      logger.debug(`从缓存获取: ${key}`);
      return JSON.parse(cachedData);
    }
    return null;
  } catch (error) {
    logger.warn(`缓存获取失败: ${key}`, error);
    return null;
  }
};

/**
 * 将数据存入缓存
 * @param {String} key - 缓存键
 * @param {Object} data - 要缓存的数据
 * @param {Number} ttl - 缓存有效期(秒)
 * @returns {Promise<Boolean>} 是否成功
 */
const saveToCache = async (key, data, ttl) => {
  try {
    const redisClient = getRedisClient();
    await redisClient.set(key, JSON.stringify(data));
    await redisClient.expire(key, ttl);
    logger.debug(`数据已缓存: ${key}, TTL: ${ttl}秒`);
    return true;
  } catch (error) {
    logger.warn(`缓存保存失败: ${key}`, error);
    return false;
  }
};

/**
 * 从缓存删除数据
 * @param {String} key - 缓存键
 * @returns {Promise<Boolean>} 是否成功
 */
const removeFromCache = async (key) => {
  try {
    const redisClient = getRedisClient();
    await redisClient.del(key);
    logger.debug(`缓存已删除: ${key}`);
    return true;
  } catch (error) {
    logger.warn(`缓存删除失败: ${key}`, error);
    return false;
  }
};

/**
 * 清理迷宫相关的所有缓存
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Boolean>} 是否成功
 */
const clearMazeCache = async (mazeId) => {
  try {
    const redisClient = getRedisClient();
    const keys = await redisClient.keys(`maze:*:${mazeId}`);
    
    if (keys.length > 0) {
      await redisClient.del(keys);
      logger.info(`清理迷宫缓存: ${mazeId}, 共${keys.length}个键`);
    }
    
    // 同时清理列表缓存
    const listKeys = await redisClient.keys('maze:list:*');
    if (listKeys.length > 0) {
      await redisClient.del(listKeys);
      logger.info(`清理迷宫列表缓存: 共${listKeys.length}个键`);
    }
    
    return true;
  } catch (error) {
    logger.warn(`清理迷宫缓存失败: ${mazeId}`, error);
    return false;
  }
};

/**
 * 创建新迷宫
 * @param {Object} mazeData - 迷宫数据
 * @returns {Promise<Object>} 创建的迷宫
 */
const createMaze = async (mazeData) => {
  try {
    // 如果没有提供网格数据，则自动生成
    if (!mazeData.grid) {
      const { width, height, difficulty, generationConfig } = mazeData;
      
      // 根据难度配置生成迷宫参数
      const genConfig = {
        width,
        height,
        ...generationConfig
      };
      
      // 根据难度调整生成参数
      if (difficulty) {
        genConfig.difficultyLevel = difficulty;
        
        // 根据难度调整参数
        switch (difficulty) {
          case MAZE_DIFFICULTY.EASY:
            genConfig.deadEndRemovalRate = 0.6; // 大量移除死胡同
            genConfig.extraConnections = Math.ceil(width * height * 0.05); // 增加额外连接
            break;
          case MAZE_DIFFICULTY.HARD:
            genConfig.deadEndRemovalRate = 0.05; // 保留更多死胡同
            genConfig.branchingFactor = 0.9; // 增加分支
            break;
          case MAZE_DIFFICULTY.EXPERT:
            genConfig.deadEndRemovalRate = 0; // 不移除死胡同
            genConfig.branchingFactor = 1.0; // 最大分支
            genConfig.corridorBias = 0.75; // 更多垂直走廊
            break;
        }
      }
      
      // 生成迷宫结构
      const mazeStructure = mazeGenerator.generateMaze(genConfig);
      
      // 如果配置了死胡同移除率，处理死胡同
      if (genConfig.deadEndRemovalRate > 0) {
        mazeStructure.grid = mazeGenerator.removeDeadEnds(
          mazeStructure.grid,
          genConfig.deadEndRemovalRate
        );
      }
      
      // 计算最短路径
      const shortestPath = mazeGenerator.findShortestPath(
        mazeStructure.grid, 
        mazeStructure.startPosition, 
        mazeStructure.endPosition
      );
      
      // 分析迷宫复杂度
      const complexity = mazeGenerator.analyzeMazeComplexity(mazeStructure.grid);
      
      // 合并生成的数据
      Object.assign(mazeData, {
        grid: mazeStructure.grid,
        width: mazeStructure.width,
        height: mazeStructure.height,
        startPosition: mazeStructure.startPosition,
        endPosition: mazeStructure.endPosition,
        shortestPathLength: shortestPath ? shortestPath.length : 0,
        generationConfig: {
          ...mazeData.generationConfig,
          algorithm: genConfig.algorithm,
          complexity: complexity.complexityScore
        }
      });
    }
    
    // 创建新迷宫
    const maze = new Maze(mazeData);
    
    // 检查迷宫有效性
    if (!maze.isValid()) {
      throw createError('迷宫结构无效，请检查起点和终点设置', 400);
    }
    
    // 保存迷宫
    await maze.save();
    
    logger.info(`迷宫创建成功: ${maze._id}`);
    return maze;
  } catch (error) {
    logger.error('创建迷宫失败:', error);
    
    if (error.name === 'ValidationError') {
      const messages = Object.values(error.errors).map(err => err.message);
      throw createError(`迷宫数据验证失败: ${messages.join(', ')}`, 400);
    }
    
    throw createError('创建迷宫失败', 400);
  }
};

/**
 * 获取所有迷宫
 * @param {Object} filter - 过滤条件
 * @param {Object} options - 查询选项
 * @returns {Promise<Array>} 迷宫列表
 */
const getAllMazes = async (filter = {}, options = {}) => {
  try {
    const { 
      page = 1, 
      limit = 10, 
      sort = { createdAt: -1 },
      lean = true,
      projection = null,
      populate = null,
      useCache = true
    } = options;
    
    const skip = (page - 1) * limit;
    
    // 创建缓存键
    const cacheKey = useCache ? 
      `maze:list:${JSON.stringify(filter)}:${page}:${limit}:${JSON.stringify(sort)}:${projection ? JSON.stringify(projection) : 'all'}` :
      null;
    
    // 尝试从缓存获取
    if (cacheKey) {
      const cachedResult = await getFromCache(cacheKey);
      if (cachedResult) {
        return cachedResult;
      }
    }
    
    // 构建查询
    let query = Maze.find(filter);
    
    // 添加投影
    if (projection) {
      query = query.select(projection);
    }
    
    // 添加排序
    query = query.sort(sort);
    
    // 添加分页
    query = query.skip(skip).limit(limit);
    
    // 添加填充
    if (populate) {
      query = query.populate(populate);
    }
    
    // 是否使用精简模式
    if (lean) {
      query = query.lean();
    }
    
    // 执行查询
    const startTime = Date.now();
    const [mazes, total] = await Promise.all([
      query.exec(),
      Maze.countDocuments(filter)
    ]);
    const queryTime = Date.now() - startTime;
    
    logger.debug(`迷宫查询执行时间: ${queryTime}ms, 结果数: ${mazes.length}`);
    
    // 构建结果
    const result = {
      mazes,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      },
      queryTime
    };
    
    // 缓存结果
    if (cacheKey) {
      await saveToCache(cacheKey, result, CACHE_TTL.LIST);
    }
    
    return result;
  } catch (error) {
    logger.error('获取迷宫列表失败:', error);
    throw createError('获取迷宫列表失败', 500);
  }
};

/**
 * 通过ID获取迷宫
 * @param {String} id - 迷宫ID
 * @param {Object} options - 查询选项
 * @returns {Promise<Object>} 迷宫
 */
const getMazeById = async (id, options = {}) => {
  try {
    const { 
      lean = true, 
      projection = null, 
      populate = null,
      includeTreasures = false,
      useCache = true
    } = options;
    
    // 创建缓存键
    const cacheKey = useCache ? 
      `maze:detail:${id}:${projection ? JSON.stringify(projection) : 'all'}:${includeTreasures}` :
      null;
    
    // 尝试从缓存获取
    if (cacheKey) {
      const cachedMaze = await getFromCache(cacheKey);
      if (cachedMaze) {
        return cachedMaze;
      }
    }
    
    // 构建查询
    let query = Maze.findById(id);
    
    // 添加投影
    if (projection) {
      query = query.select(projection);
    }
    
    // 添加填充
    if (populate) {
      query = query.populate(populate);
    }
    
    // 填充宝藏信息
    if (includeTreasures) {
      query = query.populate('treasurePositions.treasureId');
    }
    
    // 是否使用精简模式
    if (lean) {
      query = query.lean();
    }
    
    // 执行查询
    const startTime = Date.now();
    const maze = await query.exec();
    const queryTime = Date.now() - startTime;
    
    if (!maze) {
      throw createError('迷宫不存在', 404);
    }
    
    logger.debug(`迷宫详情查询执行时间: ${queryTime}ms, ID: ${id}`);
    
    // 添加性能指标
    const result = {
      ...maze,
      _queryTime: queryTime
    };
    
    // 缓存结果
    if (cacheKey) {
      await saveToCache(cacheKey, result, CACHE_TTL.DETAIL);
    }
    
    return result;
  } catch (error) {
    logger.error(`获取迷宫ID:${id}失败:`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('获取迷宫详情失败', 500);
  }
};

/**
 * 更新迷宫
 * @param {String} id - 迷宫ID
 * @param {Object} updateData - 更新数据
 * @returns {Promise<Object>} 更新后的迷宫
 */
const updateMaze = async (id, updateData) => {
  try {
    // 获取迷宫
    const maze = await Maze.findById(id);
    
    if (!maze) {
      throw createError('迷宫不存在', 404);
    }
    
    // 更新可修改的字段
    Object.keys(updateData).forEach(key => {
      // 防止更新敏感字段
      if (key !== '_id' && key !== 'createdAt') {
        maze[key] = updateData[key];
      }
    });
    
    // 保存更新
    await maze.save();
    
    // 清理缓存
    await clearMazeCache(id);
    
    logger.info(`迷宫更新成功: ${id}`);
    return maze;
  } catch (error) {
    logger.error(`更新迷宫ID:${id}失败:`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    if (error.name === 'ValidationError') {
      const messages = Object.values(error.errors).map(err => err.message);
      throw createError(`迷宫数据验证失败: ${messages.join(', ')}`, 400);
    }
    
    throw createError('更新迷宫失败', 500);
  }
};

/**
 * 删除迷宫
 * @param {String} id - 迷宫ID
 * @returns {Promise<Boolean>} 是否成功
 */
const deleteMaze = async (id) => {
  try {
    const result = await Maze.findByIdAndDelete(id);
    
    if (!result) {
      throw createError('迷宫不存在', 404);
    }
    
    // 清理缓存
    await clearMazeCache(id);
    
    logger.info(`迷宫删除成功: ${id}`);
    return true;
  } catch (error) {
    logger.error(`删除迷宫ID:${id}失败:`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('删除迷宫失败', 500);
  }
};

/**
 * 向迷宫添加宝藏
 * @param {String} mazeId - 迷宫ID
 * @param {String} treasureId - 宝藏ID
 * @param {Number} x - X坐标
 * @param {Number} y - Y坐标
 * @returns {Promise<Object>} 更新后的迷宫
 */
const addTreasureToMaze = async (mazeId, treasureId, x, y) => {
  try {
    const maze = await Maze.findById(mazeId);
    
    if (!maze) {
      throw createError('迷宫不存在', 404);
    }
    
    // 添加宝藏
    maze.addTreasure(x, y, treasureId);
    await maze.save();
    
    // 清理缓存
    await clearMazeCache(mazeId);
    
    logger.info(`宝藏添加成功: 迷宫=${mazeId}, 宝藏=${treasureId}, 位置=(${x},${y})`);
    return maze;
  } catch (error) {
    logger.error(`向迷宫ID:${mazeId}添加宝藏失败:`, error);
    
    if (error.message === '无效的宝藏坐标' || 
        error.message === '该位置已存在宝藏' ||
        error.message === '宝藏只能放置在通道上') {
      throw createError(error.message, 400);
    }
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('添加宝藏失败', 500);
  }
};

/**
 * 获取迷宫的宝藏列表
 * @param {String} mazeId - 迷宫ID
 * @param {Object} options - 查询选项
 * @returns {Promise<Array>} 宝藏列表
 */
const getMazeTreasures = async (mazeId, options = {}) => {
  try {
    const { useCache = true } = options;
    
    // 创建缓存键
    const cacheKey = useCache ? `maze:treasures:${mazeId}` : null;
    
    // 尝试从缓存获取
    if (cacheKey) {
      const cachedTreasures = await getFromCache(cacheKey);
      if (cachedTreasures) {
        return cachedTreasures;
      }
    }
    
    // 执行查询
    const maze = await Maze.findById(mazeId)
      .select('treasurePositions')
      .populate('treasurePositions.treasureId')
      .lean();
    
    if (!maze) {
      throw createError('迷宫不存在', 404);
    }
    
    // 缓存结果
    if (cacheKey && maze.treasurePositions) {
      await saveToCache(cacheKey, maze.treasurePositions, CACHE_TTL.LIST);
    }
    
    return maze.treasurePositions;
  } catch (error) {
    logger.error(`获取迷宫ID:${mazeId}的宝藏失败:`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('获取迷宫宝藏失败', 500);
  }
};

/**
 * 获取迷宫统计数据
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Object>} 统计数据
 */
const getMazeStats = async (mazeId) => {
  try {
    // 创建缓存键
    const cacheKey = `maze:stats:${mazeId}`;
    
    // 尝试从缓存获取
    const cachedStats = await getFromCache(cacheKey);
    if (cachedStats) {
      return cachedStats;
    }
    
    // 执行查询
    const maze = await Maze.findById(mazeId)
      .select('stats name difficulty width height createdAt treasurePositions grid startPosition endPosition')
      .lean();
    
    if (!maze) {
      throw createError('迷宫不存在', 404);
    }
    
    // 计算迷宫复杂度
    const complexity = maze.grid ? mazeGenerator.analyzeMazeComplexity(maze.grid) : null;
    
    // 计算最短路径
    let shortestPath = null;
    if (maze.grid && maze.startPosition && maze.endPosition) {
      shortestPath = mazeGenerator.findShortestPath(maze.grid, maze.startPosition, maze.endPosition);
    }
    
    // 获取团队数据
    // 这里可以添加更多聚合查询来获取额外统计信息
    
    const stats = {
      basic: {
        name: maze.name,
        difficulty: maze.difficulty,
        size: `${maze.width}x${maze.height}`,
        createdAt: maze.createdAt,
        treasureCount: maze.treasurePositions ? maze.treasurePositions.length : 0
      },
      usage: maze.stats,
      complexity: complexity ? {
        score: complexity.complexityScore,
        deadEnds: complexity.deadEnds,
        junctions: complexity.junctions,
        openness: complexity.openness
      } : null,
      pathInfo: shortestPath ? {
        shortestPathLength: shortestPath.length,
        minStepsRequired: shortestPath.length - 1
      } : null
    };
    
    // 缓存结果
    await saveToCache(cacheKey, stats, CACHE_TTL.STATS);
    
    return stats;
  } catch (error) {
    logger.error(`获取迷宫ID:${mazeId}的统计数据失败:`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('获取迷宫统计数据失败', 500);
  }
};

/**
 * 通过季节ID获取迷宫列表
 * @param {String} seasonId - 季节ID
 * @param {Object} options - 查询选项
 * @returns {Promise<Array>} 迷宫列表
 */
const getMazesBySeasonId = async (seasonId, options = {}) => {
  const filter = { seasonId, isActive: true };
  return getAllMazes(filter, { 
    sort: { difficulty: 1, createdAt: -1 },
    ...options
  });
};

/**
 * 生成迷宫结构
 * @param {Object} config - 迷宫生成配置
 * @returns {Promise<Object>} 生成的迷宫结构
 */
const generateMazeStructure = async (config) => {
  try {
    // 使用优化后的迷宫生成算法
    const mazeStructure = mazeGenerator.generateMaze(config);
    
    // 分析复杂度
    const complexity = mazeGenerator.analyzeMazeComplexity(mazeStructure.grid);
    
    // 计算最短路径
    const shortestPath = mazeGenerator.findShortestPath(
      mazeStructure.grid, 
      mazeStructure.startPosition, 
      mazeStructure.endPosition
    );
    
    return {
      ...mazeStructure,
      shortestPathLength: shortestPath ? shortestPath.length : 0,
      complexity: complexity.complexityScore,
      analysisResults: complexity
    };
  } catch (error) {
    logger.error('生成迷宫结构失败:', error);
    throw createError('生成迷宫结构失败', 500);
  }
};

/**
 * 记录迷宫访问
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Object>} 更新后的统计数据
 */
const recordMazeVisit = async (mazeId) => {
  try {
    const maze = await Maze.findById(mazeId);
    
    if (!maze) {
      throw createError('迷宫不存在', 404);
    }
    
    await maze.incrementVisits();
    
    // 清理统计缓存
    await removeFromCache(`maze:stats:${mazeId}`);
    
    return maze.stats;
  } catch (error) {
    logger.error(`记录迷宫访问失败: ${mazeId}`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('记录迷宫访问失败', 500);
  }
};

/**
 * 记录迷宫完成
 * @param {String} mazeId - 迷宫ID
 * @param {Number} completionTime - 完成时间(秒)
 * @returns {Promise<Object>} 更新后的统计数据
 */
const recordMazeCompletion = async (mazeId, completionTime) => {
  try {
    const maze = await Maze.findById(mazeId);
    
    if (!maze) {
      throw createError('迷宫不存在', 404);
    }
    
    await maze.recordCompletion(completionTime);
    
    // 清理统计缓存
    await removeFromCache(`maze:stats:${mazeId}`);
    
    return maze.stats;
  } catch (error) {
    logger.error(`记录迷宫完成失败: ${mazeId}`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('记录迷宫完成失败', 500);
  }
};

/**
 * 根据用户历史数据推荐合适难度的迷宫
 * @param {String} userId - 用户ID
 * @param {String} seasonId - 季节ID
 * @returns {Promise<Array>} 推荐的迷宫列表
 */
const recommendMazes = async (userId, seasonId) => {
  try {
    // 获取用户完成的迷宫历史
    // 这里需要与用户服务交互，简化实现
    const userHistory = {
      completedMazes: 5,
      averageCompletionTime: 420, // 秒
      treasuresFound: 12,
      preferredDifficulty: 'medium'
    };
    
    // 基于用户历史确定合适的难度
    let recommendedDifficulty;
    
    if (userHistory.completedMazes < 3) {
      recommendedDifficulty = MAZE_DIFFICULTY.EASY;
    } else if (userHistory.completedMazes < 10) {
      recommendedDifficulty = MAZE_DIFFICULTY.MEDIUM;
    } else {
      recommendedDifficulty = MAZE_DIFFICULTY.HARD;
    }
    
    // 获取推荐难度的迷宫
    const filter = { 
      seasonId, 
      isActive: true,
      difficulty: recommendedDifficulty
    };
    
    const result = await getAllMazes(filter, {
      limit: 3,
      sort: { createdAt: -1 },
      projection: 'name difficulty width height theme treasurePositions stats'
    });
    
    return {
      mazes: result.mazes,
      recommendedDifficulty,
      userHistory
    };
  } catch (error) {
    logger.error(`获取用户推荐迷宫失败: ${userId}`, error);
    throw createError('获取推荐迷宫失败', 500);
  }
};

module.exports = {
  createMaze,
  getAllMazes,
  getMazeById,
  updateMaze,
  deleteMaze,
  addTreasureToMaze,
  getMazeTreasures,
  getMazeStats,
  getMazesBySeasonId,
  generateMazeStructure,
  recordMazeVisit,
  recordMazeCompletion,
  recommendMazes
};
