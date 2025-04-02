/**
 * 用户匹配控制器
 * 处理用户兴趣图谱匹配相关HTTP请求
 */
const userMatchService = require('../services/user-match.service');
const { BadRequestError, NotFoundError, UnauthorizedError } = require('../utils/errors');

/**
 * 创建用户匹配
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const createMatch = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { matchedUserId, matchType, matchScore, matchReason, matchedInterests, matchedKnowledgeDomains } = req.body;
    
    const match = await userMatchService.createMatch(userId, matchedUserId, {
      matchType,
      matchScore,
      matchReason,
      matchedInterests,
      matchedKnowledgeDomains
    });
    
    res.status(201).json({
      success: true,
      data: match
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取匹配详情
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const getMatchById = async (req, res, next) => {
  try {
    const { matchId } = req.params;
    const userId = req.user.id;
    
    const match = await userMatchService.getMatchById(matchId, userId);
    
    res.json({
      success: true,
      data: match
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 更新匹配状态
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const updateMatchStatus = async (req, res, next) => {
  try {
    const { matchId } = req.params;
    const userId = req.user.id;
    const { status } = req.body;
    
    const match = await userMatchService.updateMatchStatus(matchId, userId, status);
    
    res.json({
      success: true,
      data: match
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取用户匹配列表
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const getUserMatches = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { 
      limit = 20, 
      offset = 0, 
      matchType, 
      matchStatus, 
      minScore, 
      maxScore,
      includeUserInfo = false,
      isHidden
    } = req.query;
    
    const filters = {};
    
    if (matchType) {
      filters.matchType = matchType;
    }
    
    if (matchStatus) {
      filters.matchStatus = matchStatus;
    }
    
    if (minScore !== undefined) {
      filters.minScore = parseInt(minScore);
    }
    
    if (maxScore !== undefined) {
      filters.maxScore = parseInt(maxScore);
    }
    
    if (isHidden !== undefined) {
      filters.isHidden = isHidden === 'true';
    }
    
    filters.includeUserInfo = includeUserInfo === 'true';
    
    const matches = await userMatchService.getUserMatches(
      userId, 
      parseInt(limit), 
      parseInt(offset),
      filters
    );
    
    res.json({
      success: true,
      data: matches
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 删除匹配记录
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const deleteMatch = async (req, res, next) => {
  try {
    const { matchId } = req.params;
    const userId = req.user.id;
    
    await userMatchService.deleteMatch(matchId, userId);
    
    res.status(200).json({
      success: true,
      message: '匹配记录已删除'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 计算用户兴趣向量
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const calculateUserInterestVector = async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    const vector = await userMatchService.calculateUserInterestVector(userId);
    
    res.status(201).json({
      success: true,
      data: vector
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 查找潜在匹配用户
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const findPotentialMatches = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { limit = 10 } = req.query;
    
    const matches = await userMatchService.findPotentialMatches(userId, {
      limit: parseInt(limit)
    });
    
    res.json({
      success: true,
      data: matches
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 创建用户连接请求
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const createConnection = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { connectedUserId, connectionType, matchId, message } = req.body;
    
    const connection = await userMatchService.createConnection(userId, connectedUserId, {
      connectionType,
      matchId,
      message
    });
    
    res.status(201).json({
      success: true,
      data: connection
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 更新连接状态
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const updateConnectionStatus = async (req, res, next) => {
  try {
    const { connectionId } = req.params;
    const userId = req.user.id;
    const { status } = req.body;
    
    const connection = await userMatchService.updateConnectionStatus(connectionId, userId, status);
    
    res.json({
      success: true,
      data: connection
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取用户连接列表
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const getUserConnections = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { 
      limit = 20, 
      offset = 0, 
      connectionType, 
      connectionStatus 
    } = req.query;
    
    const filters = {};
    
    if (connectionType) {
      filters.connectionType = connectionType;
    }
    
    if (connectionStatus) {
      filters.connectionStatus = connectionStatus;
    }
    
    const connections = await userMatchService.getUserConnections(
      userId, 
      parseInt(limit), 
      parseInt(offset),
      filters
    );
    
    res.json({
      success: true,
      data: connections
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  createMatch,
  getMatchById,
  updateMatchStatus,
  getUserMatches,
  deleteMatch,
  calculateUserInterestVector,
  findPotentialMatches,
  createConnection,
  updateConnectionStatus,
  getUserConnections
};