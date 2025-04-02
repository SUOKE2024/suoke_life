/**
 * 离线服务
 * 提供离线功能支持和数据同步
 */
const logger = require('../utils/logger');
const { createError } = require('../middlewares/errorHandler');
const { getRedisClient } = require('../config/redis');
const crypto = require('crypto');
const Maze = require('../models/maze.model');
const Team = require('../models/team.model');

// 同步状态枚举
const SYNC_STATUS = {
  PENDING: 'pending',
  SYNCING: 'syncing',
  COMPLETED: 'completed',
  FAILED: 'failed'
};

// 同步操作类型
const SYNC_OPERATION = {
  CREATE: 'create',
  UPDATE: 'update',
  DELETE: 'delete'
};

// 每批同步的最大记录数
const MAX_BATCH_SIZE = 50;

/**
 * 生成离线包数据
 * @param {String} userId - 用户ID
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Object>} 离线包数据
 */
const generateOfflinePackage = async (userId, mazeId) => {
  try {
    logger.info(`为用户${userId}生成迷宫${mazeId}的离线包`);
    
    // 获取迷宫数据
    const maze = await Maze.findById(mazeId)
      .select('name description difficulty width height grid compressedGrid startPosition endPosition treasurePositions specialZones theme')
      .lean();
    
    if (!maze) {
      throw createError('迷宫不存在', 404);
    }
    
    // 获取玩家的团队数据
    const team = await Team.findOne({
      mazeId,
      'players.userId': userId,
      status: { $in: ['waiting', 'in_progress'] }
    }).lean();
    
    // 生成版本哈希，用于同步检查
    const versionHash = generateVersionHash(maze, team);
    
    // 构建离线包
    const offlinePackage = {
      version: versionHash,
      timestamp: Date.now(),
      maze: {
        ...maze,
        // 解压缩迷宫数据以便离线使用
        grid: maze.compressedGrid ? decompressGrid(maze.compressedGrid, maze.width, maze.height) : maze.grid
      },
      team: team ? sanitizeTeamData(team) : null,
      assetsUrls: await getAssetsUrls(maze),
      configData: getConfigData()
    };
    
    // 删除不必要的压缩数据
    delete offlinePackage.maze.compressedGrid;
    
    // 存储离线包版本记录用于后续同步
    await storeOfflinePackageVersion(userId, mazeId, versionHash);
    
    return offlinePackage;
  } catch (error) {
    logger.error(`生成离线包失败: ${userId}, ${mazeId}`, error);
    throw createError('生成离线包失败', 500);
  }
};

/**
 * 生成版本哈希
 * @param {Object} maze - 迷宫数据
 * @param {Object} team - 团队数据
 * @returns {String} 版本哈希
 */
const generateVersionHash = (maze, team) => {
  const data = JSON.stringify({
    maze: {
      _id: maze._id,
      updatedAt: maze.updatedAt
    },
    team: team ? {
      _id: team._id,
      updatedAt: team.updatedAt,
      players: team.players.map(p => ({
        userId: p.userId,
        updatedAt: p.updatedAt
      }))
    } : null
  });
  
  return crypto.createHash('md5').update(data).digest('hex');
};

/**
 * 存储离线包版本记录
 * @param {String} userId - 用户ID
 * @param {String} mazeId - 迷宫ID
 * @param {String} versionHash - 版本哈希
 * @returns {Promise<void>}
 */
const storeOfflinePackageVersion = async (userId, mazeId, versionHash) => {
  const redisClient = getRedisClient();
  const key = `offline:version:${userId}:${mazeId}`;
  
  await redisClient.set(key, JSON.stringify({
    versionHash,
    timestamp: Date.now()
  }));
  
  // 设置一周过期时间
  await redisClient.expire(key, 7 * 24 * 60 * 60);
};

/**
 * 检查离线包是否需要更新
 * @param {String} userId - 用户ID
 * @param {String} mazeId - 迷宫ID
 * @param {String} clientVersionHash - 客户端版本哈希
 * @returns {Promise<Boolean>} 是否需要更新
 */
const checkOfflinePackageUpdates = async (userId, mazeId, clientVersionHash) => {
  try {
    const redisClient = getRedisClient();
    const key = `offline:version:${userId}:${mazeId}`;
    
    const versionData = await redisClient.get(key);
    if (!versionData) {
      return true; // 找不到版本记录，需要更新
    }
    
    const { versionHash } = JSON.parse(versionData);
    return versionHash !== clientVersionHash;
  } catch (error) {
    logger.error(`检查离线包更新失败: ${userId}, ${mazeId}`, error);
    return true; // 出错时默认需要更新
  }
};

/**
 * 净化团队数据（减少数据量）
 * @param {Object} team - 团队数据
 * @returns {Object} 净化后的团队数据
 */
const sanitizeTeamData = (team) => {
  // 仅保留离线所需的团队数据
  const { _id, name, code, mazeId, status, players, progress, settings } = team;
  
  return {
    _id, name, code, mazeId, status, 
    players: players.map(({ userId, name, avatarUrl, role, treasuresFound, isActive, position }) => ({
      userId, name, avatarUrl, role, treasuresFound, isActive, position
    })),
    progress: progress ? {
      startedAt: progress.startedAt,
      lastActiveAt: progress.lastActiveAt,
      completedPercentage: progress.completedPercentage
    } : null,
    settings: {
      allowJoinRequests: settings?.allowJoinRequests || false,
      isPrivate: settings?.isPrivate || false
    }
  };
};

/**
 * 获取迷宫相关资源URL
 * @param {Object} maze - 迷宫数据
 * @returns {Promise<Array>} 资源URL列表
 */
const getAssetsUrls = async (maze) => {
  // 这里是简化实现，实际项目中应该根据迷宫内容动态生成资源列表
  // 包括主题图片、特殊区域图片、宝藏图片等
  
  const assets = [
    `/assets/themes/${maze.theme}/background.jpg`,
    `/assets/themes/${maze.theme}/wall.png`,
    `/assets/themes/${maze.theme}/path.png`,
    `/assets/common/treasures/chest.png`,
    `/assets/common/ui/compass.png`,
    `/assets/common/ui/map.png`
  ];
  
  // 添加特殊区域资源
  if (maze.specialZones && maze.specialZones.length > 0) {
    for (const zone of maze.specialZones) {
      assets.push(`/assets/special-zones/${zone.type}.png`);
    }
  }
  
  return assets;
};

/**
 * 获取离线配置数据
 * @returns {Object} 配置数据
 */
const getConfigData = () => {
  return {
    offlineMode: {
      maxTimeWithoutSync: 7 * 24 * 60 * 60 * 1000, // 最长离线时间（1周）
      syncRetryInterval: 5 * 60 * 1000, // 重试同步间隔（5分钟）
      autoSyncInterval: 30 * 60 * 1000, // 自动同步间隔（30分钟）
      maxStorageSize: 50 * 1024 * 1024, // 最大存储空间（50MB）
    },
    gameRules: {
      treasureDiscoveryRadius: 5, // 宝藏发现半径
      pointsPerTreasure: 100, // 每个宝藏的分数
      gameCompletionBonus: 500, // 完成游戏奖励
    }
  };
};

/**
 * 解压缩迷宫网格数据
 * @param {String} compressedGrid - 压缩的迷宫网格数据
 * @param {Number} width - 迷宫宽度
 * @param {Number} height - 迷宫高度
 * @returns {Array} 解压缩后的二维网格数组
 */
const decompressGrid = (compressedGrid, width, height) => {
  if (!compressedGrid) return null;
  
  try {
    // 解析Run-Length编码的数据
    const chunks = compressedGrid.split(',');
    const grid = Array(height).fill().map(() => Array(width).fill(0));
    
    let row = 0;
    let col = 0;
    
    for (const chunk of chunks) {
      const [count, value] = chunk.split(':');
      const countNum = parseInt(count, 10);
      const valueNum = parseInt(value, 10);
      
      for (let i = 0; i < countNum; i++) {
        grid[row][col] = valueNum;
        col++;
        
        if (col >= width) {
          col = 0;
          row++;
        }
      }
    }
    
    return grid;
  } catch (error) {
    logger.error(`解压缩迷宫数据失败`, error);
    return null;
  }
};

/**
 * 保存离线更改队列
 * @param {String} userId - 用户ID
 * @param {Array} changes - 更改队列
 * @returns {Promise<Object>} 保存结果
 */
const saveOfflineChanges = async (userId, changes) => {
  try {
    if (!Array.isArray(changes) || changes.length === 0) {
      return { success: true, synced: 0, pending: 0 };
    }
    
    logger.info(`保存用户${userId}的${changes.length}个离线更改`);
    
    const redisClient = getRedisClient();
    const key = `offline:changes:${userId}`;
    
    // 获取现有的更改队列
    let existingChanges = [];
    const existingData = await redisClient.get(key);
    
    if (existingData) {
      existingChanges = JSON.parse(existingData);
    }
    
    // 添加时间戳和状态
    const timestampedChanges = changes.map(change => ({
      ...change,
      timestamp: Date.now(),
      status: SYNC_STATUS.PENDING,
      retryCount: 0
    }));
    
    // 合并更改队列
    const mergedChanges = [...existingChanges, ...timestampedChanges];
    
    // 保存更改队列
    await redisClient.set(key, JSON.stringify(mergedChanges));
    
    // 设置一个月过期时间
    await redisClient.expire(key, 30 * 24 * 60 * 60);
    
    // 尝试同步更改
    const syncResult = await syncOfflineChanges(userId);
    
    return {
      success: true,
      synced: syncResult.synced,
      pending: syncResult.pending,
      failed: syncResult.failed
    };
  } catch (error) {
    logger.error(`保存离线更改失败: ${userId}`, error);
    throw createError('保存离线更改失败', 500);
  }
};

/**
 * 同步离线更改
 * @param {String} userId - 用户ID
 * @returns {Promise<Object>} 同步结果
 */
const syncOfflineChanges = async (userId) => {
  try {
    logger.info(`开始同步用户${userId}的离线更改`);
    
    const redisClient = getRedisClient();
    const key = `offline:changes:${userId}`;
    
    // 获取更改队列
    const data = await redisClient.get(key);
    if (!data) {
      return { synced: 0, pending: 0, failed: 0 };
    }
    
    const changes = JSON.parse(data);
    if (changes.length === 0) {
      return { synced: 0, pending: 0, failed: 0 };
    }
    
    // 过滤出待同步的更改
    const pendingChanges = changes.filter(
      change => change.status === SYNC_STATUS.PENDING || 
                (change.status === SYNC_STATUS.FAILED && change.retryCount < 3)
    );
    
    if (pendingChanges.length === 0) {
      return { 
        synced: changes.filter(c => c.status === SYNC_STATUS.COMPLETED).length,
        pending: 0,
        failed: changes.filter(c => c.status === SYNC_STATUS.FAILED).length
      };
    }
    
    // 按照资源类型和操作类型分组
    const changesByResource = {};
    
    for (const change of pendingChanges) {
      const key = `${change.resource}:${change.resourceId}`;
      if (!changesByResource[key]) {
        changesByResource[key] = [];
      }
      changesByResource[key].push(change);
    }
    
    // 按资源同步更改
    let syncedCount = 0;
    let failedCount = 0;
    
    for (const resourceChanges of Object.values(changesByResource)) {
      try {
        // 按时间戳排序
        resourceChanges.sort((a, b) => a.timestamp - b.timestamp);
        
        // 每次只同步一部分，避免请求过大
        const batchToSync = resourceChanges.slice(0, MAX_BATCH_SIZE);
        
        // 根据资源类型处理
        for (const change of batchToSync) {
          // 更新状态为同步中
          change.status = SYNC_STATUS.SYNCING;
          
          // 根据资源类型调用相应的处理函数
          let syncSuccess = false;
          
          switch (change.resource) {
            case 'playerPosition':
              syncSuccess = await syncPlayerPosition(userId, change);
              break;
            case 'treasureFound':
              syncSuccess = await syncTreasureFound(userId, change);
              break;
            case 'teamProgress':
              syncSuccess = await syncTeamProgress(userId, change);
              break;
            default:
              logger.warn(`未知的资源类型: ${change.resource}`);
              change.status = SYNC_STATUS.FAILED;
              change.error = '未知的资源类型';
              failedCount++;
              continue;
          }
          
          if (syncSuccess) {
            change.status = SYNC_STATUS.COMPLETED;
            change.syncedAt = Date.now();
            syncedCount++;
          } else {
            change.status = SYNC_STATUS.FAILED;
            change.retryCount = (change.retryCount || 0) + 1;
            failedCount++;
          }
        }
      } catch (error) {
        logger.error(`同步资源更改失败`, error);
        
        // 标记该批次更改为失败
        for (const change of resourceChanges) {
          if (change.status === SYNC_STATUS.SYNCING) {
            change.status = SYNC_STATUS.FAILED;
            change.retryCount = (change.retryCount || 0) + 1;
            change.error = error.message;
            failedCount++;
          }
        }
      }
    }
    
    // 更新更改队列
    await redisClient.set(key, JSON.stringify(changes));
    
    // 清理已完成的旧更改（超过7天）
    const oneWeekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
    const filteredChanges = changes.filter(change => 
      change.status !== SYNC_STATUS.COMPLETED || change.syncedAt > oneWeekAgo
    );
    
    if (filteredChanges.length !== changes.length) {
      await redisClient.set(key, JSON.stringify(filteredChanges));
    }
    
    return {
      synced: syncedCount,
      pending: pendingChanges.length - syncedCount - failedCount,
      failed: failedCount
    };
  } catch (error) {
    logger.error(`同步离线更改失败: ${userId}`, error);
    throw createError('同步离线更改失败', 500);
  }
};

/**
 * 同步玩家位置
 * @param {String} userId - 用户ID
 * @param {Object} change - 更改数据
 * @returns {Promise<Boolean>} 是否成功
 */
const syncPlayerPosition = async (userId, change) => {
  try {
    const { resourceId, data } = change;
    
    if (!data || !data.position || !data.position.x || !data.position.y) {
      return false;
    }
    
    // 更新团队中玩家的位置
    const result = await Team.updateOne(
      { 
        _id: resourceId,
        'players.userId': userId
      },
      { 
        $set: {
          'players.$.position': data.position,
          'players.$.lastActive': new Date()
        } 
      }
    );
    
    return result.modifiedCount > 0;
  } catch (error) {
    logger.error(`同步玩家位置失败: ${userId}`, error);
    return false;
  }
};

/**
 * 同步宝藏发现
 * @param {String} userId - 用户ID
 * @param {Object} change - 更改数据
 * @returns {Promise<Boolean>} 是否成功
 */
const syncTreasureFound = async (userId, change) => {
  try {
    const { resourceId, data } = change;
    
    if (!data || !data.treasureId) {
      return false;
    }
    
    // 检查宝藏是否已在玩家的发现列表中
    const team = await Team.findOne({
      _id: resourceId,
      'players.userId': userId,
      'players.treasuresFound': data.treasureId
    });
    
    if (team) {
      return true; // 已经同步过了
    }
    
    // 更新团队中玩家发现的宝藏
    const result = await Team.updateOne(
      { 
        _id: resourceId,
        'players.userId': userId
      },
      { 
        $addToSet: {
          'players.$.treasuresFound': data.treasureId
        },
        $set: {
          'players.$.lastActive': new Date()
        }
      }
    );
    
    if (result.modifiedCount > 0) {
      // 更新团队统计信息
      await Team.updateOne(
        { _id: resourceId },
        { 
          $inc: { 'stats.totalTreasuresFound': 1 },
          $set: { 'stats.lastTreasureFoundAt': new Date() }
        }
      );
      
      return true;
    }
    
    return false;
  } catch (error) {
    logger.error(`同步宝藏发现失败: ${userId}`, error);
    return false;
  }
};

/**
 * 同步团队进度
 * @param {String} userId - 用户ID
 * @param {Object} change - 更改数据
 * @returns {Promise<Boolean>} 是否成功
 */
const syncTeamProgress = async (userId, change) => {
  try {
    const { resourceId, data } = change;
    
    if (!data || !data.progress) {
      return false;
    }
    
    // 检查用户是否是团队成员
    const team = await Team.findOne({
      _id: resourceId,
      'players.userId': userId
    });
    
    if (!team) {
      return false;
    }
    
    // 验证用户是否有权更新进度（例如是否是团队队长）
    const player = team.players.find(p => p.userId === userId);
    if (!player || player.role !== 'leader') {
      // 仅允许队长更新进度（或者任何玩家，取决于游戏规则）
      // 这里简化处理，实际项目中可能需要更复杂的权限控制
      logger.warn(`用户${userId}无权更新团队${resourceId}的进度`);
      return false;
    }
    
    // 更新团队进度
    const updateData = {};
    
    if (data.progress.completedPercentage !== undefined) {
      updateData['progress.completedPercentage'] = data.progress.completedPercentage;
    }
    
    if (data.progress.status && ['in_progress', 'completed', 'abandoned'].includes(data.progress.status)) {
      updateData.status = data.progress.status;
      
      // 如果状态变为已完成，记录完成时间
      if (data.progress.status === 'completed') {
        updateData['progress.completedAt'] = new Date();
      }
    }
    
    if (Object.keys(updateData).length === 0) {
      return false;
    }
    
    // 始终更新最后活动时间
    updateData['progress.lastActiveAt'] = new Date();
    
    const result = await Team.updateOne(
      { _id: resourceId },
      { $set: updateData }
    );
    
    return result.modifiedCount > 0;
  } catch (error) {
    logger.error(`同步团队进度失败: ${userId}`, error);
    return false;
  }
};

/**
 * 获取同步状态
 * @param {String} userId - 用户ID
 * @returns {Promise<Object>} 同步状态
 */
const getSyncStatus = async (userId) => {
  try {
    const redisClient = getRedisClient();
    const key = `offline:changes:${userId}`;
    
    const data = await redisClient.get(key);
    if (!data) {
      return {
        totalChanges: 0,
        pendingChanges: 0,
        completedChanges: 0,
        failedChanges: 0,
        lastSyncAttempt: null
      };
    }
    
    const changes = JSON.parse(data);
    
    // 计算各种状态的更改数量
    const pendingChanges = changes.filter(c => c.status === SYNC_STATUS.PENDING).length;
    const syncingChanges = changes.filter(c => c.status === SYNC_STATUS.SYNCING).length;
    const completedChanges = changes.filter(c => c.status === SYNC_STATUS.COMPLETED).length;
    const failedChanges = changes.filter(c => c.status === SYNC_STATUS.FAILED).length;
    
    // 找出最近一次同步时间
    let lastSyncAttempt = null;
    
    for (const change of changes) {
      if (change.syncedAt && (!lastSyncAttempt || change.syncedAt > lastSyncAttempt)) {
        lastSyncAttempt = change.syncedAt;
      }
    }
    
    return {
      totalChanges: changes.length,
      pendingChanges: pendingChanges + syncingChanges,
      completedChanges,
      failedChanges,
      lastSyncAttempt
    };
  } catch (error) {
    logger.error(`获取同步状态失败: ${userId}`, error);
    throw createError('获取同步状态失败', 500);
  }
};

module.exports = {
  // 离线包管理
  generateOfflinePackage,
  checkOfflinePackageUpdates,
  
  // 离线更改同步
  saveOfflineChanges,
  syncOfflineChanges,
  getSyncStatus,
  
  // 导出常量
  SYNC_STATUS,
  SYNC_OPERATION
}; 