/**
 * 离线功能控制器
 * 处理离线功能相关请求
 */
const logger = require('../utils/logger');
const offlineService = require('../services/offlineService');
const { createError } = require('../middlewares/errorHandler');

/**
 * 获取离线数据包
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getOfflinePackage = async (req, res, next) => {
  try {
    const { mazeId } = req.params;
    const userId = req.user.id;
    
    if (!mazeId) {
      return next(createError('缺少迷宫ID', 400));
    }
    
    const offlinePackage = await offlineService.generateOfflinePackage(userId, mazeId);
    
    res.json({
      success: true,
      data: offlinePackage
    });
  } catch (error) {
    logger.error(`获取离线包失败: ${req.params.mazeId}`, error);
    next(createError(error.message || '获取离线包失败', error.status || 500));
  }
};

/**
 * 同步离线更改
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const syncOfflineChanges = async (req, res, next) => {
  try {
    const { changes } = req.body;
    const userId = req.user.id;
    
    if (!changes || !Array.isArray(changes)) {
      return next(createError('无效的更改数据', 400));
    }
    
    const result = await offlineService.saveOfflineChanges(userId, changes);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error(`同步离线更改失败: ${req.user.id}`, error);
    next(createError(error.message || '同步离线更改失败', error.status || 500));
  }
};

/**
 * 获取同步状态
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getSyncStatus = async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    const status = await offlineService.getSyncStatus(userId);
    
    res.json({
      success: true,
      data: status
    });
  } catch (error) {
    logger.error(`获取同步状态失败: ${req.user.id}`, error);
    next(createError(error.message || '获取同步状态失败', error.status || 500));
  }
};

/**
 * 检查离线包更新
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const checkUpdates = async (req, res, next) => {
  try {
    const { mazeId, versionHash } = req.body;
    const userId = req.user.id;
    
    if (!mazeId || !versionHash) {
      return next(createError('缺少必要参数', 400));
    }
    
    const needsUpdate = await offlineService.checkOfflinePackageUpdates(userId, mazeId, versionHash);
    
    res.json({
      success: true,
      data: {
        needsUpdate
      }
    });
  } catch (error) {
    logger.error(`检查离线包更新失败: ${req.body.mazeId}`, error);
    next(createError(error.message || '检查离线包更新失败', error.status || 500));
  }
};

module.exports = {
  getOfflinePackage,
  syncOfflineChanges,
  getSyncStatus,
  checkUpdates
}; 