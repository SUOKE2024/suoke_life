/**
 * 推荐服务
 * 提供个性化推荐和匹配功能
 */
const logger = require('../utils/logger');
const { getRedisClient } = require('../config/redis');
const { createError } = require('../middlewares/errorHandler');
const mazeService = require('./mazeService');
const Maze = require('../models/maze.model');
const Team = require('../models/team.model');

// 缓存配置
const CACHE_TTL = {
  RECOMMENDATIONS: 3600, // 推荐缓存1小时
  USER_HISTORY: 86400 // 用户历史缓存1天
};

/**
 * 获取用户游戏历史
 * @param {String} userId - 用户ID
 * @returns {Promise<Object>} 用户历史数据
 */
const getUserHistory = async (userId) => {
  try {
    // 尝试从缓存获取
    const redisClient = getRedisClient();
    const cacheKey = `user:history:${userId}`;
    
    const cachedHistory = await redisClient.get(cacheKey);
    if (cachedHistory) {
      return JSON.parse(cachedHistory);
    }
    
    // 从数据库获取用户历史（这里简化实现）
    // 实际项目中应该从用户服务或历史记录集合中获取
    
    // 获取用户参与的团队
    const teams = await Team.find({
      'players.userId': userId,
      status: { $in: ['completed', 'in_progress'] }
    }).lean();
    
    // 分析团队数据
    const completedMazes = teams.filter(t => t.status === 'completed').length;
    const activeMazes = teams.filter(t => t.status === 'in_progress').length;
    
    // 计算平均完成时间
    let totalCompletionTime = 0;
    let completionCount = 0;
    
    for (const team of teams) {
      if (team.status === 'completed' && team.progress.startedAt && team.progress.completedAt) {
        const durationMs = new Date(team.progress.completedAt) - new Date(team.progress.startedAt);
        const durationSeconds = Math.floor(durationMs / 1000);
        totalCompletionTime += durationSeconds;
        completionCount++;
      }
    }
    
    const averageCompletionTime = completionCount > 0 ? Math.floor(totalCompletionTime / completionCount) : 0;
    
    // 计算收集的宝藏数量
    let treasuresFound = 0;
    for (const team of teams) {
      const player = team.players.find(p => p.userId === userId);
      if (player && player.treasuresFound) {
        treasuresFound += player.treasuresFound.length;
      }
    }
    
    // 确定用户的难度偏好
    const difficultyScores = {
      'easy': 0,
      'medium': 0,
      'hard': 0,
      'expert': 0
    };
    
    // 根据完成的迷宫计算难度偏好
    for (const team of teams) {
      if (team.status === 'completed' && team.mazeId) {
        const maze = await Maze.findById(team.mazeId).select('difficulty').lean();
        if (maze && maze.difficulty) {
          difficultyScores[maze.difficulty] += 1;
        }
      }
    }
    
    // 找出最高分的难度
    let preferredDifficulty = 'medium'; // 默认值
    let maxScore = 0;
    
    for (const [difficulty, score] of Object.entries(difficultyScores)) {
      if (score > maxScore) {
        maxScore = score;
        preferredDifficulty = difficulty;
      }
    }
    
    // 构建历史数据
    const history = {
      completedMazes,
      activeMazes,
      averageCompletionTime,
      treasuresFound,
      preferredDifficulty,
      lastActive: new Date(),
      teams: teams.map(t => t._id.toString()).slice(0, 10) // 限制数量
    };
    
    // 缓存历史数据
    await redisClient.set(cacheKey, JSON.stringify(history));
    await redisClient.expire(cacheKey, CACHE_TTL.USER_HISTORY);
    
    return history;
  } catch (error) {
    logger.error(`获取用户历史失败: ${userId}`, error);
    return {
      completedMazes: 0,
      activeMazes: 0,
      averageCompletionTime: 0,
      treasuresFound: 0,
      preferredDifficulty: 'medium',
      lastActive: new Date(),
      teams: []
    };
  }
};

/**
 * 根据用户历史推荐迷宫
 * @param {String} userId - 用户ID
 * @param {String} seasonId - 季节ID
 * @returns {Promise<Object>} 推荐结果
 */
const recommendMazes = async (userId, seasonId) => {
  try {
    const cacheKey = `recommendations:mazes:${userId}:${seasonId}`;
    const redisClient = getRedisClient();
    
    // 尝试从缓存获取
    const cachedRecommendations = await redisClient.get(cacheKey);
    if (cachedRecommendations) {
      return JSON.parse(cachedRecommendations);
    }
    
    // 获取用户历史
    const history = await getUserHistory(userId);
    
    // 确定推荐难度
    let recommendedDifficulty;
    
    if (history.completedMazes < 3) {
      // 新手用户从简单开始
      recommendedDifficulty = 'easy';
    } else if (history.completedMazes < 10) {
      // 有一些经验的用户
      recommendedDifficulty = history.preferredDifficulty === 'easy' ? 'medium' : history.preferredDifficulty;
    } else {
      // 经验丰富的用户，可以升级难度
      const difficultyLevels = ['easy', 'medium', 'hard', 'expert'];
      const currentIndex = difficultyLevels.indexOf(history.preferredDifficulty);
      const nextIndex = Math.min(currentIndex + 1, difficultyLevels.length - 1);
      recommendedDifficulty = difficultyLevels[nextIndex];
    }
    
    // 获取推荐迷宫
    const filter = { 
      seasonId, 
      isActive: true,
      difficulty: recommendedDifficulty
    };
    
    const result = await mazeService.getAllMazes(filter, {
      limit: 3,
      sort: { createdAt: -1 },
      projection: 'name difficulty width height theme treasurePositions stats'
    });
    
    // 构建推荐结果
    const recommendations = {
      mazes: result.mazes,
      recommendedDifficulty,
      userStats: {
        completedMazes: history.completedMazes,
        averageCompletionTime: history.averageCompletionTime,
        treasuresFound: history.treasuresFound
      },
      reasoning: getRecommendationReasoning(history)
    };
    
    // 缓存推荐结果
    await redisClient.set(cacheKey, JSON.stringify(recommendations));
    await redisClient.expire(cacheKey, CACHE_TTL.RECOMMENDATIONS);
    
    return recommendations;
  } catch (error) {
    logger.error(`生成迷宫推荐失败: ${userId}`, error);
    throw createError('生成迷宫推荐失败', 500);
  }
};

/**
 * 获取推荐理由
 * @param {Object} history - 用户历史
 * @returns {String} 推荐理由
 */
const getRecommendationReasoning = (history) => {
  if (history.completedMazes < 3) {
    return '您是新玩家，我们推荐从简单难度开始熟悉游戏';
  } else if (history.completedMazes < 10) {
    return `您已完成${history.completedMazes}个迷宫，看起来已经掌握了基本技巧`;
  } else {
    return `您是经验丰富的玩家，已完成${history.completedMazes}个迷宫，我们为您准备了更具挑战性的内容`;
  }
};

/**
 * 推荐适合用户的团队
 * @param {String} userId - 用户ID
 * @param {String} mazeId - 迷宫ID (可选)
 * @returns {Promise<Array>} 推荐的团队列表
 */
const recommendTeams = async (userId, mazeId = null) => {
  try {
    const cacheKey = `recommendations:teams:${userId}:${mazeId || 'all'}`;
    const redisClient = getRedisClient();
    
    // 尝试从缓存获取
    const cachedRecommendations = await redisClient.get(cacheKey);
    if (cachedRecommendations) {
      return JSON.parse(cachedRecommendations);
    }
    
    // 获取用户历史
    const history = await getUserHistory(userId);
    
    // 构建查询条件
    const filter = {
      status: 'waiting', // 等待中的团队
      'players.userId': { $ne: userId }, // 排除用户已加入的团队
      'settings.allowJoinRequests': true // 允许加入请求
    };
    
    // 如果指定了迷宫，则筛选该迷宫的团队
    if (mazeId) {
      filter.mazeId = mazeId;
    }
    
    // 查询所有候选团队
    const teams = await Team.find(filter)
      .select('name code players settings mazeId createdAt')
      .populate('mazeId', 'name difficulty')
      .lean();
    
    // 如果没有找到团队，返回空结果
    if (!teams.length) {
      return { teams: [] };
    }
    
    // 对团队进行评分
    const scoredTeams = teams.map(team => {
      let score = 0;
      
      // 团队规模因素 (优先推荐人数适中的团队)
      const teamSize = team.players.filter(p => p.isActive).length;
      score += 10 - Math.abs(2 - teamSize); // 2-3人团队得分高
      
      // 难度匹配因素
      if (team.mazeId && team.mazeId.difficulty === history.preferredDifficulty) {
        score += 5;
      }
      
      // 新鲜度因素 (较新的团队得分高)
      const ageHours = (Date.now() - new Date(team.createdAt)) / (1000 * 60 * 60);
      score += Math.max(0, 10 - ageHours); // 最多10分，每小时减1分
      
      return {
        ...team,
        score,
        playerCount: teamSize,
        formation: formatTimeDiff(new Date(team.createdAt))
      };
    });
    
    // 按评分排序
    scoredTeams.sort((a, b) => b.score - a.score);
    
    // 构建推荐结果
    const recommendations = {
      teams: scoredTeams.slice(0, 5), // 取前5个
      userHistory: {
        completedMazes: history.completedMazes,
        preferredDifficulty: history.preferredDifficulty
      }
    };
    
    // 缓存推荐结果
    await redisClient.set(cacheKey, JSON.stringify(recommendations));
    await redisClient.expire(cacheKey, CACHE_TTL.RECOMMENDATIONS);
    
    return recommendations;
  } catch (error) {
    logger.error(`生成团队推荐失败: ${userId}`, error);
    throw createError('生成团队推荐失败', 500);
  }
};

/**
 * 格式化时间差
 * @param {Date} date - 日期
 * @returns {String} 格式化后的时间差
 */
const formatTimeDiff = (date) => {
  const now = new Date();
  const diffMs = now - date;
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  
  if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`;
  }
  
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours}小时前`;
  }
  
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}天前`;
};

/**
 * 推荐宝藏
 * @param {String} userId - 用户ID
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Array>} 推荐的宝藏列表
 */
const recommendTreasures = async (userId, mazeId) => {
  try {
    const cacheKey = `recommendations:treasures:${userId}:${mazeId}`;
    const redisClient = getRedisClient();
    
    // 尝试从缓存获取
    const cachedRecommendations = await redisClient.get(cacheKey);
    if (cachedRecommendations) {
      return JSON.parse(cachedRecommendations);
    }
    
    // 获取用户历史
    const history = await getUserHistory(userId);
    
    // 获取迷宫宝藏
    const treasures = await mazeService.getMazeTreasures(mazeId, { useCache: true });
    
    // 如果没有宝藏，返回空结果
    if (!treasures || !treasures.length) {
      return { treasures: [] };
    }
    
    // 获取用户在该迷宫收集的宝藏
    const team = await Team.findOne({
      mazeId,
      'players.userId': userId
    }).select('players').lean();
    
    const collectedTreasureIds = new Set();
    
    if (team) {
      const player = team.players.find(p => p.userId === userId);
      if (player && player.treasuresFound) {
        player.treasuresFound.forEach(id => collectedTreasureIds.add(id));
      }
    }
    
    // 过滤出未收集的宝藏
    const uncollectedTreasures = treasures.filter(
      t => !collectedTreasureIds.has(t.treasureId?.toString())
    );
    
    // 如果都已收集，返回空结果
    if (!uncollectedTreasures.length) {
      return { 
        treasures: [],
        message: '您已收集该迷宫的所有宝藏！'
      };
    }
    
    // 根据用户位置计算距离 (如果有)
    // 这里简化实现，实际项目中应使用实时位置数据
    const userPosition = { x: 0, y: 0 }; // 默认位置
    
    // 对宝藏评分
    const scoredTreasures = uncollectedTreasures.map(treasure => {
      // 计算到用户的距离
      const distance = Math.sqrt(
        Math.pow(treasure.x - userPosition.x, 2) + 
        Math.pow(treasure.y - userPosition.y, 2)
      );
      
      // 评分标准: 距离越近得分越高
      const proximityScore = Math.max(0, 10 - distance / 2);
      
      return {
        ...treasure,
        distance,
        score: proximityScore
      };
    });
    
    // 按评分排序
    scoredTreasures.sort((a, b) => b.score - a.score);
    
    // 构建推荐结果
    const recommendations = {
      treasures: scoredTreasures.slice(0, 3), // 取前3个
      collectedCount: collectedTreasureIds.size,
      totalCount: treasures.length
    };
    
    // 缓存推荐结果
    await redisClient.set(cacheKey, JSON.stringify(recommendations));
    await redisClient.expire(cacheKey, 300); // 宝藏推荐缓存5分钟
    
    return recommendations;
  } catch (error) {
    logger.error(`生成宝藏推荐失败: ${userId}, ${mazeId}`, error);
    throw createError('生成宝藏推荐失败', 500);
  }
};

module.exports = {
  getUserHistory,
  recommendMazes,
  recommendTeams,
  recommendTreasures
}; 