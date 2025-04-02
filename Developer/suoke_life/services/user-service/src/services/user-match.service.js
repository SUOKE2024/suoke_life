/**
 * 用户匹配服务
 * 处理用户兴趣图谱匹配相关业务逻辑
 */
const userMatchRepository = require('../repositories/user-match.repository');
const userRepository = require('../repositories/user.repository');
const userPreferenceRepository = require('../repositories/user-preference.repository');
const knowledgePreferenceRepository = require('../repositories/knowledge-preference.repository');
const logger = require('../utils/logger');
const userMatchModel = require('../models/user-match.model');
const { BadRequestError, NotFoundError, UnauthorizedError } = require('../utils/errors');

/**
 * 创建用户匹配
 * @param {string} userId - 发起匹配的用户ID
 * @param {string} matchedUserId - 被匹配的用户ID
 * @param {Object} matchData - 匹配数据
 * @returns {Promise<Object>} 创建的匹配对象
 */
async function createMatch(userId, matchedUserId, matchData) {
  try {
    // 验证两个用户存在
    const user = await userRepository.getUserById(userId);
    if (!user) {
      throw new NotFoundError('用户不存在');
    }
    
    const matchedUser = await userRepository.getUserById(matchedUserId);
    if (!matchedUser) {
      throw new NotFoundError('被匹配用户不存在');
    }
    
    // 验证匹配类型
    if (!Object.values(userMatchModel.MATCH_TYPES).includes(matchData.matchType)) {
      throw new BadRequestError('无效的匹配类型');
    }
    
    // 验证匹配分数
    if (matchData.matchScore < 0 || matchData.matchScore > 100) {
      throw new BadRequestError('匹配分数必须在0-100之间');
    }
    
    // 创建匹配
    const match = await userMatchRepository.createMatch({
      userId,
      matchedUserId,
      matchType: matchData.matchType,
      matchScore: matchData.matchScore,
      matchReason: matchData.matchReason,
      matchedInterests: matchData.matchedInterests,
      matchedKnowledgeDomains: matchData.matchedKnowledgeDomains,
      matchStatus: userMatchModel.MATCH_STATUS.PENDING
    });
    
    return match;
  } catch (error) {
    if (error instanceof BadRequestError || error instanceof NotFoundError) {
      throw error;
    }
    logger.error('创建用户匹配失败', { userId, matchedUserId, error: error.message });
    throw new Error('创建用户匹配失败');
  }
}

/**
 * 更新匹配状态
 * @param {string} matchId - 匹配ID
 * @param {string} userId - 用户ID
 * @param {string} status - 新状态
 * @returns {Promise<Object>} 更新后的匹配对象
 */
async function updateMatchStatus(matchId, userId, status) {
  try {
    // 获取匹配对象
    const match = await userMatchRepository.getMatchById(matchId);
    if (!match) {
      throw new NotFoundError('匹配记录不存在');
    }
    
    // 验证权限（只有匹配的发起者或接收者可以更新状态）
    if (match.userId !== userId && match.matchedUserId !== userId) {
      throw new UnauthorizedError('无权更新此匹配状态');
    }
    
    // 验证状态
    if (!Object.values(userMatchModel.MATCH_STATUS).includes(status)) {
      throw new BadRequestError('无效的匹配状态');
    }
    
    // 更新状态
    const updated = await userMatchRepository.updateMatch(matchId, {
      matchStatus: status
    });
    
    if (!updated) {
      throw new Error('更新匹配状态失败');
    }
    
    // 获取更新后的匹配对象
    return await userMatchRepository.getMatchById(matchId);
  } catch (error) {
    if (error instanceof BadRequestError || error instanceof NotFoundError || error instanceof UnauthorizedError) {
      throw error;
    }
    logger.error(`更新匹配状态失败: ${matchId}`, { userId, status, error: error.message });
    throw new Error('更新匹配状态失败');
  }
}

/**
 * 获取匹配详情
 * @param {string} matchId - 匹配ID
 * @param {string} userId - 请求用户ID（验证访问权限）
 * @returns {Promise<Object>} 匹配对象
 */
async function getMatchById(matchId, userId) {
  try {
    // 获取匹配对象
    const match = await userMatchRepository.getMatchById(matchId);
    if (!match) {
      throw new NotFoundError('匹配记录不存在');
    }
    
    // 验证访问权限（只有匹配的发起者或接收者可以查看）
    if (match.userId !== userId && match.matchedUserId !== userId) {
      throw new UnauthorizedError('无权查看此匹配记录');
    }
    
    return match;
  } catch (error) {
    if (error instanceof NotFoundError || error instanceof UnauthorizedError) {
      throw error;
    }
    logger.error(`获取匹配记录失败: ${matchId}`, { userId, error: error.message });
    throw new Error('获取匹配记录失败');
  }
}

/**
 * 获取用户匹配列表
 * @param {string} userId - 用户ID
 * @param {number} limit - 限制返回数量
 * @param {number} offset - 结果偏移量
 * @param {Object} filters - 过滤条件
 * @returns {Promise<Array>} 匹配列表
 */
async function getUserMatches(userId, limit = 20, offset = 0, filters = {}) {
  try {
    // 验证用户存在
    const user = await userRepository.getUserById(userId);
    if (!user) {
      throw new NotFoundError('用户不存在');
    }
    
    // 获取匹配列表
    const matches = await userMatchRepository.getUserMatches(userId, limit, offset, filters);
    
    // 如果需要，可以在这里添加匹配用户的基本信息
    if (matches.length > 0 && filters.includeUserInfo) {
      const userIds = matches.map(match => match.matchedUserId);
      const users = await userRepository.getUsersByIds(userIds);
      
      // 构建用户ID到用户信息的映射
      const userMap = users.reduce((map, user) => {
        map[user.id] = user;
        return map;
      }, {});
      
      // 为每个匹配添加用户信息
      matches.forEach(match => {
        match.matchedUser = userMap[match.matchedUserId] || null;
      });
    }
    
    return matches;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`获取用户匹配列表失败: ${userId}`, { error: error.message });
    throw new Error('获取用户匹配列表失败');
  }
}

/**
 * 删除匹配记录
 * @param {string} matchId - 匹配ID
 * @param {string} userId - 用户ID
 * @returns {Promise<boolean>} 操作结果
 */
async function deleteMatch(matchId, userId) {
  try {
    // 获取匹配对象
    const match = await userMatchRepository.getMatchById(matchId);
    if (!match) {
      throw new NotFoundError('匹配记录不存在');
    }
    
    // 验证权限（只有匹配的发起者可以删除）
    if (match.userId !== userId) {
      throw new UnauthorizedError('无权删除此匹配记录');
    }
    
    // 删除匹配
    const deleted = await userMatchRepository.deleteMatch(matchId, userId);
    if (!deleted) {
      throw new Error('删除匹配记录失败');
    }
    
    return true;
  } catch (error) {
    if (error instanceof NotFoundError || error instanceof UnauthorizedError) {
      throw error;
    }
    logger.error(`删除匹配记录失败: ${matchId}`, { userId, error: error.message });
    throw new Error('删除匹配记录失败');
  }
}

/**
 * 计算用户兴趣向量
 * @param {string} userId - 用户ID
 * @returns {Promise<Object>} 用户兴趣向量数据
 */
async function calculateUserInterestVector(userId) {
  try {
    // 验证用户存在
    const user = await userRepository.getUserById(userId);
    if (!user) {
      throw new NotFoundError('用户不存在');
    }
    
    // 获取用户偏好
    const preferences = await userPreferenceRepository.getUserPreferences(userId);
    
    // 获取知识偏好
    const knowledgePreferences = await knowledgePreferenceRepository.getUserKnowledgePreferences(userId);
    
    // 构建兴趣向量元数据
    const metadata = {
      userPreferenceCount: preferences.length,
      knowledgePreferenceCount: knowledgePreferences.length,
      lastUpdated: new Date().toISOString()
    };
    
    // 这里应该使用实际的向量计算逻辑
    // 目前使用简化版，实际系统中应该使用更复杂的算法
    const interestVector = [];
    
    // 从用户偏好中提取兴趣点
    preferences.forEach(pref => {
      if (pref.preferenceType === 'interest') {
        interestVector.push({
          type: 'interest',
          id: pref.preferenceKey,
          name: pref.preferenceName,
          value: pref.preferenceValue,
          weight: 0.7
        });
      }
    });
    
    // 从知识偏好中提取兴趣点
    knowledgePreferences.forEach(pref => {
      interestVector.push({
        type: 'knowledge',
        id: pref.domainId,
        name: pref.domainName,
        value: pref.preferenceLevel,
        weight: 0.5
      });
    });
    
    // 存储兴趣向量
    const vectorRecord = await userMatchRepository.storeUserInterestVector(
      userId,
      'interest',
      interestVector,
      metadata
    );
    
    return vectorRecord;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`计算用户兴趣向量失败: ${userId}`, { error: error.message });
    throw new Error('计算用户兴趣向量失败');
  }
}

/**
 * 查找潜在匹配用户
 * @param {string} userId - 用户ID
 * @param {Object} options - 查询选项
 * @returns {Promise<Array>} 潜在匹配用户列表
 */
async function findPotentialMatches(userId, options = {}) {
  try {
    // 验证用户存在
    const user = await userRepository.getUserById(userId);
    if (!user) {
      throw new NotFoundError('用户不存在');
    }
    
    // 获取用户的兴趣向量
    let interestVector = await userMatchRepository.getUserInterestVector(userId, 'interest');
    
    // 如果用户没有兴趣向量，则计算一个
    if (!interestVector) {
      interestVector = await calculateUserInterestVector(userId);
    }
    
    // 在实际系统中，这里应该是一个复杂的匹配算法
    // 例如，调用向量数据库进行相似度搜索
    // 或者使用其他匹配算法来找到相似的用户
    
    // 这是一个简化版的匹配逻辑，在实际系统中应该替换为更复杂的算法
    
    // 获取其他用户的简单列表（实际系统应该有更智能的选择机制）
    const limit = options.limit || 10;
    const otherUsers = await userRepository.getUsers(limit + 1, 0);
    
    // 过滤掉当前用户
    const potentialUsers = otherUsers.filter(u => u.id !== userId);
    
    // 为每个用户创建一个匹配记录
    const matches = [];
    
    for (const potentialUser of potentialUsers.slice(0, limit)) {
      // 计算匹配分数（简化版）
      const matchScore = Math.floor(Math.random() * 100); // 在实际系统中，这应该基于向量相似度
      
      // 创建匹配记录
      const match = await createMatch(userId, potentialUser.id, {
        matchType: userMatchModel.MATCH_TYPES.INTEREST,
        matchScore,
        matchReason: '基于兴趣相似度',
        matchedInterests: []  // 在实际系统中，这应该基于实际的兴趣交集
      });
      
      matches.push(match);
    }
    
    return matches;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`查找潜在匹配用户失败: ${userId}`, { error: error.message });
    throw new Error('查找潜在匹配用户失败');
  }
}

/**
 * 创建用户连接请求
 * @param {string} userId - 发起连接的用户ID
 * @param {string} connectedUserId - 被连接的用户ID
 * @param {Object} connectionData - 连接数据
 * @returns {Promise<Object>} 创建的连接对象
 */
async function createConnection(userId, connectedUserId, connectionData) {
  try {
    // 验证两个用户存在
    const user = await userRepository.getUserById(userId);
    if (!user) {
      throw new NotFoundError('用户不存在');
    }
    
    const connectedUser = await userRepository.getUserById(connectedUserId);
    if (!connectedUser) {
      throw new NotFoundError('被连接用户不存在');
    }
    
    // 验证连接类型
    if (!connectionData.connectionType || !Object.values(userMatchModel.CONNECTION_TYPES).includes(connectionData.connectionType)) {
      throw new BadRequestError('无效的连接类型');
    }
    
    // 创建连接请求
    const connection = await userMatchRepository.createConnection({
      userId,
      connectedUserId,
      connectionType: connectionData.connectionType,
      initiatedFromMatchId: connectionData.matchId,
      message: connectionData.message
    });
    
    // 如果存在匹配ID，则更新匹配状态
    if (connectionData.matchId) {
      await userMatchRepository.updateMatch(connectionData.matchId, {
        matchStatus: userMatchModel.MATCH_STATUS.CONNECTION_REQUESTED
      });
    }
    
    return connection;
  } catch (error) {
    if (error instanceof BadRequestError || error instanceof NotFoundError) {
      throw error;
    }
    logger.error('创建用户连接请求失败', { userId, connectedUserId, error: error.message });
    throw new Error('创建用户连接请求失败');
  }
}

/**
 * 更新连接状态
 * @param {string} connectionId - 连接ID
 * @param {string} userId - 用户ID
 * @param {string} status - 新状态
 * @returns {Promise<Object>} 更新后的连接对象
 */
async function updateConnectionStatus(connectionId, userId, status) {
  try {
    // 获取连接请求
    const connections = await userMatchRepository.getUserConnections(
      userId, 
      1, 
      0, 
      { connectionId }
    );
    
    if (connections.length === 0) {
      throw new NotFoundError('连接请求不存在或您无权访问');
    }
    
    const connection = connections[0];
    
    // 验证权限（只有连接的发起者或接收者可以更新状态）
    if (connection.userId !== userId && connection.connectedUserId !== userId) {
      throw new UnauthorizedError('无权更新此连接状态');
    }
    
    // 验证状态变更逻辑
    if (connection.connectionStatus === 'accepted' && status !== 'rejected') {
      throw new BadRequestError('已接受的连接不能更改状态');
    }
    
    // 更新状态
    const updated = await userMatchRepository.updateConnectionStatus(connectionId, status, userId);
    if (!updated) {
      throw new Error('更新连接状态失败');
    }
    
    // 如果接受了连接请求，并且有来源匹配ID，更新匹配状态
    if (status === 'accepted' && connection.initiatedFromMatchId) {
      await userMatchRepository.updateMatch(connection.initiatedFromMatchId, {
        matchStatus: userMatchModel.MATCH_STATUS.CONNECTED
      });
    }
    
    // 获取更新后的连接请求
    const updatedConnections = await userMatchRepository.getUserConnections(
      userId, 
      1, 
      0, 
      { connectionId }
    );
    
    return updatedConnections[0];
  } catch (error) {
    if (error instanceof BadRequestError || error instanceof NotFoundError || error instanceof UnauthorizedError) {
      throw error;
    }
    logger.error(`更新连接状态失败: ${connectionId}`, { userId, status, error: error.message });
    throw new Error('更新连接状态失败');
  }
}

/**
 * 获取用户连接列表
 * @param {string} userId - 用户ID
 * @param {number} limit - 限制返回数量
 * @param {number} offset - 结果偏移量
 * @param {Object} filters - 过滤条件
 * @returns {Promise<Array>} 连接列表
 */
async function getUserConnections(userId, limit = 20, offset = 0, filters = {}) {
  try {
    // 验证用户存在
    const user = await userRepository.getUserById(userId);
    if (!user) {
      throw new NotFoundError('用户不存在');
    }
    
    // 获取连接列表
    const connections = await userMatchRepository.getUserConnections(userId, limit, offset, filters);
    
    // 如果需要，可以在这里添加连接用户的基本信息
    if (connections.length > 0 && filters.includeUserInfo) {
      const userIds = new Set();
      
      connections.forEach(conn => {
        const otherUserId = conn.userId === userId ? conn.connectedUserId : conn.userId;
        userIds.add(otherUserId);
      });
      
      const users = await userRepository.getUsersByIds(Array.from(userIds));
      
      // 构建用户ID到用户信息的映射
      const userMap = users.reduce((map, user) => {
        map[user.id] = user;
        return map;
      }, {});
      
      // 为每个连接添加用户信息
      connections.forEach(conn => {
        const otherUserId = conn.userId === userId ? conn.connectedUserId : conn.userId;
        conn.otherUser = userMap[otherUserId] || null;
      });
    }
    
    return connections;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }
    logger.error(`获取用户连接列表失败: ${userId}`, { error: error.message });
    throw new Error('获取用户连接列表失败');
  }
}

module.exports = {
  createMatch,
  updateMatchStatus,
  getMatchById,
  getUserMatches,
  deleteMatch,
  calculateUserInterestVector,
  findPotentialMatches,
  createConnection,
  updateConnectionStatus,
  getUserConnections
};