/**
 * 实时服务
 * 负责WebSocket实时通信和状态同步
 */
const logger = require('../utils/logger');
const Redis = require('redis');
const { promisify } = require('util');
const zlib = require('zlib');
const { EventEmitter } = require('events');

// Redis客户端配置
const redisClient = Redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  retry_strategy: function(options) {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      logger.error('Redis连接被拒绝');
      return new Error('Redis服务器连接被拒绝');
    }
    if (options.total_retry_time > 1000 * 60 * 30) {
      logger.error('Redis重试时间过长，放弃连接');
      return new Error('Redis重试超时');
    }
    return Math.min(options.attempt * 100, 3000);
  }
});

// 将Redis方法转为Promise
const redisGet = promisify(redisClient.get).bind(redisClient);
const redisSet = promisify(redisClient.set).bind(redisClient);
const redisPub = promisify(redisClient.publish).bind(redisClient);

// 创建Redis订阅客户端
const redisSub = redisClient.duplicate();

// 事件总线
const eventBus = new EventEmitter();

// 连接处理
redisClient.on('connect', () => logger.info('Redis主客户端连接成功'));
redisClient.on('error', (err) => logger.error('Redis主客户端错误:', err));
redisSub.on('connect', () => logger.info('Redis订阅客户端连接成功'));
redisSub.on('error', (err) => logger.error('Redis订阅客户端错误:', err));

// 在线用户连接映射
const activeConnections = new Map();
// 房间/频道映射
const rooms = new Map();
// 消息队列与批处理
const messageQueue = new Map();
const BATCH_SIZE = 10;
const BATCH_INTERVAL = 100; // 毫秒

/**
 * 压缩消息数据
 * @param {Object} data - 要压缩的数据
 * @returns {Promise<Buffer>} 压缩后的数据
 */
const compressData = (data) => {
  return new Promise((resolve, reject) => {
    const jsonData = JSON.stringify(data);
    zlib.deflate(jsonData, (err, compressed) => {
      if (err) {
        logger.error('消息压缩失败:', err);
        reject(err);
      } else {
        resolve(compressed);
      }
    });
  });
};

/**
 * 解压消息数据
 * @param {Buffer} compressed - 压缩的数据
 * @returns {Promise<Object>} 解压后的数据
 */
const decompressData = (compressed) => {
  return new Promise((resolve, reject) => {
    zlib.inflate(compressed, (err, decompressed) => {
      if (err) {
        logger.error('消息解压失败:', err);
        reject(err);
      } else {
        try {
          const data = JSON.parse(decompressed.toString());
          resolve(data);
        } catch (parseErr) {
          logger.error('解析解压数据失败:', parseErr);
          reject(parseErr);
        }
      }
    });
  });
};

/**
 * 初始化消息批处理定时器
 */
const initMessageBatchProcessor = () => {
  setInterval(() => {
    processBatchedMessages();
  }, BATCH_INTERVAL);

  logger.info(`消息批处理器已启动，批次大小: ${BATCH_SIZE}, 间隔: ${BATCH_INTERVAL}ms`);
};

/**
 * 处理批处理消息队列
 */
const processBatchedMessages = async () => {
  for (const [userId, messages] of messageQueue.entries()) {
    if (messages.length > 0) {
      try {
        if (activeConnections.has(userId)) {
          const connection = activeConnections.get(userId);
          const batchToSend = messages.splice(0, BATCH_SIZE);
          
          if (batchToSend.length > 0) {
            // 实际项目中，这里会将消息发送到WebSocket连接
            logger.debug(`批量发送${batchToSend.length}条消息到用户${userId}`);
            
            // 如果消息数量为1，直接发送；否则打包发送
            if (batchToSend.length === 1) {
              // 实际发送逻辑 - 单条消息
              await sendToWebSocket(connection, batchToSend[0]);
            } else {
              // 实际发送逻辑 - 批量消息
              await sendToWebSocket(connection, {
                type: 'message_batch',
                messages: batchToSend
              });
            }
          }
        } else {
          // 用户离线，存储到Redis中的离线消息队列
          const offlineQueueKey = `offline:messages:${userId}`;
          const currentQueue = await redisGet(offlineQueueKey) || '[]';
          const queue = JSON.parse(currentQueue);
          queue.push(...messages);
          
          // 限制队列大小防止无限增长
          while (queue.length > 100) {
            queue.shift();
          }
          
          await redisSet(offlineQueueKey, JSON.stringify(queue));
          messageQueue.delete(userId);
          logger.info(`用户${userId}离线，${messages.length}条消息已保存到离线队列`);
        }
      } catch (error) {
        logger.error(`处理用户${userId}批量消息失败:`, error);
      }
    }
  }
};

/**
 * 发送消息到WebSocket连接
 * @param {Object} connection - WebSocket连接
 * @param {Object} message - 消息
 */
const sendToWebSocket = async (connection, message) => {
  try {
    // 在实际项目中实现WebSocket消息发送
    // connection.send(JSON.stringify(message));
    
    // 模拟发送，实际项目应替换为真实实现
    logger.debug(`消息已发送到连接:`, connection.connectionId);
    return true;
  } catch (error) {
    logger.error('WebSocket消息发送失败:', error);
    throw error;
  }
};

/**
 * 发送用户通知
 * @param {String} userId - 用户ID
 * @param {Object} notification - 通知数据
 * @returns {Promise<Boolean>} 是否成功
 */
const sendUserNotification = async (userId, notification) => {
  try {
    logger.info(`向用户${userId}发送实时通知: ${notification.type}`);
    
    // 添加性能指标
    notification.timestamp = Date.now();
    notification.messageId = `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    // 使用消息队列进行批处理
    if (!messageQueue.has(userId)) {
      messageQueue.set(userId, []);
    }
    
    messageQueue.get(userId).push(notification);
    
    // 发布事件
    eventBus.emit('message_queued', {userId, notification});
    
    // 同时通过Redis发布，以便于集群中的其他实例接收
    await redisPub(`user:notification:${userId}`, JSON.stringify(notification));
    
    return true;
  } catch (error) {
    logger.error(`发送用户实时通知失败:`, error);
    return false;
  }
};

/**
 * 通知团队成员
 * @param {String} teamId - 团队ID
 * @param {String} eventType - 事件类型
 * @param {Object} eventData - 事件数据
 * @returns {Promise<Object>} 结果
 */
const notifyTeamMembers = async (teamId, eventType, eventData) => {
  try {
    logger.info(`向团队${teamId}发送事件: ${eventType}`);
    
    // 实际项目中应该获取团队成员并发送消息
    // 这里假设团队ID就是一个房间/频道
    const roomKey = `team:${teamId}`;
    
    // 发布到Redis频道以支持集群
    await redisPub(roomKey, JSON.stringify({
      type: eventType,
      teamId,
      timestamp: Date.now(),
      ...eventData
    }));
    
    if (rooms.has(roomKey)) {
      const userIds = rooms.get(roomKey);
      logger.info(`团队房间${roomKey}有${userIds.length}个在线成员`);
      
      // 向所有在线成员发送消息
      let sentCount = 0;
      const batchPromises = userIds.map(userId => 
        sendUserNotification(userId, {
          type: eventType,
          teamId,
          ...eventData
        }).then(success => {
          if (success) sentCount++;
          return success;
        })
      );
      
      await Promise.all(batchPromises);
      
      return {
        success: true,
        total: userIds.length,
        sent: sentCount
      };
    } else {
      logger.info(`团队房间${roomKey}不存在或没有在线成员`);
      return {
        success: false,
        reason: 'no_active_room'
      };
    }
  } catch (error) {
    logger.error(`通知团队成员失败:`, error);
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * 广播迷宫事件
 * @param {String} mazeId - 迷宫ID
 * @param {String} eventType - 事件类型
 * @param {Object} eventData - 事件数据
 * @returns {Promise<Object>} 结果
 */
const broadcastMazeEvent = async (mazeId, eventType, eventData) => {
  try {
    logger.info(`广播迷宫${mazeId}事件: ${eventType}`);
    
    const roomKey = `maze:${mazeId}`;
    
    // 发布到Redis频道
    await redisPub(roomKey, JSON.stringify({
      type: eventType,
      mazeId,
      timestamp: Date.now(),
      ...eventData
    }));
    
    if (rooms.has(roomKey)) {
      const userIds = rooms.get(roomKey);
      
      // 使用Promise.all并行发送通知
      const results = await Promise.allSettled(
        userIds.map(userId => 
          sendUserNotification(userId, {
            type: eventType,
            mazeId,
            ...eventData
          })
        )
      );
      
      const sentCount = results.filter(r => r.status === 'fulfilled' && r.value === true).length;
      
      return {
        success: true,
        total: userIds.length,
        sent: sentCount
      };
    } else {
      return {
        success: false,
        reason: 'no_active_room'
      };
    }
  } catch (error) {
    logger.error(`广播迷宫事件失败:`, error);
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * 加入房间/频道
 * @param {String} userId - 用户ID
 * @param {String} roomType - 房间类型
 * @param {String} roomId - 房间ID
 * @returns {Promise<Boolean>} 是否成功
 */
const joinRoom = async (userId, roomType, roomId) => {
  try {
    const roomKey = `${roomType}:${roomId}`;
    
    if (!rooms.has(roomKey)) {
      rooms.set(roomKey, []);
    }
    
    const userIds = rooms.get(roomKey);
    if (!userIds.includes(userId)) {
      userIds.push(userId);
      logger.info(`用户${userId}加入房间${roomKey}`);
      
      // 通知房间有新成员加入
      await redisPub(`${roomKey}:system`, JSON.stringify({
        type: 'user_joined',
        userId,
        timestamp: Date.now()
      }));
    }
    
    return true;
  } catch (error) {
    logger.error(`加入房间失败:`, error);
    return false;
  }
};

/**
 * 离开房间/频道
 * @param {String} userId - 用户ID
 * @param {String} roomType - 房间类型
 * @param {String} roomId - 房间ID
 * @returns {Promise<Boolean>} 是否成功
 */
const leaveRoom = async (userId, roomType, roomId) => {
  try {
    const roomKey = `${roomType}:${roomId}`;
    
    if (rooms.has(roomKey)) {
      const userIds = rooms.get(roomKey);
      const index = userIds.indexOf(userId);
      
      if (index !== -1) {
        userIds.splice(index, 1);
        logger.info(`用户${userId}离开房间${roomKey}`);
        
        // 通知房间有成员离开
        await redisPub(`${roomKey}:system`, JSON.stringify({
          type: 'user_left',
          userId,
          timestamp: Date.now()
        }));
        
        // 如果房间为空，删除房间
        if (userIds.length === 0) {
          rooms.delete(roomKey);
          logger.info(`房间${roomKey}已空，被删除`);
        }
      }
    }
    
    return true;
  } catch (error) {
    logger.error(`离开房间失败:`, error);
    return false;
  }
};

/**
 * 用户连接
 * @param {String} userId - 用户ID
 * @param {Object} connectionInfo - 连接信息
 * @returns {Promise<Boolean>} 是否成功
 */
const userConnect = async (userId, connectionInfo) => {
  try {
    const connectionId = `conn_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    
    activeConnections.set(userId, {
      connectionId,
      connectedAt: new Date(),
      lastActivity: new Date(),
      ...connectionInfo
    });
    
    logger.info(`用户${userId}已连接，连接ID: ${connectionId}`);
    
    // 发布用户连接事件
    await redisPub('user:connections', JSON.stringify({
      type: 'user_connected',
      userId,
      connectionId,
      timestamp: Date.now()
    }));
    
    // 检查并发送离线消息
    await checkAndSendOfflineMessages(userId);
    
    return true;
  } catch (error) {
    logger.error(`用户连接处理失败:`, error);
    return false;
  }
};

/**
 * 检查并发送离线消息
 * @param {String} userId - 用户ID
 * @returns {Promise<Boolean>} 是否成功
 */
const checkAndSendOfflineMessages = async (userId) => {
  try {
    const offlineQueueKey = `offline:messages:${userId}`;
    const offlineMessages = await redisGet(offlineQueueKey);
    
    if (offlineMessages) {
      const messages = JSON.parse(offlineMessages);
      logger.info(`为用户${userId}找到${messages.length}条离线消息`);
      
      if (messages.length > 0 && !messageQueue.has(userId)) {
        messageQueue.set(userId, []);
      }
      
      // 将离线消息添加到发送队列
      messageQueue.get(userId).push(...messages);
      
      // 清除Redis中的离线消息
      await redisSet(offlineQueueKey, '[]');
      return true;
    }
    
    return false;
  } catch (error) {
    logger.error(`处理用户${userId}离线消息失败:`, error);
    return false;
  }
};

/**
 * 用户断开连接
 * @param {String} userId - 用户ID
 * @returns {Promise<Boolean>} 是否成功
 */
const userDisconnect = async (userId) => {
  try {
    if (activeConnections.has(userId)) {
      const connection = activeConnections.get(userId);
      activeConnections.delete(userId);
      
      logger.info(`用户${userId}已断开连接，连接ID: ${connection.connectionId}`);
      
      // 发布用户断开连接事件
      await redisPub('user:connections', JSON.stringify({
        type: 'user_disconnected',
        userId,
        connectionId: connection.connectionId,
        timestamp: Date.now()
      }));
      
      // 从所有房间中移除用户
      for (const [roomKey, userIds] of rooms.entries()) {
        const index = userIds.indexOf(userId);
        if (index !== -1) {
          userIds.splice(index, 1);
          logger.info(`用户${userId}从房间${roomKey}中移除`);
          
          // 通知房间有成员离开
          await redisPub(`${roomKey}:system`, JSON.stringify({
            type: 'user_left',
            userId,
            connectionId: connection.connectionId,
            timestamp: Date.now()
          }));
          
          // 如果房间为空，删除房间
          if (userIds.length === 0) {
            rooms.delete(roomKey);
            logger.info(`房间${roomKey}已空，被删除`);
          }
        }
      }
    }
    
    return true;
  } catch (error) {
    logger.error(`用户断开连接处理失败:`, error);
    return false;
  }
};

/**
 * 更新用户活动状态
 * @param {String} userId - 用户ID
 * @returns {Promise<Boolean>} 是否成功
 */
const updateUserActivity = async (userId) => {
  try {
    if (activeConnections.has(userId)) {
      const connection = activeConnections.get(userId);
      connection.lastActivity = new Date();
      return true;
    }
    return false;
  } catch (error) {
    logger.error(`更新用户${userId}活动状态失败:`, error);
    return false;
  }
};

/**
 * 初始化Redis订阅
 */
const initRedisSubscriptions = () => {
  // 订阅用户通知
  redisSub.subscribe('user:connections');
  
  // 处理订阅消息
  redisSub.on('message', (channel, message) => {
    try {
      const data = JSON.parse(message);
      
      // 处理不同类型的频道
      if (channel === 'user:connections') {
        handleUserConnectionEvent(data);
      } else if (channel.startsWith('team:')) {
        handleTeamEvent(channel, data);
      } else if (channel.startsWith('maze:')) {
        handleMazeEvent(channel, data);
      }
    } catch (error) {
      logger.error(`处理Redis订阅消息失败:`, error);
    }
  });
  
  logger.info('Redis订阅初始化完成');
};

/**
 * 处理用户连接事件
 * @param {Object} data - 事件数据
 */
const handleUserConnectionEvent = (data) => {
  // 实现分布式用户连接状态同步
  logger.debug(`收到用户连接事件: ${data.type} 用户: ${data.userId}`);
};

/**
 * 处理团队事件
 * @param {String} channel - 频道
 * @param {Object} data - 事件数据
 */
const handleTeamEvent = (channel, data) => {
  // 实现分布式团队事件处理
  logger.debug(`收到团队事件: ${channel} 类型: ${data.type}`);
};

/**
 * 处理迷宫事件
 * @param {String} channel - 频道
 * @param {Object} data - 事件数据
 */
const handleMazeEvent = (channel, data) => {
  // 实现分布式迷宫事件处理
  logger.debug(`收到迷宫事件: ${channel} 类型: ${data.type}`);
};

// 初始化
const init = () => {
  initMessageBatchProcessor();
  initRedisSubscriptions();
  logger.info('实时服务初始化完成');
};

// 服务启动时初始化
init();

module.exports = {
  sendUserNotification,
  notifyTeamMembers,
  broadcastMazeEvent,
  joinRoom,
  leaveRoom,
  userConnect,
  userDisconnect,
  updateUserActivity,
  compressData,
  decompressData
}; 