/**
 * AR增强控制器
 * 处理AR相关的各种请求，包括图像识别、地理位置探索、手势互动等
 */
const mongoose = require('mongoose');
const Treasure = require('../models/treasure.model');
const ARMessage = require('../models/arMessage.model');
const Team = require('../models/team.model');
const logger = require('../utils/logger');
const { createError } = require('../middlewares/errorHandler');
const npcService = require('../services/npc/npcService');
const treasureService = require('../services/treasureService');
const socketService = require('../services/socketService');

// 导入实用工具
const { calculateDistance } = require('../utils/geoUtils');
const { detectGesture } = require('../utils/gestureDetection');
const { analyzeImage } = require('../utils/imageAnalysis');

/**
 * AR控制器类
 */
class ARController {
  /**
   * 扫描图像识别宝藏
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async scanImage(req, res, next) {
    try {
      const { userId } = req.user;
      const { image, location } = req.body;

      if (!image) {
        return next(createError('图像数据不能为空', 400));
      }

      // 分析图像
      const imageAnalysisResult = await analyzeImage(image);
      
      // 搜索匹配的宝藏
      const treasures = await treasureService.scanImageTreasure(imageAnalysisResult, location);
      
      // 记录扫描活动
      logger.info(`用户[${userId}]进行图像扫描`, {
        treasuresFound: treasures.length,
        location
      });
      
      // 实时通知团队成员
      await this.notifyTeamMembersAboutScan(userId, treasures, location);

      res.status(200).json({
        success: true,
        treasures,
        confidence: imageAnalysisResult.confidence
      });
    } catch (error) {
      logger.error('图像扫描失败', error);
      next(createError('图像扫描处理失败: ' + error.message, 500));
    }
  }

  /**
   * 基于地理位置发现宝藏
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async discoverByLocation(req, res, next) {
    try {
      const { userId } = req.user;
      const { latitude, longitude, accuracy } = req.query;
      
      if (!latitude || !longitude) {
        return next(createError('位置坐标不能为空', 400));
      }
      
      const coordinates = [parseFloat(longitude), parseFloat(latitude)];
      const locationAccuracy = parseFloat(accuracy) || 10; // 默认10米精度
      
      // 获取附近的宝藏
      const treasures = await treasureService.discoverTreasuresByLocation(
        coordinates, 
        locationAccuracy,
        userId
      );
      
      // 检查是否有活跃的迷宫区域
      const mazeInfo = await this.checkActiveMazeAtLocation(coordinates);
      
      // 记录位置探索
      logger.info(`用户[${userId}]进行位置探索`, {
        coordinates,
        accuracy: locationAccuracy,
        treasuresFound: treasures.length,
        mazeId: mazeInfo?.mazeId
      });
      
      // 获取附近的AR消息
      const nearbyMessages = await this.getNearbyARMessages(coordinates, 50);
      
      // 检查是否有NPC在此位置
      const npcInteraction = await this.checkNPCAtLocation(coordinates, userId);
      
      res.status(200).json({
        success: true,
        treasures,
        messages: nearbyMessages,
        mazeInfo,
        npcInteraction
      });
    } catch (error) {
      logger.error('位置发现失败', error);
      next(createError('位置探索处理失败: ' + error.message, 500));
    }
  }

  /**
   * 使用手势收集宝藏
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async collectWithGesture(req, res, next) {
    try {
      const { userId } = req.user;
      const { treasureId } = req.params;
      const { gestureData, location } = req.body;
      
      if (!treasureId || !gestureData) {
        return next(createError('宝藏ID和手势数据不能为空', 400));
      }
      
      // 分析手势
      const gestureResult = await detectGesture(gestureData);
      
      // 尝试用手势收集宝藏
      const result = await treasureService.collectTreasureWithGesture(
        treasureId,
        userId,
        gestureResult.gestureName,
        location
      );
      
      if (!result.success) {
        return res.status(200).json({
          success: false,
          message: result.message
        });
      }
      
      // 实时通知团队成员
      await this.notifyTeamMembersAboutCollection(userId, result.treasure);
      
      res.status(200).json({
        success: true,
        treasure: result.treasure,
        rewards: result.rewards,
        gestureRecognized: gestureResult.gestureName,
        confidence: gestureResult.confidence
      });
    } catch (error) {
      logger.error('手势收集失败', error);
      next(createError('手势收集处理失败: ' + error.message, 500));
    }
  }

  /**
   * 启动团队寻宝
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async startTeamTreasureHunt(req, res, next) {
    try {
      const { userId } = req.user;
      const { teamId, mazeId } = req.params;
      const { duration, maxTreasures } = req.body;
      
      // 验证团队存在并且用户是成员
      const team = await Team.findOne({
        _id: teamId,
        members: { $elemMatch: { userId } }
      });
      
      if (!team) {
        return next(createError('团队不存在或您不是团队成员', 404));
      }
      
      // 启动团队寻宝会话
      const huntSession = await treasureService.startTeamTreasureHunt(
        teamId,
        mazeId,
        {
          initiatedBy: userId,
          duration: duration || 60, // 默认60分钟
          maxTreasures: maxTreasures || 10
        }
      );
      
      // 通过WebSocket通知所有团队成员
      team.members.forEach(member => {
        socketService.emitToUser(member.userId, 'team-hunt-started', {
          teamId,
          mazeId,
          huntSession
        });
      });
      
      res.status(200).json({
        success: true,
        huntSession
      });
    } catch (error) {
      logger.error('启动团队寻宝失败', error);
      next(createError('启动团队寻宝失败: ' + error.message, 500));
    }
  }

  /**
   * 分享宝藏
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async shareTreasure(req, res, next) {
    try {
      const { userId } = req.user;
      const { treasureId } = req.params;
      const { receiverId, message } = req.body;
      
      if (!treasureId || !receiverId) {
        return next(createError('宝藏ID和接收者ID不能为空', 400));
      }
      
      // 分享宝藏
      const result = await treasureService.shareTreasure(
        treasureId,
        userId,
        receiverId,
        message
      );
      
      if (!result.success) {
        return res.status(200).json({
          success: false,
          message: result.message
        });
      }
      
      // 发送实时通知
      socketService.emitToUser(receiverId, 'treasure-shared', {
        treasureId,
        sharedBy: userId,
        message,
        timestamp: new Date()
      });
      
      res.status(200).json({
        success: true,
        sharedTreasure: result.sharedTreasure
      });
    } catch (error) {
      logger.error('分享宝藏失败', error);
      next(createError('分享宝藏失败: ' + error.message, 500));
    }
  }

  /**
   * 创建AR留言
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async createARMessage(req, res, next) {
    try {
      const { userId } = req.user;
      const { content, location, visibility, expiresIn } = req.body;
      
      if (!content || !location || !location.coordinates) {
        return next(createError('留言内容和位置不能为空', 400));
      }
      
      // 创建新的AR留言
      const arMessage = new ARMessage({
        userId,
        content,
        location: {
          type: 'Point',
          coordinates: location.coordinates
        },
        visibility: visibility || 'public',
        expires: expiresIn ? new Date(Date.now() + expiresIn * 60000) : null
      });
      
      await arMessage.save();
      
      // 通知附近的用户
      await this.notifyNearbyUsersAboutMessage(arMessage);
      
      res.status(201).json({
        success: true,
        message: arMessage
      });
    } catch (error) {
      logger.error('创建AR留言失败', error);
      next(createError('创建AR留言失败: ' + error.message, 500));
    }
  }

  /**
   * 获取附近的AR留言
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async getNearbyARMessages(req, res, next) {
    try {
      const { userId } = req.user;
      const { longitude, latitude, radius } = req.query;
      
      if (!longitude || !latitude) {
        return next(createError('位置坐标不能为空', 400));
      }
      
      const coordinates = [parseFloat(longitude), parseFloat(latitude)];
      const searchRadius = parseFloat(radius) || 100; // 默认100米
      
      // 查询附近的留言
      const messages = await ARMessage.find({
        'location.coordinates': {
          $nearSphere: {
            $geometry: {
              type: 'Point',
              coordinates
            },
            $maxDistance: searchRadius
          }
        },
        $or: [
          { visibility: 'public' },
          { userId },
          { 'teams.teamId': { $in: await this.getUserTeams(userId) } }
        ],
        expires: { $gt: new Date() }
      }).populate('userId', 'username avatar').sort({ createdAt: -1 });
      
      res.status(200).json({
        success: true,
        messages
      });
    } catch (error) {
      logger.error('获取附近AR留言失败', error);
      next(createError('获取附近AR留言失败: ' + error.message, 500));
    }
  }

  /**
   * 与NPC交互
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async interactWithNPC(req, res, next) {
    try {
      const { userId } = req.user;
      const { message, npcId, sessionId, location } = req.body;
      
      if (!message) {
        return next(createError('消息内容不能为空', 400));
      }
      
      // 创建交互上下文
      const context = {
        sessionId,
        location,
        timestamp: new Date()
      };
      
      // 调用NPC服务进行交互
      const response = await npcService.interact(userId, npcId || 'laoke', message, context);
      
      // 查看是否有任务触发
      let quest = null;
      if (response.quest) {
        quest = response.quest;
      }
      
      res.status(200).json({
        success: true,
        response: response.message,
        actions: response.actions,
        quest,
        npcId: npcId || 'laoke',
        sessionId: response.sessionId || sessionId
      });
    } catch (error) {
      logger.error('NPC交互失败', error);
      next(createError('NPC交互失败: ' + error.message, 500));
    }
  }

  /**
   * 提交环境扫描数据
   * @param {Object} req - 请求对象
   * @param {Object} res - 响应对象
   * @param {Function} next - 下一个中间件
   */
  async submitEnvironmentScan(req, res, next) {
    try {
      const { userId } = req.user;
      const { scanData, location, deviceInfo } = req.body;
      
      if (!scanData || !location) {
        return next(createError('扫描数据和位置不能为空', 400));
      }
      
      // 处理环境扫描数据
      // 这里可以保存点云数据、环境光线信息等
      
      // 检查是否有与位置相关的任务
      const locationTasks = await this.checkLocationTasks(userId, location.coordinates);
      
      res.status(200).json({
        success: true,
        message: '环境数据已接收',
        locationTasks
      });
    } catch (error) {
      logger.error('提交环境扫描失败', error);
      next(createError('提交环境扫描失败: ' + error.message, 500));
    }
  }

  /**
   * 检查位置任务
   * @param {string} userId - 用户ID
   * @param {Array} coordinates - 坐标 [longitude, latitude]
   * @returns {Promise<Array>} - 返回任务列表
   */
  async checkLocationTasks(userId, coordinates) {
    try {
      const Quest = mongoose.model('Quest');
      
      // 查找与位置相关的任务
      return await Quest.find({
        userId,
        status: { $in: ['active', 'in_progress'] },
        'locationRestriction.enabled': true,
        'locationRestriction.center.coordinates': {
          $nearSphere: {
            $geometry: {
              type: 'Point',
              coordinates
            },
            $maxDistance: '$locationRestriction.radius'
          }
        }
      }).lean();
    } catch (error) {
      logger.error('检查位置任务失败', error);
      return [];
    }
  }

  /**
   * 检查活跃迷宫
   * @param {Array} coordinates - 坐标 [longitude, latitude]
   * @returns {Promise<Object>} - 返回迷宫信息
   */
  async checkActiveMazeAtLocation(coordinates) {
    try {
      const Maze = mongoose.model('Maze');
      
      // 查找用户所在位置的迷宫
      const maze = await Maze.findOne({
        isActive: true,
        'boundary.type': 'Polygon',
        'boundary.coordinates': {
          $geoIntersects: {
            $geometry: {
              type: 'Point',
              coordinates
            }
          }
        }
      }).select('_id name difficulty currentLevel treasureCount').lean();
      
      if (!maze) {
        return null;
      }
      
      return {
        mazeId: maze._id,
        name: maze.name,
        difficulty: maze.difficulty,
        level: maze.currentLevel,
        treasureCount: maze.treasureCount
      };
    } catch (error) {
      logger.error('检查活跃迷宫失败', error);
      return null;
    }
  }

  /**
   * 获取附近的AR消息
   * @param {Array} coordinates - 坐标 [longitude, latitude]
   * @param {number} radius - 半径（米）
   * @returns {Promise<Array>} - 返回消息列表
   */
  async getNearbyARMessages(coordinates, radius = 50) {
    try {
      // 查询附近的公开留言
      return await ARMessage.find({
        'location.coordinates': {
          $nearSphere: {
            $geometry: {
              type: 'Point',
              coordinates
            },
            $maxDistance: radius
          }
        },
        visibility: 'public',
        expires: { $gt: new Date() }
      }).populate('userId', 'username avatar').sort({ createdAt: -1 }).limit(10).lean();
    } catch (error) {
      logger.error('获取附近AR消息失败', error);
      return [];
    }
  }

  /**
   * 检查位置处是否有NPC
   * @param {Array} coordinates - 坐标 [longitude, latitude]
   * @param {string} userId - 用户ID
   * @returns {Promise<Object>} - 返回NPC交互信息
   */
  async checkNPCAtLocation(coordinates, userId) {
    try {
      // 检查是否有NPC预设在该位置
      // 这里可以实现复杂的NPC位置逻辑
      
      // 简单示例：检查是否在老克的活动范围内
      const NPCLocation = mongoose.model('NPCLocation');
      
      const npcLocation = await NPCLocation.findOne({
        npcId: 'laoke',
        isActive: true,
        'location.coordinates': {
          $nearSphere: {
            $geometry: {
              type: 'Point',
              coordinates
            },
            $maxDistance: 50 // 50米范围内
          }
        }
      }).lean();
      
      if (!npcLocation) {
        return null;
      }
      
      // 获取NPC的问候语
      const greeting = await npcService.getNPCGreeting('laoke', userId);
      
      return {
        npcId: 'laoke',
        greeting,
        distance: calculateDistance(
          coordinates[1], coordinates[0],
          npcLocation.location.coordinates[1], npcLocation.location.coordinates[0]
        ),
        available: true
      };
    } catch (error) {
      logger.error('检查NPC位置失败', error);
      return null;
    }
  }

  /**
   * 通知团队成员有关扫描
   * @param {string} userId - 用户ID
   * @param {Array} treasures - 宝藏列表
   * @param {Object} location - 位置信息
   */
  async notifyTeamMembersAboutScan(userId, treasures, location) {
    try {
      if (treasures.length === 0) return;
      
      // 获取用户所在的活跃团队
      const userTeams = await Team.find({
        members: { $elemMatch: { userId, isActive: true } },
        isActive: true
      }).select('_id members').lean();
      
      if (userTeams.length === 0) return;
      
      // 为每个团队发送通知
      userTeams.forEach(team => {
        const teamMembers = team.members
          .filter(member => member.userId.toString() !== userId.toString() && member.isActive);
        
        teamMembers.forEach(member => {
          socketService.emitToUser(member.userId, 'team-member-scan', {
            userId,
            treasures: treasures.map(t => ({
              id: t._id,
              name: t.name,
              rarity: t.rarity
            })),
            location,
            teamId: team._id,
            timestamp: new Date()
          });
        });
      });
    } catch (error) {
      logger.error('通知团队成员有关扫描失败', error);
      // 失败不应影响主流程
    }
  }

  /**
   * 通知团队成员有关收集
   * @param {string} userId - 用户ID
   * @param {Object} treasure - 宝藏对象
   */
  async notifyTeamMembersAboutCollection(userId, treasure) {
    try {
      // 获取用户所在的活跃团队
      const userTeams = await Team.find({
        members: { $elemMatch: { userId, isActive: true } },
        isActive: true
      }).select('_id members').lean();
      
      if (userTeams.length === 0) return;
      
      // 为每个团队发送通知
      userTeams.forEach(team => {
        const teamMembers = team.members
          .filter(member => member.userId.toString() !== userId.toString() && member.isActive);
        
        teamMembers.forEach(member => {
          socketService.emitToUser(member.userId, 'team-member-collection', {
            userId,
            treasure: {
              id: treasure._id,
              name: treasure.name,
              rarity: treasure.rarity
            },
            teamId: team._id,
            timestamp: new Date()
          });
        });
      });
    } catch (error) {
      logger.error('通知团队成员有关收集失败', error);
      // 失败不应影响主流程
    }
  }

  /**
   * 通知附近用户有关新消息
   * @param {Object} message - AR消息对象
   */
  async notifyNearbyUsersAboutMessage(message) {
    try {
      // 获取附近的用户
      const onlineUsers = socketService.getOnlineUsers();
      const nearbyUsers = [];
      
      // 筛选在附近的用户
      for (const userId of onlineUsers) {
        const userLocation = socketService.getUserLocation(userId);
        
        if (userLocation && calculateDistance(
          userLocation.latitude, userLocation.longitude,
          message.location.coordinates[1], message.location.coordinates[0]
        ) <= 100) { // 100米范围内
          nearbyUsers.push(userId);
        }
      }
      
      // 通知每个附近的用户
      nearbyUsers.forEach(userId => {
        socketService.emitToUser(userId, 'nearby-ar-message', {
          messageId: message._id,
          content: message.content,
          createdBy: message.userId,
          location: message.location,
          timestamp: message.createdAt
        });
      });
    } catch (error) {
      logger.error('通知附近用户有关新消息失败', error);
      // 失败不应影响主流程
    }
  }

  /**
   * 获取用户所在的团队ID列表
   * @param {string} userId - 用户ID
   * @returns {Promise<Array>} - 返回团队ID列表
   */
  async getUserTeams(userId) {
    try {
      const teams = await Team.find({
        members: { $elemMatch: { userId } }
      }).select('_id').lean();
      
      return teams.map(team => team._id);
    } catch (error) {
      logger.error('获取用户团队失败', error);
      return [];
    }
  }
}

module.exports = new ARController(); 