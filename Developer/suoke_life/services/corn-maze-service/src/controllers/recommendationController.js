/**
 * 推荐系统控制器
 * 处理推荐系统相关请求
 */
const logger = require('../utils/logger');
const recommendationService = require('../services/recommendationService');
const { createError } = require('../middlewares/errorHandler');

/**
 * 获取用户历史数据
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getUserHistory = async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    const history = await recommendationService.getUserHistory(userId);
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    logger.error(`获取用户历史失败: ${req.user.id}`, error);
    next(createError(error.message || '获取用户历史失败', error.status || 500));
  }
};

/**
 * 获取推荐的迷宫
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getRecommendedMazes = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { seasonId } = req.query;
    
    if (!seasonId) {
      return next(createError('缺少季节ID', 400));
    }
    
    const recommendations = await recommendationService.recommendMazes(userId, seasonId);
    
    res.json({
      success: true,
      data: recommendations
    });
  } catch (error) {
    logger.error(`获取推荐迷宫失败: ${req.user.id}`, error);
    next(createError(error.message || '获取推荐迷宫失败', error.status || 500));
  }
};

/**
 * 获取推荐的团队
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getRecommendedTeams = async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    const recommendations = await recommendationService.recommendTeams(userId);
    
    res.json({
      success: true,
      data: recommendations
    });
  } catch (error) {
    logger.error(`获取推荐团队失败: ${req.user.id}`, error);
    next(createError(error.message || '获取推荐团队失败', error.status || 500));
  }
};

/**
 * 获取指定迷宫的推荐团队
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getRecommendedTeamsForMaze = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { mazeId } = req.params;
    
    if (!mazeId) {
      return next(createError('缺少迷宫ID', 400));
    }
    
    const recommendations = await recommendationService.recommendTeams(userId, mazeId);
    
    res.json({
      success: true,
      data: recommendations
    });
  } catch (error) {
    logger.error(`获取迷宫推荐团队失败: ${req.user.id}, ${req.params.mazeId}`, error);
    next(createError(error.message || '获取迷宫推荐团队失败', error.status || 500));
  }
};

/**
 * 获取推荐的宝藏
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getRecommendedTreasures = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { mazeId } = req.params;
    
    if (!mazeId) {
      return next(createError('缺少迷宫ID', 400));
    }
    
    const recommendations = await recommendationService.recommendTreasures(userId, mazeId);
    
    res.json({
      success: true,
      data: recommendations
    });
  } catch (error) {
    logger.error(`获取推荐宝藏失败: ${req.user.id}, ${req.params.mazeId}`, error);
    next(createError(error.message || '获取推荐宝藏失败', error.status || 500));
  }
};

module.exports = {
  getUserHistory,
  getRecommendedMazes,
  getRecommendedTeams,
  getRecommendedTeamsForMaze,
  getRecommendedTreasures
}; 