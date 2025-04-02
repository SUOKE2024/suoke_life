/**
 * 宝藏服务
 * 提供宝藏管理和AR交互功能
 */
const Treasure = require('../models/treasure.model');
const { createError } = require('../middlewares/errorHandler');
const logger = require('../utils/logger');
const { REWARD_TYPES, REWARD_RARITY, AR_MARKER_TYPES } = require('../utils/constants');

// 导入新服务模块
const imageRecognitionService = require('./imageRecognitionService');
const notificationService = require('./notificationService');
const realTimeService = require('./realTimeService');

// 暂时模拟缺少的模型
const Team = require('../models/team.model');
const Maze = require('../models/maze.model');
const TeamHuntSession = mongoose.model('TeamHuntSession', new mongoose.Schema({
  teamId: String,
  mazeId: String,
  startedBy: String,
  startedAt: Date,
  status: String,
  participants: Array
}));
const TreasureShare = mongoose.model('TreasureShare', new mongoose.Schema({
  treasureId: String,
  fromUser: String,
  toUser: String,
  message: String,
  sharedAt: Date
}));

/**
 * 创建新宝藏
 * @param {Object} treasureData - 宝藏数据
 * @returns {Promise<Object>} 创建的宝藏
 */
const createTreasure = async (treasureData) => {
  try {
    // 确保AR标记ID唯一
    if (treasureData.arMarker && treasureData.arMarker.markerId) {
      const existingTreasure = await Treasure.findOne({
        'arMarker.markerId': treasureData.arMarker.markerId
      });
      
      if (existingTreasure) {
        throw createError('AR标记ID已被使用', 409);
      }
    }
    
    // 如果是限量宝藏，设置剩余数量
    if (treasureData.isLimited && treasureData.limitedQuantity) {
      treasureData.remainingQuantity = treasureData.limitedQuantity;
    }
    
    const treasure = new Treasure(treasureData);
    await treasure.save();
    return treasure;
  } catch (error) {
    logger.error('创建宝藏失败:', error);
    
    if (error.statusCode) {
      throw error;
    }
    
    throw createError('创建宝藏失败', 400);
  }
};

/**
 * 获取所有宝藏
 * @param {Object} filter - 过滤条件
 * @param {Object} options - 查询选项
 * @returns {Promise<Array>} 宝藏列表
 */
const getAllTreasures = async (filter = {}, options = {}) => {
  try {
    const { page = 1, limit = 10, sort = { createdAt: -1 } } = options;
    const skip = (page - 1) * limit;
    
    const treasures = await Treasure.find(filter)
      .sort(sort)
      .skip(skip)
      .limit(limit);
    
    const total = await Treasure.countDocuments(filter);
    
    return {
      treasures,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      }
    };
  } catch (error) {
    logger.error('获取宝藏列表失败:', error);
    throw createError('获取宝藏列表失败', 500);
  }
};

/**
 * 通过ID获取宝藏
 * @param {String} id - 宝藏ID
 * @returns {Promise<Object>} 宝藏
 */
const getTreasureById = async (id) => {
  try {
    const treasure = await Treasure.findById(id);
    
    if (!treasure) {
      throw createError('宝藏不存在', 404);
    }
    
    return treasure;
  } catch (error) {
    logger.error(`获取宝藏ID:${id}失败:`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('获取宝藏详情失败', 500);
  }
};

/**
 * 更新宝藏
 * @param {String} id - 宝藏ID
 * @param {Object} updateData - 更新数据
 * @returns {Promise<Object>} 更新后的宝藏
 */
const updateTreasure = async (id, updateData) => {
  try {
    const treasure = await Treasure.findById(id);
    
    if (!treasure) {
      throw createError('宝藏不存在', 404);
    }
    
    // 验证AR标记ID唯一
    if (updateData.arMarker && updateData.arMarker.markerId && 
        updateData.arMarker.markerId !== treasure.arMarker.markerId) {
      const existingTreasure = await Treasure.findOne({
        'arMarker.markerId': updateData.arMarker.markerId,
        _id: { $ne: id }
      });
      
      if (existingTreasure) {
        throw createError('AR标记ID已被使用', 409);
      }
    }
    
    // 更新可修改的字段
    Object.keys(updateData).forEach(key => {
      // 防止更新敏感字段
      if (key !== '_id' && key !== 'createdAt' && key !== 'discoveredBy') {
        treasure[key] = updateData[key];
      }
    });
    
    await treasure.save();
    return treasure;
  } catch (error) {
    logger.error(`更新宝藏ID:${id}失败:`, error);
    
    if (error.statusCode) {
      throw error;
    }
    
    throw createError('更新宝藏失败', 500);
  }
};

/**
 * 删除宝藏
 * @param {String} id - 宝藏ID
 * @returns {Promise<Boolean>} 是否成功
 */
const deleteTreasure = async (id) => {
  try {
    const result = await Treasure.findByIdAndDelete(id);
    
    if (!result) {
      throw createError('宝藏不存在', 404);
    }
    
    return true;
  } catch (error) {
    logger.error(`删除宝藏ID:${id}失败:`, error);
    
    if (error.statusCode === 404) {
      throw error;
    }
    
    throw createError('删除宝藏失败', 500);
  }
};

/**
 * 通过AR标记ID扫描宝藏
 * @param {String} markerId - AR标记ID
 * @param {String} userId - 用户ID
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Object>} 扫描结果
 */
const scanARMarker = async (markerId, userId, mazeId) => {
  try {
    // 查找匹配的宝藏
    const treasure = await Treasure.findOne({
      'arMarker.markerId': markerId
    });
    
    if (!treasure) {
      throw createError('未找到匹配的AR标记', 404);
    }
    
    // 检查宝藏是否可用
    if (!treasure.isAvailable()) {
      throw createError('该宝藏不可用', 400);
    }
    
    // 检查用户是否已经发现过该宝藏
    const alreadyDiscovered = treasure.discoveredBy.some(
      d => d.userId === userId && d.mazeId.toString() === mazeId
    );
    
    if (alreadyDiscovered) {
      throw createError('您已经发现过该宝藏', 400);
    }
    
    // 返回宝藏信息
    return {
      treasure,
      isDiscovered: false,
      message: '发现新宝藏！'
    };
  } catch (error) {
    logger.error(`扫描AR标记ID:${markerId}失败:`, error);
    
    if (error.statusCode) {
      throw error;
    }
    
    throw createError('扫描AR标记失败', 500);
  }
};

/**
 * 收集宝藏
 * @param {String} treasureId - 宝藏ID
 * @param {String} userId - 用户ID
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Object>} 收集结果
 */
const collectTreasure = async (treasureId, userId, mazeId) => {
  try {
    const treasure = await Treasure.findById(treasureId);
    
    if (!treasure) {
      throw createError('宝藏不存在', 404);
    }
    
    // 检查宝藏是否可用
    if (!treasure.isAvailable()) {
      throw createError('该宝藏不可用', 400);
    }
    
    // 标记宝藏被发现
    const success = treasure.markDiscovered(userId, mazeId);
    
    if (!success) {
      throw createError('您已经收集过该宝藏', 400);
    }
    
    // 保存宝藏
    await treasure.save();
    
    // 返回收集结果
    return {
      treasure,
      collected: true,
      reward: {
        type: treasure.rewardType,
        value: treasure.value,
        name: treasure.name,
        description: treasure.description
      },
      message: `成功收集宝藏: ${treasure.name}`
    };
  } catch (error) {
    logger.error(`收集宝藏ID:${treasureId}失败:`, error);
    
    if (error.statusCode) {
      throw error;
    }
    
    throw createError('收集宝藏失败', 500);
  }
};

/**
 * 获取用户发现的宝藏
 * @param {String} userId - 用户ID
 * @param {Object} options - 查询选项
 * @returns {Promise<Array>} 宝藏列表
 */
const getUserDiscoveredTreasures = async (userId, options = {}) => {
  try {
    const { page = 1, limit = 10, mazeId = null } = options;
    const skip = (page - 1) * limit;
    
    // 构建查询条件
    const filter = {
      'discoveredBy.userId': userId
    };
    
    if (mazeId) {
      filter['discoveredBy.mazeId'] = mazeId;
    }
    
    // 查询宝藏
    const treasures = await Treasure.find(filter)
      .sort({ 'discoveredBy.discoveredAt': -1 })
      .skip(skip)
      .limit(limit);
    
    const total = await Treasure.countDocuments(filter);
    
    // 处理宝藏数据，添加发现信息
    const processedTreasures = treasures.map(treasure => {
      const discoveryInfo = treasure.discoveredBy.find(d => d.userId === userId);
      return {
        _id: treasure._id,
        name: treasure.name,
        description: treasure.description,
        rewardType: treasure.rewardType,
        rarity: treasure.rarity,
        value: treasure.value,
        imageUrl: treasure.imageUrl,
        discoveredAt: discoveryInfo ? discoveryInfo.discoveredAt : null,
        mazeId: discoveryInfo ? discoveryInfo.mazeId : null
      };
    });
    
    return {
      treasures: processedTreasures,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      }
    };
  } catch (error) {
    logger.error(`获取用户ID:${userId}发现的宝藏失败:`, error);
    throw createError('获取发现的宝藏失败', 500);
  }
};

/**
 * 获取宝藏统计信息
 * @param {String} seasonId - 季节ID
 * @returns {Promise<Object>} 统计信息
 */
const getTreasureStats = async (seasonId = null) => {
  try {
    // 构建查询条件
    const filter = {};
    if (seasonId) {
      filter.seasonId = seasonId;
    }
    
    // 总宝藏数
    const totalTreasures = await Treasure.countDocuments(filter);
    
    // 按类型统计
    const typeStats = await Treasure.aggregate([
      { $match: filter },
      { $group: { _id: '$rewardType', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);
    
    // 按稀有度统计
    const rarityStats = await Treasure.aggregate([
      { $match: filter },
      { $group: { _id: '$rarity', count: { $sum: 1 } } },
      { $sort: { _id: 1 } }
    ]);
    
    // 限量宝藏统计
    const limitedTreasures = await Treasure.countDocuments({
      ...filter,
      isLimited: true
    });
    
    // 剩余限量宝藏统计
    const remainingLimitedTreasures = await Treasure.aggregate([
      { $match: { ...filter, isLimited: true } },
      { $group: { _id: null, total: { $sum: '$remainingQuantity' } } }
    ]);
    
    return {
      totalTreasures,
      typeStats: typeStats.map(item => ({
        type: item._id,
        count: item.count
      })),
      rarityStats: rarityStats.map(item => ({
        rarity: item._id,
        count: item.count
      })),
      limitedTreasures,
      remainingLimitedTreasures: remainingLimitedTreasures.length > 0 ? 
        remainingLimitedTreasures[0].total : 0
    };
  } catch (error) {
    logger.error('获取宝藏统计信息失败:', error);
    throw createError('获取统计信息失败', 500);
  }
};

/**
 * 图像识别宝藏
 * @param {String|Buffer} imageData - 图像数据
 * @param {String} userId - 用户ID
 * @returns {Promise<Object>} 识别结果
 */
const scanImageTreasure = async (imageData, userId) => {
  try {
    // 使用图像识别API分析图像
    const recognitionResult = await imageRecognitionService.analyze(imageData);
    
    // 根据识别结果查找对应宝藏
    const treasures = await Treasure.find({ 
      'recognitionData.imageSignatures': { $in: recognitionResult.signatures },
      isActive: true 
    });
    
    if (treasures.length === 0) {
      return { success: false, message: '未识别到宝藏' };
    }
    
    // 返回识别到的宝藏信息
    return { 
      success: true, 
      treasures, 
      recognitionData: recognitionResult,
      message: `识别到${treasures.length}个宝藏！` 
    };
  } catch (error) {
    logger.error('图像识别宝藏失败', error);
    throw createError('图像识别处理失败', 500);
  }
};

/**
 * 地理位置发现宝藏
 * @param {Number} latitude - 纬度
 * @param {Number} longitude - 经度
 * @param {String} userId - 用户ID
 * @param {Number} radius - 搜索半径(米)
 * @returns {Promise<Object>} 搜索结果
 */
const discoverTreasuresByLocation = async (latitude, longitude, userId, radius = 50) => {
  try {
    // 查找指定范围内的地理位置宝藏
    const nearbyTreasures = await Treasure.find({
      location: {
        $near: {
          $geometry: {
            type: "Point",
            coordinates: [longitude, latitude]
          },
          $maxDistance: radius // 单位:米
        }
      },
      isActive: true
    });
    
    if (nearbyTreasures.length === 0) {
      return { success: false, message: '附近没有发现宝藏' };
    }
    
    return { 
      success: true, 
      treasures: nearbyTreasures, 
      count: nearbyTreasures.length,
      message: `在附近${radius}米范围内发现${nearbyTreasures.length}个宝藏！` 
    };
  } catch (error) {
    logger.error('地理位置宝藏查询失败', error);
    throw createError('地理位置服务异常', 500);
  }
};

/**
 * 使用手势收集宝藏
 * @param {String} treasureId - 宝藏ID
 * @param {String} userId - 用户ID
 * @param {Object} gestureData - 手势数据
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Object>} 收集结果
 */
const collectTreasureWithGesture = async (treasureId, userId, gestureData, mazeId) => {
  try {
    const treasure = await Treasure.findById(treasureId);
    
    if (!treasure) {
      throw createError('宝藏不存在', 404);
    }
    
    // 检查宝藏是否需要手势
    if (treasure.interactionType !== 'gesture') {
      throw createError('该宝藏不需要手势解锁', 400);
    }
    
    // 检查手势是否匹配
    if (treasure.gestureName !== gestureData.name) {
      return { success: false, message: '手势不匹配，请尝试其他手势' };
    }
    
    // 标记宝藏被发现
    const success = treasure.markDiscovered(userId, mazeId);
    
    if (!success) {
      throw createError('您已经收集过该宝藏', 400);
    }
    
    await treasure.save();
    
    // 发送实时通知
    await realTimeService.sendUserNotification(userId, {
      type: 'treasure_collected',
      title: '恭喜收集到宝藏！',
      message: `您成功使用${gestureData.name}手势收集了"${treasure.name}"`,
      treasureId: treasure._id
    });
    
    return {
      success: true,
      treasure,
      reward: {
        type: treasure.rewardType,
        value: treasure.value,
        rarity: treasure.rarity
      },
      message: `手势匹配成功！获得${treasure.name}`
    };
  } catch (error) {
    logger.error(`使用手势收集宝藏失败:${treasureId}`, error);
    
    if (error.statusCode) {
      throw error;
    }
    
    throw createError('收集宝藏失败', 500);
  }
};

/**
 * 分享宝藏
 * @param {String} treasureId - 宝藏ID
 * @param {String} fromUserId - 分享用户ID
 * @param {String} toUserId - 接收用户ID
 * @param {String} message - 分享消息
 * @returns {Promise<Object>} 分享结果
 */
const shareTreasure = async (treasureId, fromUserId, toUserId, message) => {
  try {
    const treasure = await Treasure.findById(treasureId);
    if (!treasure) {
      throw createError('宝藏不存在', 404);
    }
    
    // 检查宝藏是否可分享
    if (!treasure.isSharable()) {
      throw createError('该宝藏不可分享', 400);
    }
    
    // 创建宝藏分享记录
    const shareRecord = await TreasureShare.create({
      treasureId,
      fromUser: fromUserId,
      toUser: toUserId,
      message,
      sharedAt: new Date()
    });
    
    // 发送通知
    await notificationService.sendTreasureShareNotification(toUserId, fromUserId, treasure);
    
    // 实时通知接收用户
    await realTimeService.sendUserNotification(toUserId, {
      type: 'treasure_shared',
      title: '收到宝藏分享',
      message: `${fromUserId}向您分享了宝藏"${treasure.name}"`,
      treasureId: treasure._id,
      fromUserId
    });
    
    return { 
      success: true, 
      shareId: shareRecord._id,
      message: '宝藏分享成功'
    };
  } catch (error) {
    logger.error('宝藏分享失败', error);
    
    if (error.statusCode) {
      throw error;
    }
    
    throw createError('宝藏分享过程发生错误', 500);
  }
};

/**
 * 团队同步寻宝
 * @param {String} teamId - 团队ID
 * @param {String} mazeId - 迷宫ID
 * @param {String} initiatorId - 发起人ID
 * @returns {Promise<Object>} 团队寻宝结果
 */
const startTeamTreasureHunt = async (teamId, mazeId, initiatorId) => {
  try {
    // 验证团队和迷宫
    const team = await Team.findById(teamId);
    const maze = await Maze.findById(mazeId);
    
    if (!team || !maze) {
      throw createError('团队或迷宫不存在', 404);
    }
    
    // 检查用户是否为团队成员
    if (!team.members.includes(initiatorId)) {
      throw createError('您不是该团队成员', 403);
    }
    
    // 创建团队寻宝会话
    const huntSession = await TeamHuntSession.create({
      teamId,
      mazeId,
      startedBy: initiatorId,
      startedAt: new Date(),
      status: 'active',
      participants: team.members.map(member => ({
        userId: member,
        joinedAt: member === initiatorId ? new Date() : null,
        treasuresFound: []
      }))
    });
    
    // 实时通知团队成员
    await realTimeService.notifyTeamMembers(teamId, 'team_hunt_started', {
      sessionId: huntSession._id,
      mazeName: maze.name,
      initiator: initiatorId
    });
    
    return { 
      success: true, 
      sessionId: huntSession._id,
      message: '团队寻宝活动已开始'
    };
  } catch (error) {
    logger.error('团队寻宝启动失败', error);
    
    if (error.statusCode) {
      throw error;
    }
    
    throw createError('启动团队寻宝失败', 500);
  }
};

/**
 * 获取AR留言
 * @param {Number} latitude - 纬度
 * @param {Number} longitude - 经度
 * @param {Number} radius - 搜索半径(米)
 * @returns {Promise<Array>} 留言列表
 */
const getARMessages = async (latitude, longitude, radius = 100) => {
  try {
    // 查询指定地理位置附近的AR留言
    const messages = await ARMessage.find({
      location: {
        $near: {
          $geometry: {
            type: "Point",
            coordinates: [longitude, latitude]
          },
          $maxDistance: radius
        }
      },
      expiresAt: { $gt: new Date() }
    }).sort({ createdAt: -1 }).limit(20);
    
    return messages;
  } catch (error) {
    logger.error('获取AR留言失败', error);
    throw createError('获取AR留言失败', 500);
  }
};

/**
 * 创建AR留言
 * @param {Object} messageData - 留言数据
 * @returns {Promise<Object>} 创建的留言
 */
const createARMessage = async (messageData) => {
  try {
    const message = new ARMessage({
      ...messageData,
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7天后过期
    });
    
    await message.save();
    return message;
  } catch (error) {
    logger.error('创建AR留言失败', error);
    throw createError('创建AR留言失败', 500);
  }
};

// 导出所有函数
module.exports = {
  createTreasure,
  getAllTreasures,
  getTreasureById,
  updateTreasure,
  deleteTreasure,
  scanARMarker,
  collectTreasure,
  getUserDiscoveredTreasures,
  getTreasureStats,
  // 新增功能
  scanImageTreasure,
  discoverTreasuresByLocation,
  collectTreasureWithGesture,
  shareTreasure,
  startTeamTreasureHunt,
  getARMessages,
  createARMessage
};
