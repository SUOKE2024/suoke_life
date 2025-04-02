/**
 * 玉米迷宫服务 WebSocket 负载测试函数
 * 模拟虚拟玩家行为，测试服务稳定性和性能
 */

const uuid = require('uuid');
const jwt = require('jsonwebtoken');

// 地图边界 (约定的测试迷宫区域)
const MAP_BOUNDS = {
  minLat: 39.900,
  maxLat: 39.950,
  minLon: 116.300,
  maxLon: 116.350
};

/**
 * 生成随机测试用户
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function generateUser(userContext, events, done) {
  const userId = `test-user-${uuid.v4()}`;
  const deviceId = `test-device-${uuid.v4()}`;
  
  // 生成测试令牌 (使用环境变量中的密钥或默认测试密钥)
  const jwtSecret = process.env.JWT_SECRET || 'test-secret-key';
  const token = jwt.sign(
    { userId, deviceId, role: 'player', isTest: true },
    jwtSecret,
    { expiresIn: '1h' }
  );
  
  // 初始化用户状态
  userContext.vars.userId = userId;
  userContext.vars.deviceId = deviceId;
  userContext.vars.token = token;
  userContext.vars.position = generateRandomPosition();
  userContext.vars.heading = Math.random() * 360;
  userContext.vars.teamId = null;
  userContext.vars.messageCount = 0;
  
  return done();
}

/**
 * 生成随机位置
 * @returns {Object} 随机位置对象
 */
function generateRandomPosition() {
  return {
    latitude: MAP_BOUNDS.minLat + (Math.random() * (MAP_BOUNDS.maxLat - MAP_BOUNDS.minLat)),
    longitude: MAP_BOUNDS.minLon + (Math.random() * (MAP_BOUNDS.maxLon - MAP_BOUNDS.minLon))
  };
}

/**
 * 模拟加入游戏
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function joinGame(userContext, events, done) {
  const messageId = `msg-${++userContext.vars.messageCount}-${userContext.vars.userId}`;
  
  const message = {
    type: 'user:join',
    id: messageId,
    timestamp: Date.now(),
    data: {
      displayName: `TestPlayer-${userContext.vars.userId.substr(-6)}`,
      avatar: `https://example.com/test-avatar-${Math.floor(Math.random() * 20)}.jpg`
    }
  };
  
  userContext.ws.send(JSON.stringify(message));
  return done();
}

/**
 * 模拟位置更新
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function updateLocation(userContext, events, done) {
  const messageId = `msg-${++userContext.vars.messageCount}-${userContext.vars.userId}`;
  
  // 更新当前位置（随机移动）
  const position = userContext.vars.position;
  const heading = userContext.vars.heading;
  
  // 计算新位置（模拟行走）
  const distance = Math.random() * 0.0002; // 约20米
  const newHeading = heading + (Math.random() * 40 - 20); // 随机调整方向
  
  // 计算新坐标
  const newLat = position.latitude + distance * Math.cos(newHeading * Math.PI / 180);
  const newLon = position.longitude + distance * Math.sin(newHeading * Math.PI / 180);
  
  // 确保在边界内
  const boundedLat = Math.max(MAP_BOUNDS.minLat, Math.min(MAP_BOUNDS.maxLat, newLat));
  const boundedLon = Math.max(MAP_BOUNDS.minLon, Math.min(MAP_BOUNDS.maxLon, newLon));
  
  // 更新位置和方向
  userContext.vars.position = {
    latitude: boundedLat,
    longitude: boundedLon
  };
  userContext.vars.heading = newHeading % 360;
  
  // 发送位置更新
  const message = {
    type: 'location:update',
    id: messageId,
    timestamp: Date.now(),
    data: {
      latitude: boundedLat,
      longitude: boundedLon,
      accuracy: 5.0 + Math.random() * 5.0,
      heading: newHeading,
      speed: 0.8 + Math.random() * 1.2,
      altitude: 50 + Math.random() * 10,
      altitudeAccuracy: 5 + Math.random() * 3
    }
  };
  
  userContext.ws.send(JSON.stringify(message));
  return done();
}

/**
 * 模拟随机移动
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function moveRandomly(userContext, events, done) {
  // 随机初始方向
  userContext.vars.heading = Math.random() * 360;
  userContext.vars.moveInterval = 3000 + Math.random() * 2000;
  
  return updateLocation(userContext, events, done);
}

/**
 * 执行随机动作
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function performRandomAction(userContext, events, done) {
  const actions = [
    scanAR,          // 权重 1
    scanAR,          // 权重 1
    interactWithNPC, // 权重 1
    discoverTreasure, // 权重 1
    collectResource, // 权重 1
    sendARMessage    // 权重 1
  ];
  
  // 随机选择一个动作
  const action = actions[Math.floor(Math.random() * actions.length)];
  action(userContext, events, done);
}

/**
 * 模拟AR扫描
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function scanAR(userContext, events, done) {
  const messageId = `msg-${++userContext.vars.messageCount}-${userContext.vars.userId}`;
  
  const message = {
    type: 'ar:scan',
    id: messageId,
    timestamp: Date.now(),
    data: {
      scanType: 'environment',
      location: userContext.vars.position,
      // 使用空图像数据，避免负载测试传输大量数据
      // 实际请求会包含图像数据
      imageData: "test_image_data"
    }
  };
  
  userContext.ws.send(JSON.stringify(message));
  return done();
}

/**
 * 模拟与NPC交互
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function interactWithNPC(userContext, events, done) {
  const messageId = `msg-${++userContext.vars.messageCount}-${userContext.vars.userId}`;
  const npcIds = ['laoke-001', 'laoke-002', 'laoke-003', 'laoke-004'];
  
  const message = {
    type: 'npc:interact',
    id: messageId,
    timestamp: Date.now(),
    data: {
      npcId: npcIds[Math.floor(Math.random() * npcIds.length)],
      action: 'talk',
      message: '你好！',
      location: userContext.vars.position
    }
  };
  
  userContext.ws.send(JSON.stringify(message));
  return done();
}

/**
 * 模拟发现宝藏
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function discoverTreasure(userContext, events, done) {
  const messageId = `msg-${++userContext.vars.messageCount}-${userContext.vars.userId}`;
  
  const message = {
    type: 'treasure:discover',
    id: messageId,
    timestamp: Date.now(),
    data: {
      treasureId: `test-treasure-${Math.floor(Math.random() * 1000)}`,
      location: userContext.vars.position
    }
  };
  
  userContext.ws.send(JSON.stringify(message));
  return done();
}

/**
 * 模拟收集资源
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function collectResource(userContext, events, done) {
  const messageId = `msg-${++userContext.vars.messageCount}-${userContext.vars.userId}`;
  
  const message = {
    type: 'resource:collect',
    id: messageId,
    timestamp: Date.now(),
    data: {
      resourceId: `test-resource-${Math.floor(Math.random() * 1000)}`,
      location: userContext.vars.position
    }
  };
  
  userContext.ws.send(JSON.stringify(message));
  return done();
}

/**
 * 模拟发送AR留言
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function sendARMessage(userContext, events, done) {
  const messageId = `msg-${++userContext.vars.messageCount}-${userContext.vars.userId}`;
  const messages = [
    '这里有个宝藏！',
    '小心这条路有障碍！',
    '往东走有捷径！',
    '这里的玉米长得真高！',
    '注意看周围的标记！'
  ];
  
  const message = {
    type: 'ar:message',
    id: messageId,
    timestamp: Date.now(),
    data: {
      content: messages[Math.floor(Math.random() * messages.length)],
      location: userContext.vars.position,
      visibility: 'public',
      expiresIn: 3600
    }
  };
  
  userContext.ws.send(JSON.stringify(message));
  return done();
}

/**
 * 发送心跳
 * @param {Object} userContext - 用户上下文
 * @param {Object} events - 事件系统
 * @param {Function} done - 完成回调
 */
function sendPing(userContext, events, done) {
  const messageId = `ping-${++userContext.vars.messageCount}-${userContext.vars.userId}`;
  
  const message = {
    type: 'ping',
    id: messageId,
    timestamp: Date.now(),
    data: {}
  };
  
  userContext.ws.send(JSON.stringify(message));
  return done();
}

module.exports = {
  generateUser,
  joinGame,
  updateLocation,
  moveRandomly,
  performRandomAction,
  scanAR,
  interactWithNPC,
  discoverTreasure,
  collectResource,
  sendARMessage,
  sendPing
};