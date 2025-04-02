/**
 * AR功能控制器
 * 处理增强现实相关功能
 */
const treasureService = require('../services/treasureService');
const imageRecognitionService = require('../services/imageRecognitionService');
const notificationService = require('../services/notificationService');
const realTimeService = require('../services/realTimeService');
const { createError } = require('../middlewares/errorHandler');
const logger = require('../utils/logger');
const demoData = require('../utils/demo-data');

/**
 * 扫描图像识别宝藏
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const scanImage = async (req, res, next) => {
  try {
    // 检查是否有文件上传
    if (!req.file) {
      return next(createError('未上传图像', 400));
    }
    
    const imageData = req.file.buffer;
    const userId = req.user.id;
    
    // 调用服务层方法处理图像识别
    const result = await treasureService.scanImageTreasure(imageData, userId);
    
    // 记录活动
    logger.info(`用户 ${userId} 进行了图像识别扫描，结果: ${result.success ? '成功' : '失败'}`);
    
    // 返回识别结果
    res.json(result);
  } catch (error) {
    logger.error('图像扫描控制器错误:', error);
    next(error);
  }
};

/**
 * 基于地理位置发现宝藏
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const discoverByLocation = async (req, res, next) => {
  try {
    const { latitude, longitude, radius } = req.query;
    const userId = req.user.id;
    
    // 验证参数
    if (!latitude || !longitude) {
      return next(createError('缺少位置参数', 400));
    }
    
    // 调用服务层方法
    const result = await treasureService.discoverTreasuresByLocation(
      parseFloat(latitude),
      parseFloat(longitude),
      userId,
      radius ? parseInt(radius) : undefined
    );
    
    // 记录活动
    logger.info(`用户 ${userId} 在位置(${latitude},${longitude})发现了${result.treasures?.length || 0}个宝藏`);
    
    // 实时通知
    if (result.success && result.treasures.length > 0) {
      await realTimeService.sendUserNotification(userId, {
        type: 'location_treasures_found',
        count: result.treasures.length,
        location: { latitude, longitude }
      });
    }
    
    // 返回结果
    res.json(result);
  } catch (error) {
    logger.error('地理位置宝藏发现控制器错误:', error);
    next(error);
  }
};

/**
 * 使用手势收集宝藏
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const collectWithGesture = async (req, res, next) => {
  try {
    const treasureId = req.params.id;
    const userId = req.user.id;
    const { gestureData, mazeId } = req.body;
    
    // 验证参数
    if (!gestureData || !gestureData.name) {
      return next(createError('缺少手势数据', 400));
    }
    
    if (!mazeId) {
      return next(createError('缺少迷宫ID', 400));
    }
    
    // 调用服务层方法
    const result = await treasureService.collectTreasureWithGesture(
      treasureId,
      userId,
      gestureData,
      mazeId
    );
    
    // 记录活动
    logger.info(`用户 ${userId} 使用手势 ${gestureData.name} 收集宝藏 ${treasureId}`);
    
    // 转发成功收集的宝藏通知给团队成员
    if (result.success) {
      // 获取用户所在团队
      // 这里假设有一个服务可以获取用户的团队信息
      // const teams = await teamService.getUserTeams(userId);
      // if (teams.length > 0) {
      //   await realTimeService.notifyTeamMembers(teams[0].id, 'team_member_found_treasure', {
      //     userId,
      //     treasureId,
      //     treasureName: result.treasure.name,
      //     gesture: gestureData.name
      //   });
      // }
    }
    
    // 返回结果
    res.json(result);
  } catch (error) {
    logger.error('手势收集宝藏控制器错误:', error);
    next(error);
  }
};

/**
 * 分享宝藏给其他用户
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const shareTreasure = async (req, res, next) => {
  try {
    const treasureId = req.params.id;
    const fromUserId = req.user.id;
    const { toUserId, message } = req.body;
    
    // 验证参数
    if (!toUserId) {
      return next(createError('缺少接收用户ID', 400));
    }
    
    // 调用服务层方法
    const result = await treasureService.shareTreasure(
      treasureId,
      fromUserId,
      toUserId,
      message || ''
    );
    
    // 记录活动
    logger.info(`用户 ${fromUserId} 分享宝藏 ${treasureId} 给用户 ${toUserId}`);
    
    // 返回结果
    res.json(result);
  } catch (error) {
    logger.error('分享宝藏控制器错误:', error);
    next(error);
  }
};

/**
 * 开始团队同步寻宝活动
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const startTeamHunt = async (req, res, next) => {
  try {
    const teamId = req.params.teamId;
    const mazeId = req.params.mazeId;
    const initiatorId = req.user.id;
    
    // 调用服务层方法
    const result = await treasureService.startTeamTreasureHunt(
      teamId,
      mazeId,
      initiatorId
    );
    
    // 记录活动
    logger.info(`用户 ${initiatorId} 为团队 ${teamId} 在迷宫 ${mazeId} 启动了同步寻宝活动`);
    
    // 返回结果
    res.json(result);
  } catch (error) {
    logger.error('启动团队寻宝控制器错误:', error);
    next(error);
  }
};

/**
 * 获取附近的AR留言
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getNearbyMessages = async (req, res, next) => {
  try {
    const { latitude, longitude, radius } = req.query;
    
    // 验证参数
    if (!latitude || !longitude) {
      return next(createError('缺少位置参数', 400));
    }
    
    // 调用服务层方法
    const messages = await treasureService.getARMessages(
      parseFloat(latitude),
      parseFloat(longitude),
      radius ? parseInt(radius) : undefined
    );
    
    // 返回结果
    res.json({ success: true, messages });
  } catch (error) {
    logger.error('获取AR留言控制器错误:', error);
    next(error);
  }
};

/**
 * 创建AR留言
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const createMessage = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { text, latitude, longitude, imageUrl, isPublic, targetUsers, tags, mazeId } = req.body;
    
    // 验证参数
    if (!text || !latitude || !longitude) {
      return next(createError('缺少必要参数', 400));
    }
    
    // 构建消息数据
    const messageData = {
      userId,
      text,
      location: {
        type: 'Point',
        coordinates: [parseFloat(longitude), parseFloat(latitude)]
      },
      imageUrl,
      isPublic: isPublic !== undefined ? isPublic : true,
      targetUsers: targetUsers || [],
      tags: tags || [],
      mazeId
    };
    
    // 调用服务层方法
    const message = await treasureService.createARMessage(messageData);
    
    // 记录活动
    logger.info(`用户 ${userId} 在位置(${latitude},${longitude})创建了AR留言`);
    
    // 实时通知附近用户
    await broadcastMessageCreated(userId, message);
    
    // 返回结果
    res.status(201).json({ success: true, message });
  } catch (error) {
    logger.error('创建AR留言控制器错误:', error);
    next(error);
  }
};

/**
 * 广播新创建的留言给附近用户
 * @param {String} creatorId - 创建者ID
 * @param {Object} message - 留言对象
 */
const broadcastMessageCreated = async (creatorId, message) => {
  try {
    // 获取留言位置附近的房间
    const [longitude, latitude] = message.location.coordinates;
    const roomKey = `location:${Math.floor(latitude * 100) / 100},${Math.floor(longitude * 100) / 100}`;
    
    // 如果房间存在，广播消息
    if (realTimeService.roomExists(roomKey)) {
      await realTimeService.broadcastToRoom(roomKey, 'new_ar_message', {
        messageId: message._id,
        creatorId,
        text: message.text.substring(0, 50) + (message.text.length > 50 ? '...' : ''),
        location: {
          latitude,
          longitude
        },
        createdAt: message.createdAt
      });
    }
  } catch (error) {
    logger.error('广播新留言失败:', error);
  }
};

/**
 * 为AR功能加载演示数据
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const loadDemoData = async (req, res, next) => {
  try {
    // 仅允许管理员访问
    if (req.user.role !== 'admin') {
      return next(createError('无权访问', 403));
    }
    
    // 获取要加载的数据类型
    const { dataType } = req.params;
    let result;
    
    // 根据类型加载不同的演示数据
    switch (dataType) {
      case 'images':
        result = demoData.generateARImageData();
        break;
      case 'gestures':
        result = demoData.generateGestureData();
        break;
      case 'locations':
        result = demoData.generateLocationTreasures();
        break;
      case 'treasures':
        result = demoData.generateARTreasures();
        // 将示例宝藏数据存入数据库
        for (const treasure of result) {
          await treasureService.createTreasure(treasure);
        }
        break;
      case 'social':
        result = demoData.generateSocialInteractionData();
        break;
      default:
        return next(createError('未知的数据类型', 400));
    }
    
    // 记录活动
    logger.info(`管理员 ${req.user.id} 加载了 ${dataType} 类型的演示数据`);
    
    // 返回结果
    res.json({ success: true, data: result });
  } catch (error) {
    logger.error('加载演示数据控制器错误:', error);
    next(error);
  }
};

module.exports = {
  scanImage,
  discoverByLocation,
  collectWithGesture,
  shareTreasure,
  startTeamHunt,
  getNearbyMessages,
  createMessage,
  loadDemoData
}; 