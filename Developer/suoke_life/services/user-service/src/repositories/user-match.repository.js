/**
 * 用户匹配存储库
 * 处理用户兴趣图谱匹配相关数据库操作
 */
const db = require('../utils/db');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');
const userMatchModel = require('../models/user-match.model');

/**
 * 创建用户匹配
 * @param {Object} matchData - 匹配数据
 * @returns {Promise<Object>} 创建的匹配对象
 */
async function createMatch(matchData) {
  try {
    const id = uuidv4();
    const now = new Date();
    
    const match = {
      id,
      user_id: matchData.userId,
      matched_user_id: matchData.matchedUserId,
      match_type: matchData.matchType,
      match_score: matchData.matchScore,
      match_reason: matchData.matchReason || '',
      matched_interests: matchData.matchedInterests ? JSON.stringify(matchData.matchedInterests) : null,
      matched_knowledge_domains: matchData.matchedKnowledgeDomains ? JSON.stringify(matchData.matchedKnowledgeDomains) : null,
      match_status: matchData.matchStatus || userMatchModel.MATCH_STATUS.PENDING,
      is_hidden: matchData.isHidden || false,
      created_at: now,
      updated_at: now
    };
    
    const query = `
      INSERT INTO ${userMatchModel.TABLE_NAME} (
        id, user_id, matched_user_id, match_type, match_score, match_reason,
        matched_interests, matched_knowledge_domains, match_status, is_hidden,
        created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE
        match_type = VALUES(match_type),
        match_score = VALUES(match_score),
        match_reason = VALUES(match_reason),
        matched_interests = VALUES(matched_interests),
        matched_knowledge_domains = VALUES(matched_knowledge_domains),
        match_status = VALUES(match_status),
        is_hidden = VALUES(is_hidden),
        updated_at = VALUES(updated_at)
    `;
    
    const values = [
      match.id, match.user_id, match.matched_user_id, match.match_type, 
      match.match_score, match.match_reason, match.matched_interests, 
      match.matched_knowledge_domains, match.match_status, match.is_hidden,
      match.created_at, match.updated_at
    ];
    
    await db.execute(query, values);
    
    return {
      id: match.id,
      userId: match.user_id,
      matchedUserId: match.matched_user_id,
      matchType: match.match_type,
      matchScore: match.match_score,
      matchReason: match.match_reason,
      matchedInterests: match.matched_interests ? JSON.parse(match.matched_interests) : null,
      matchedKnowledgeDomains: match.matched_knowledge_domains ? JSON.parse(match.matched_knowledge_domains) : null,
      matchStatus: match.match_status,
      isHidden: match.is_hidden,
      createdAt: match.created_at,
      updatedAt: match.updated_at
    };
  } catch (error) {
    logger.error('创建用户匹配失败', error);
    throw new Error('创建用户匹配失败');
  }
}

/**
 * 更新用户匹配
 * @param {string} matchId - 匹配ID
 * @param {Object} updateData - 更新数据
 * @returns {Promise<boolean>} 操作结果
 */
async function updateMatch(matchId, updateData) {
  try {
    const updates = [];
    const values = [];
    
    // 构建更新字段
    if (updateData.matchScore !== undefined) {
      updates.push('match_score = ?');
      values.push(updateData.matchScore);
    }
    
    if (updateData.matchReason !== undefined) {
      updates.push('match_reason = ?');
      values.push(updateData.matchReason);
    }
    
    if (updateData.matchedInterests !== undefined) {
      updates.push('matched_interests = ?');
      values.push(JSON.stringify(updateData.matchedInterests));
    }
    
    if (updateData.matchedKnowledgeDomains !== undefined) {
      updates.push('matched_knowledge_domains = ?');
      values.push(JSON.stringify(updateData.matchedKnowledgeDomains));
    }
    
    if (updateData.matchStatus !== undefined) {
      updates.push('match_status = ?');
      values.push(updateData.matchStatus);
    }
    
    if (updateData.isHidden !== undefined) {
      updates.push('is_hidden = ?');
      values.push(updateData.isHidden);
    }
    
    // 如果没有更新字段，直接返回true
    if (updates.length === 0) {
      return true;
    }
    
    // 添加更新时间
    updates.push('updated_at = ?');
    values.push(new Date());
    
    // 添加匹配ID
    values.push(matchId);
    
    const query = `
      UPDATE ${userMatchModel.TABLE_NAME}
      SET ${updates.join(', ')}
      WHERE id = ?
    `;
    
    const result = await db.execute(query, values);
    return result.affectedRows > 0;
  } catch (error) {
    logger.error(`更新用户匹配失败: ${matchId}`, error);
    throw new Error('更新用户匹配失败');
  }
}

/**
 * 获取用户匹配
 * @param {string} matchId - 匹配ID
 * @returns {Promise<Object|null>} 匹配对象或null
 */
async function getMatchById(matchId) {
  try {
    const query = `
      SELECT * FROM ${userMatchModel.TABLE_NAME}
      WHERE id = ?
    `;
    
    const rows = await db.query(query, [matchId]);
    
    if (rows.length === 0) {
      return null;
    }
    
    const match = rows[0];
    
    return {
      id: match.id,
      userId: match.user_id,
      matchedUserId: match.matched_user_id,
      matchType: match.match_type,
      matchScore: match.match_score,
      matchReason: match.match_reason,
      matchedInterests: match.matched_interests ? JSON.parse(match.matched_interests) : null,
      matchedKnowledgeDomains: match.matched_knowledge_domains ? JSON.parse(match.matched_knowledge_domains) : null,
      matchStatus: match.match_status,
      isHidden: match.is_hidden,
      createdAt: match.created_at,
      updatedAt: match.updated_at
    };
  } catch (error) {
    logger.error(`获取用户匹配失败: ${matchId}`, error);
    throw new Error('获取用户匹配失败');
  }
}

/**
 * 获取用户的匹配列表
 * @param {string} userId - 用户ID
 * @param {number} limit - 限制返回数量
 * @param {number} offset - 结果偏移量
 * @param {Object} filters - 过滤条件
 * @returns {Promise<Array>} 匹配列表
 */
async function getUserMatches(userId, limit = 20, offset = 0, filters = {}) {
  try {
    const conditions = ['user_id = ?'];
    const values = [userId];
    
    if (filters.matchType) {
      conditions.push('match_type = ?');
      values.push(filters.matchType);
    }
    
    if (filters.matchStatus) {
      conditions.push('match_status = ?');
      values.push(filters.matchStatus);
    }
    
    if (filters.minScore !== undefined) {
      conditions.push('match_score >= ?');
      values.push(filters.minScore);
    }
    
    if (filters.maxScore !== undefined) {
      conditions.push('match_score <= ?');
      values.push(filters.maxScore);
    }
    
    if (filters.isHidden !== undefined) {
      conditions.push('is_hidden = ?');
      values.push(filters.isHidden);
    }
    
    const query = `
      SELECT * FROM ${userMatchModel.TABLE_NAME}
      WHERE ${conditions.join(' AND ')}
      ORDER BY match_score DESC, created_at DESC
      LIMIT ? OFFSET ?
    `;
    
    values.push(limit, offset);
    
    const rows = await db.query(query, values);
    
    return rows.map(match => ({
      id: match.id,
      userId: match.user_id,
      matchedUserId: match.matched_user_id,
      matchType: match.match_type,
      matchScore: match.match_score,
      matchReason: match.match_reason,
      matchedInterests: match.matched_interests ? JSON.parse(match.matched_interests) : null,
      matchedKnowledgeDomains: match.matched_knowledge_domains ? JSON.parse(match.matched_knowledge_domains) : null,
      matchStatus: match.match_status,
      isHidden: match.is_hidden,
      createdAt: match.created_at,
      updatedAt: match.updated_at
    }));
  } catch (error) {
    logger.error(`获取用户匹配列表失败: ${userId}`, error);
    throw new Error('获取用户匹配列表失败');
  }
}

/**
 * 删除用户匹配
 * @param {string} matchId - 匹配ID
 * @param {string} userId - 用户ID（验证操作权限）
 * @returns {Promise<boolean>} 操作结果
 */
async function deleteMatch(matchId, userId) {
  try {
    const query = `
      DELETE FROM ${userMatchModel.TABLE_NAME}
      WHERE id = ? AND user_id = ?
    `;
    
    const result = await db.execute(query, [matchId, userId]);
    return result.affectedRows > 0;
  } catch (error) {
    logger.error(`删除用户匹配失败: ${matchId}`, error);
    throw new Error('删除用户匹配失败');
  }
}

/**
 * 存储用户兴趣向量
 * @param {string} userId - 用户ID
 * @param {string} vectorType - 向量类型
 * @param {Array} vectorData - 向量数据
 * @param {Object} metadata - 向量元数据
 * @returns {Promise<Object>} 创建的向量记录
 */
async function storeUserInterestVector(userId, vectorType, vectorData, metadata = {}) {
  try {
    const id = uuidv4();
    const now = new Date();
    
    const query = `
      INSERT INTO user_interest_vectors (
        id, user_id, vector_type, vector_data, vector_metadata,
        created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE
        vector_data = VALUES(vector_data),
        vector_metadata = VALUES(vector_metadata),
        updated_at = VALUES(updated_at)
    `;
    
    const values = [
      id, userId, vectorType, 
      JSON.stringify(vectorData),
      metadata ? JSON.stringify(metadata) : null,
      now, now
    ];
    
    await db.execute(query, values);
    
    return {
      id,
      userId,
      vectorType,
      vectorData,
      metadata,
      createdAt: now,
      updatedAt: now
    };
  } catch (error) {
    logger.error(`存储用户兴趣向量失败: ${userId}`, error);
    throw new Error('存储用户兴趣向量失败');
  }
}

/**
 * 获取用户兴趣向量
 * @param {string} userId - 用户ID
 * @param {string} vectorType - 向量类型
 * @returns {Promise<Object|null>} 向量记录或null
 */
async function getUserInterestVector(userId, vectorType) {
  try {
    const query = `
      SELECT * FROM user_interest_vectors
      WHERE user_id = ? AND vector_type = ?
    `;
    
    const rows = await db.query(query, [userId, vectorType]);
    
    if (rows.length === 0) {
      return null;
    }
    
    const vector = rows[0];
    
    return {
      id: vector.id,
      userId: vector.user_id,
      vectorType: vector.vector_type,
      vectorData: JSON.parse(vector.vector_data),
      metadata: vector.vector_metadata ? JSON.parse(vector.vector_metadata) : null,
      createdAt: vector.created_at,
      updatedAt: vector.updated_at
    };
  } catch (error) {
    logger.error(`获取用户兴趣向量失败: ${userId}`, error);
    throw new Error('获取用户兴趣向量失败');
  }
}

/**
 * 创建用户连接请求
 * @param {Object} connectionData - 连接数据
 * @returns {Promise<Object>} 创建的连接对象
 */
async function createConnection(connectionData) {
  try {
    const id = uuidv4();
    const now = new Date();
    
    const connection = {
      id,
      user_id: connectionData.userId,
      connected_user_id: connectionData.connectedUserId,
      connection_status: connectionData.connectionStatus || 'pending',
      connection_type: connectionData.connectionType,
      initiated_from_match_id: connectionData.initiatedFromMatchId || null,
      message: connectionData.message || null,
      created_at: now,
      updated_at: now
    };
    
    const query = `
      INSERT INTO user_connections (
        id, user_id, connected_user_id, connection_status,
        connection_type, initiated_from_match_id, message,
        created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE
        connection_status = VALUES(connection_status),
        connection_type = VALUES(connection_type),
        message = VALUES(message),
        updated_at = VALUES(updated_at)
    `;
    
    const values = [
      connection.id, connection.user_id, connection.connected_user_id,
      connection.connection_status, connection.connection_type,
      connection.initiated_from_match_id, connection.message,
      connection.created_at, connection.updated_at
    ];
    
    await db.execute(query, values);
    
    return {
      id: connection.id,
      userId: connection.user_id,
      connectedUserId: connection.connected_user_id,
      connectionStatus: connection.connection_status,
      connectionType: connection.connection_type,
      initiatedFromMatchId: connection.initiated_from_match_id,
      message: connection.message,
      createdAt: connection.created_at,
      updatedAt: connection.updated_at
    };
  } catch (error) {
    logger.error('创建用户连接失败', error);
    throw new Error('创建用户连接失败');
  }
}

/**
 * 更新用户连接状态
 * @param {string} connectionId - 连接ID
 * @param {string} status - 新状态
 * @param {string} userId - 用户ID（验证操作权限）
 * @returns {Promise<boolean>} 操作结果
 */
async function updateConnectionStatus(connectionId, status, userId) {
  try {
    const query = `
      UPDATE user_connections
      SET connection_status = ?, updated_at = ?
      WHERE id = ? AND (user_id = ? OR connected_user_id = ?)
    `;
    
    const values = [status, new Date(), connectionId, userId, userId];
    
    const result = await db.execute(query, values);
    return result.affectedRows > 0;
  } catch (error) {
    logger.error(`更新用户连接状态失败: ${connectionId}`, error);
    throw new Error('更新用户连接状态失败');
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
    const conditions = ['(user_id = ? OR connected_user_id = ?)'];
    const values = [userId, userId];
    
    if (filters.connectionStatus) {
      conditions.push('connection_status = ?');
      values.push(filters.connectionStatus);
    }
    
    if (filters.connectionType) {
      conditions.push('connection_type = ?');
      values.push(filters.connectionType);
    }
    
    if (filters.direction === 'sent') {
      conditions[0] = 'user_id = ?';
      values.splice(1, 1);
    } else if (filters.direction === 'received') {
      conditions[0] = 'connected_user_id = ?';
      values.splice(1, 1);
    }
    
    const query = `
      SELECT * FROM user_connections
      WHERE ${conditions.join(' AND ')}
      ORDER BY updated_at DESC
      LIMIT ? OFFSET ?
    `;
    
    values.push(limit, offset);
    
    const rows = await db.query(query, values);
    
    return rows.map(connection => ({
      id: connection.id,
      userId: connection.user_id,
      connectedUserId: connection.connected_user_id,
      connectionStatus: connection.connection_status,
      connectionType: connection.connection_type,
      initiatedFromMatchId: connection.initiated_from_match_id,
      message: connection.message,
      createdAt: connection.created_at,
      updatedAt: connection.updated_at
    }));
  } catch (error) {
    logger.error(`获取用户连接列表失败: ${userId}`, error);
    throw new Error('获取用户连接列表失败');
  }
}

module.exports = {
  createMatch,
  updateMatch,
  getMatchById,
  getUserMatches,
  deleteMatch,
  storeUserInterestVector,
  getUserInterestVector,
  createConnection,
  updateConnectionStatus,
  getUserConnections
};