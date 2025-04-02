/**
 * 社交分享服务
 * 处理社交分享相关业务逻辑
 */
const socialShareRepository = require('../repositories/social-share.repository');
const userRepository = require('../repositories/user.repository');
const contentRepository = require('../repositories/content.repository');
const logger = require('../utils/logger');
const socialShareModel = require('../models/social-share.model');
const { BadRequestError, NotFoundError, UnauthorizedError } = require('../utils/errors');

/**
 * 创建分享
 * @param {string} userId - 用户ID
 * @param {Object} shareData - 分享数据
 * @returns {Promise<Object>} 创建的分享对象
 */
async function createShare(userId, shareData) {
  try {
    // 验证用户存在
    const user = await userRepository.getUserById(userId);
    if (!user) {
      throw new NotFoundError('用户不存在');
    }
    
    // 验证分享类型
    if (!Object.values(socialShareModel.SHARE_TYPES).includes(shareData.shareType)) {
      throw new BadRequestError('无效的分享类型');
    }

    // 验证平台
    if (shareData.platform && !Object.values(socialShareModel.PLATFORMS).includes(shareData.platform)) {
      throw new BadRequestError('无效的分享平台');
    }
    
    // 针对内容分享，验证内容ID
    if (shareData.shareType === socialShareModel.SHARE_TYPES.CONTENT && shareData.contentId) {
      const content = await contentRepository.getContentById(shareData.contentId);
      if (!content) {
        throw new NotFoundError('分享内容不存在');
      }
      
      // 如果未提供标题或描述，则从内容中获取
      if (!shareData.title) {
        shareData.title = content.title || '分享内容';
      }
      
      if (!shareData.description) {
        shareData.description = content.summary || content.description || '';
      }
    }
    
    // 创建分享
    const share = await socialShareRepository.createShare({
      userId,
      shareType: shareData.shareType,
      contentId: shareData.contentId,
      title: shareData.title || '分享',
      description: shareData.description || '',
      imageUrl: shareData.imageUrl,
      targetUrl: shareData.targetUrl,
      platform: shareData.platform,
      shareStatus: socialShareModel.SHARE_STATUS.ACTIVE,
      customData: shareData.customData || {}
    });
    
    return share;
  } catch (error) {
    if (error instanceof BadRequestError || error instanceof NotFoundError) {
      throw error;
    }
    logger.error('创建分享失败', { userId, error: error.message });
    throw new Error('创建分享失败');
  }
}

/**
 * 更新分享
 * @param {string} shareId - 分享ID
 * @param {string} userId - 用户ID
 * @param {Object} updateData - 更新数据
 * @returns {Promise<Object>} 更新后的分享对象
 */
async function updateShare(shareId, userId, updateData) {
  try {
    // 获取分享对象
    const share = await socialShareRepository.getShareById(shareId);
    if (!share) {
      throw new NotFoundError('分享不存在');
    }
    
    // 验证所有权
    if (share.userId !== userId) {
      throw new UnauthorizedError('无权更新分享');
    }
    
    // 验证平台
    if (updateData.platform && !Object.values(socialShareModel.PLATFORMS).includes(updateData.platform)) {
      throw new BadRequestError('无效的分享平台');
    }
    
    // 验证状态
    if (updateData.shareStatus && !Object.values(socialShareModel.SHARE_STATUS).includes(updateData.shareStatus)) {
      throw new BadRequestError('无效的分享状态');
    }
    
    // 更新分享
    const updated = await socialShareRepository.updateShare(shareId, {
      title: updateData.title,
      description: updateData.description,
      imageUrl: updateData.imageUrl,
      targetUrl: updateData.targetUrl,
      platform: updateData.platform,
      shareStatus: updateData.shareStatus,
      customData: updateData.customData
    });
    
    if (!updated) {
      throw new Error('更新分享失败');
    }
    
    // 获取更新后的分享对象
    return await socialShareRepository.getShareById(shareId);
  } catch (error) {
    if (error instanceof BadRequestError || error instanceof NotFoundError || error instanceof UnauthorizedError) {
      throw error;
    }
    logger.error(`更新分享失败: ${shareId}`, { userId, error: error.message });
    throw new Error('更新分享失败');
  }
}

/**
 * 获取分享详情
 * @param {string} shareId - 分享ID
 * @returns {Promise<Object>} 分享对象
 */
async function getShareById(shareId) {
  try {
    const share = await socialShareRepository.getShareById(shareId);
    if (!share) {
      throw new NotFoundError('分享不存在');
    }
    
    return share;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`获取分享失败: ${shareId}`, { error: error.message });
    throw new Error('获取分享失败');
  }
}

/**
 * 获取用户分享列表
 * @param {string} userId - 用户ID
 * @param {number} limit - 限制返回数量
 * @param {number} offset - 结果偏移量
 * @param {Object} filters - 过滤条件
 * @returns {Promise<Array>} 分享列表
 */
async function getUserShares(userId, limit = 20, offset = 0, filters = {}) {
  try {
    // 验证用户存在
    const user = await userRepository.getUserById(userId);
    if (!user) {
      throw new NotFoundError('用户不存在');
    }
    
    // 获取分享列表
    const shares = await socialShareRepository.getUserShares(userId, limit, offset, filters);
    return shares;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`获取用户分享列表失败: ${userId}`, { error: error.message });
    throw new Error('获取用户分享列表失败');
  }
}

/**
 * 删除分享
 * @param {string} shareId - 分享ID
 * @param {string} userId - 用户ID
 * @returns {Promise<boolean>} 操作结果
 */
async function deleteShare(shareId, userId) {
  try {
    // 获取分享对象
    const share = await socialShareRepository.getShareById(shareId);
    if (!share) {
      throw new NotFoundError('分享不存在');
    }
    
    // 验证所有权
    if (share.userId !== userId) {
      throw new UnauthorizedError('无权删除分享');
    }
    
    // 删除分享
    const deleted = await socialShareRepository.deleteShare(shareId, userId);
    if (!deleted) {
      throw new Error('删除分享失败');
    }
    
    return true;
  } catch (error) {
    if (error instanceof NotFoundError || error instanceof UnauthorizedError) {
      throw error;
    }
    logger.error(`删除分享失败: ${shareId}`, { userId, error: error.message });
    throw new Error('删除分享失败');
  }
}

/**
 * 记录分享互动
 * @param {string} shareId - 分享ID
 * @param {string} interactionUserId - 交互用户ID
 * @param {string} interactionType - 交互类型
 * @param {Object} interactionData - 交互数据
 * @returns {Promise<Object>} 创建的互动对象
 */
async function recordShareInteraction(shareId, interactionUserId, interactionType, interactionData = {}) {
  try {
    // 验证分享存在
    const share = await socialShareRepository.getShareById(shareId);
    if (!share) {
      throw new NotFoundError('分享不存在');
    }
    
    // 验证互动类型
    if (!Object.values(socialShareModel.INTERACTION_TYPES).includes(interactionType)) {
      throw new BadRequestError('无效的互动类型');
    }
    
    // 记录互动
    const interaction = await socialShareRepository.recordShareInteraction({
      shareId,
      userId: interactionUserId,
      interactionType,
      interactionData
    });
    
    // 更新分享的互动计数
    if (interactionType === socialShareModel.INTERACTION_TYPES.VIEW) {
      await socialShareRepository.updateShareViewCount(shareId);
    } else {
      await socialShareRepository.updateShareInteractionCount(shareId);
    }
    
    return interaction;
  } catch (error) {
    if (error instanceof BadRequestError || error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`记录分享互动失败: ${shareId}`, { 
      interactionUserId, 
      interactionType, 
      error: error.message 
    });
    throw new Error('记录分享互动失败');
  }
}

/**
 * 获取分享互动列表
 * @param {string} shareId - 分享ID
 * @param {number} limit - 限制返回数量
 * @param {number} offset - 结果偏移量
 * @param {string} interactionType - 互动类型
 * @returns {Promise<Array>} 互动列表
 */
async function getShareInteractions(shareId, limit = 20, offset = 0, interactionType = null) {
  try {
    // 验证分享存在
    const share = await socialShareRepository.getShareById(shareId);
    if (!share) {
      throw new NotFoundError('分享不存在');
    }
    
    // 验证互动类型
    if (interactionType && !Object.values(socialShareModel.INTERACTION_TYPES).includes(interactionType)) {
      throw new BadRequestError('无效的互动类型');
    }
    
    // 获取互动列表
    const interactions = await socialShareRepository.getShareInteractions(
      shareId, 
      limit, 
      offset, 
      interactionType
    );
    
    return interactions;
  } catch (error) {
    if (error instanceof BadRequestError || error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`获取分享互动列表失败: ${shareId}`, { error: error.message });
    throw new Error('获取分享互动列表失败');
  }
}

/**
 * 生成分享链接
 * @param {string} shareId - 分享ID
 * @param {Object} options - 选项
 * @returns {Promise<string>} 分享链接
 */
async function generateShareLink(shareId, options = {}) {
  try {
    // 获取分享对象
    const share = await socialShareRepository.getShareById(shareId);
    if (!share) {
      throw new NotFoundError('分享不存在');
    }
    
    // 基础URL
    const baseUrl = process.env.SHARE_BASE_URL || 'https://suoke.life/share';
    
    // 构建查询参数
    const queryParams = new URLSearchParams();
    queryParams.append('id', shareId);
    
    if (options.utm_source) {
      queryParams.append('utm_source', options.utm_source);
    }
    
    if (options.utm_medium) {
      queryParams.append('utm_medium', options.utm_medium);
    }
    
    if (options.utm_campaign) {
      queryParams.append('utm_campaign', options.utm_campaign);
    }
    
    if (share.platform) {
      queryParams.append('platform', share.platform);
    }
    
    // 生成URL
    return `${baseUrl}?${queryParams.toString()}`;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`生成分享链接失败: ${shareId}`, { error: error.message });
    throw new Error('生成分享链接失败');
  }
}

module.exports = {
  createShare,
  updateShare,
  getShareById,
  getUserShares,
  deleteShare,
  recordShareInteraction,
  getShareInteractions,
  generateShareLink
};