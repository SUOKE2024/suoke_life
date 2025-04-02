/**
 * 社交分享控制器
 * 处理社交分享相关HTTP请求
 */
const socialShareService = require('../services/social-share.service');
const { BadRequestError, NotFoundError, UnauthorizedError } = require('../utils/errors');

/**
 * 创建分享
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const createShare = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const shareData = req.body;
    
    const share = await socialShareService.createShare(userId, shareData);
    
    res.status(201).json({
      success: true,
      data: share
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取分享详情
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const getShareById = async (req, res, next) => {
  try {
    const { shareId } = req.params;
    
    const share = await socialShareService.getShareById(shareId);
    
    res.json({
      success: true,
      data: share
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 更新分享
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const updateShare = async (req, res, next) => {
  try {
    const { shareId } = req.params;
    const userId = req.user.id;
    const updateData = req.body;
    
    const share = await socialShareService.updateShare(shareId, userId, updateData);
    
    res.json({
      success: true,
      data: share
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 删除分享
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const deleteShare = async (req, res, next) => {
  try {
    const { shareId } = req.params;
    const userId = req.user.id;
    
    await socialShareService.deleteShare(shareId, userId);
    
    res.status(200).json({
      success: true,
      message: '分享已删除'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取用户分享列表
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const getUserShares = async (req, res, next) => {
  try {
    const { userId } = req.params;
    const { 
      limit = 20, 
      offset = 0, 
      shareType, 
      platform, 
      status 
    } = req.query;
    
    const filters = {};
    
    if (shareType) {
      filters.shareType = shareType;
    }
    
    if (platform) {
      filters.platform = platform;
    }
    
    if (status) {
      filters.shareStatus = status;
    }
    
    const shares = await socialShareService.getUserShares(
      userId, 
      parseInt(limit), 
      parseInt(offset),
      filters
    );
    
    res.json({
      success: true,
      data: shares
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 记录分享互动
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const recordShareInteraction = async (req, res, next) => {
  try {
    const { shareId } = req.params;
    const userId = req.user.id;
    const { interactionType, interactionData } = req.body;
    
    const interaction = await socialShareService.recordShareInteraction(
      shareId,
      userId,
      interactionType,
      interactionData
    );
    
    res.status(201).json({
      success: true,
      data: interaction
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取分享互动列表
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const getShareInteractions = async (req, res, next) => {
  try {
    const { shareId } = req.params;
    const { 
      limit = 20, 
      offset = 0, 
      interactionType 
    } = req.query;
    
    const interactions = await socialShareService.getShareInteractions(
      shareId,
      parseInt(limit),
      parseInt(offset),
      interactionType
    );
    
    res.json({
      success: true,
      data: interactions
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 生成分享链接
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const generateShareLink = async (req, res, next) => {
  try {
    const { shareId } = req.params;
    const options = req.body;
    
    const shareLink = await socialShareService.generateShareLink(shareId, options);
    
    res.json({
      success: true,
      data: {
        shareId,
        shareLink
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 记录分享查看
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件函数
 */
const recordShareView = async (req, res, next) => {
  try {
    const { shareId } = req.params;
    const { referrer, clientInfo } = req.body;
    
    await socialShareService.recordShareInteraction(
      shareId,
      null, // 匿名用户
      'view',
      { referrer, clientInfo }
    );
    
    res.status(200).json({
      success: true,
      message: '记录查看成功'
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  createShare,
  getShareById,
  updateShare,
  deleteShare,
  getUserShares,
  recordShareInteraction,
  getShareInteractions,
  generateShareLink,
  recordShareView
};