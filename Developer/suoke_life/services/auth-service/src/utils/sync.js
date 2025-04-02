/**
 * 数据跨区域同步工具
 * 实现数据的多区域备份和一致性维护
 */
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');
const { logger } = require('@suoke/shared').utils;
const redis = require('../config/redis');
const { db } = require('../config/database');
const config = require('../config');

// 获取当前区域和同步配置
const currentRegion = process.env.POD_REGION || 'unknown';
const primaryRegion = process.env.PRIMARY_REGION || config.multiCluster?.primaryRegion || 'unknown';
const backupRegionsStr = process.env.BACKUP_REGIONS || '';
const backupRegions = backupRegionsStr.split(',').filter(r => r.trim() !== '');
const syncInterval = parseInt(process.env.CROSS_REGION_SYNC_INTERVAL || '60', 10);
const syncPriority = process.env.CROSS_REGION_SYNC_PRIORITY || 'normal';
const maxSyncRetries = parseInt(process.env.SYNC_MAX_RETRIES || '3', 10);

// 同步锁定键
const SYNC_LOCK_KEY = 'cross_region_sync:lock';
// 同步状态键
const SYNC_STATUS_KEY = 'cross_region_sync:status';
// 同步操作日志键前缀
const SYNC_LOG_PREFIX = 'cross_region_sync:log:';
// 同步数据版本键前缀
const SYNC_VERSION_PREFIX = 'cross_region_sync:version:';

// 正在同步的操作IDs
const pendingSyncOperations = new Set();

/**
 * 初始化同步服务
 * @returns {Promise<void>}
 */
const initialize = async () => {
  // 如果没有配置备份区域，则不启用同步
  if (backupRegions.length === 0) {
    logger.info('未配置备份区域，跨区域同步服务未启用');
    return;
  }
  
  logger.info(`初始化跨区域同步服务，当前区域: ${currentRegion}, 主区域: ${primaryRegion}, 备份区域: ${backupRegions.join(', ')}`);
  
  // 如果当前是主区域，启动同步间隔任务
  if (currentRegion === primaryRegion) {
    // 在启动时执行一次同步
    setTimeout(() => {
      syncAllRegions().catch(err => {
        logger.error(`初始启动同步失败: ${err.message}`);
      });
    }, 10000); // 延迟10秒启动，等待服务完全初始化
    
    // 设置周期性同步任务
    setInterval(() => {
      syncAllRegions().catch(err => {
        logger.error(`定期同步失败: ${err.message}`);
      });
    }, syncInterval * 1000);
    
    logger.info(`跨区域同步服务已启动，同步间隔: ${syncInterval}秒`);
  } else {
    logger.info('当前不是主区域，跨区域同步服务将仅作为接收端');
  }
};

/**
 * 记录同步操作
 * @param {string} table 表名
 * @param {string} operation 操作类型 (insert/update/delete)
 * @param {Object} data 数据
 * @param {string} id 记录ID
 * @returns {Promise<string>} 操作ID
 */
const recordSyncOperation = async (table, operation, data, id) => {
  // 如果未启用同步，则不记录操作
  if (backupRegions.length === 0) {
    return null;
  }
  
  try {
    const operationId = uuidv4();
    const timestamp = Date.now();
    const syncData = {
      id: operationId,
      table,
      operation,
      record_id: id,
      data: JSON.stringify(data),
      source_region: currentRegion,
      created_at: new Date(),
      status: 'pending',
      sync_priority: syncPriority,
      retry_count: 0
    };
    
    // 记录同步操作到Redis
    const logKey = `${SYNC_LOG_PREFIX}${operationId}`;
    await redis.hmset(logKey, {
      ...syncData,
      data: JSON.stringify(data)
    });
    
    // 设置TTL (24小时)
    await redis.expire(logKey, 86400);
    
    // 添加到同步列表
    await redis.zadd('cross_region_sync:queue', timestamp, operationId);
    
    logger.debug(`记录同步操作: ${operationId}, 表: ${table}, 操作: ${operation}, 记录ID: ${id}`);
    
    // 如果是高优先级同步，立即触发
    if (syncPriority === 'high') {
      // 异步触发同步，不等待结果
      setTimeout(() => {
        syncOperation(operationId).catch(err => {
          logger.error(`高优先级同步操作失败: ${err.message}`);
        });
      }, 0);
    }
    
    return operationId;
  } catch (error) {
    logger.error(`记录同步操作失败: ${error.message}`);
    return null;
  }
};

/**
 * 同步特定操作到所有备份区域
 * @param {string} operationId 操作ID
 * @returns {Promise<boolean>} 是否全部成功
 */
const syncOperation = async (operationId) => {
  // 防止重复同步
  if (pendingSyncOperations.has(operationId)) {
    logger.debug(`同步操作 ${operationId} 已在处理中，跳过`);
    return true;
  }
  
  pendingSyncOperations.add(operationId);
  
  try {
    // 获取同步操作详情
    const logKey = `${SYNC_LOG_PREFIX}${operationId}`;
    const syncData = await redis.hgetall(logKey);
    
    if (!syncData || !syncData.id) {
      logger.warn(`未找到同步操作: ${operationId}`);
      pendingSyncOperations.delete(operationId);
      return false;
    }
    
    // 解析数据
    const operation = {
      ...syncData,
      data: JSON.parse(syncData.data || '{}'),
      retry_count: parseInt(syncData.retry_count || '0', 10)
    };
    
    // 检查重试次数
    if (operation.retry_count >= maxSyncRetries) {
      logger.error(`同步操作 ${operationId} 超过最大重试次数 (${maxSyncRetries})`);
      await redis.hset(logKey, 'status', 'failed');
      pendingSyncOperations.delete(operationId);
      return false;
    }
    
    // 更新状态为处理中
    await redis.hset(logKey, 'status', 'processing');
    
    // 同步到所有备份区域
    const results = await Promise.allSettled(
      backupRegions.map(region => syncToRegion(region, operation))
    );
    
    // 检查结果
    const allSuccess = results.every(r => r.status === 'fulfilled' && r.value === true);
    
    if (allSuccess) {
      // 全部成功，更新状态
      await redis.hset(logKey, 'status', 'completed');
      await redis.zrem('cross_region_sync:queue', operationId);
      logger.debug(`同步操作 ${operationId} 成功完成`);
    } else {
      // 部分失败，增加重试计数
      const newRetryCount = operation.retry_count + 1;
      await redis.hmset(logKey, {
        status: 'retry',
        retry_count: newRetryCount.toString()
      });
      
      // 记录失败详情
      const failedRegions = results
        .map((r, i) => r.status === 'rejected' || !r.value ? backupRegions[i] : null)
        .filter(r => r !== null);
      
      logger.warn(`同步操作 ${operationId} 在以下区域失败: ${failedRegions.join(', ')}, 重试次数: ${newRetryCount}`);
    }
    
    pendingSyncOperations.delete(operationId);
    return allSuccess;
  } catch (error) {
    logger.error(`同步操作 ${operationId} 失败: ${error.message}`);
    pendingSyncOperations.delete(operationId);
    return false;
  }
};

/**
 * 同步操作到特定区域
 * @param {string} region 目标区域 
 * @param {Object} operation 操作详情
 * @returns {Promise<boolean>} 是否成功
 */
const syncToRegion = async (region, operation) => {
  try {
    // 获取目标区域API URL
    const apiUrl = getRegionApiUrl(region);
    if (!apiUrl) {
      logger.error(`未定义区域 ${region} 的API URL`);
      return false;
    }
    
    // 准备同步数据
    const syncPayload = {
      operation_id: operation.id,
      table: operation.table,
      operation_type: operation.operation,
      record_id: operation.record_id,
      data: operation.data,
      source_region: currentRegion,
      timestamp: Date.now()
    };
    
    // 获取同步令牌
    const syncToken = generateSyncToken(region);
    
    // 发送同步请求
    const response = await axios.post(`${apiUrl}/api/v1/internal/sync`, syncPayload, {
      headers: {
        'Content-Type': 'application/json',
        'X-Sync-Token': syncToken,
        'X-Source-Region': currentRegion
      },
      timeout: 15000 // 15秒超时
    });
    
    if (response.status === 200 && response.data.success) {
      logger.debug(`成功同步操作 ${operation.id} 到区域 ${region}`);
      return true;
    } else {
      logger.error(`同步到区域 ${region} 失败: ${response.data.message || '未知错误'}`);
      return false;
    }
  } catch (error) {
    logger.error(`同步到区域 ${region} 时出错: ${error.message}`);
    return false;
  }
};

/**
 * 同步所有待处理操作到所有区域
 * @returns {Promise<Object>} 同步结果
 */
const syncAllRegions = async () => {
  // 如果当前不是主区域，跳过
  if (currentRegion !== primaryRegion) {
    logger.debug('当前不是主区域，跳过主动同步');
    return { success: true, skipped: true };
  }
  
  // 尝试获取同步锁
  const lockId = uuidv4();
  const acquired = await redis.set(SYNC_LOCK_KEY, lockId, 'NX', 'EX', 300); // 5分钟锁
  
  if (!acquired) {
    logger.debug('其他进程正在执行同步，跳过');
    return { success: true, skipped: true };
  }
  
  try {
    logger.info('开始全面跨区域同步');
    
    // 更新同步状态
    await redis.hmset(SYNC_STATUS_KEY, {
      last_sync_attempt: Date.now(),
      status: 'running'
    });
    
    // 获取待处理的同步操作
    const pendingOperations = await redis.zrange('cross_region_sync:queue', 0, -1);
    
    logger.info(`找到 ${pendingOperations.length} 个待处理的同步操作`);
    
    if (pendingOperations.length === 0) {
      await redis.hmset(SYNC_STATUS_KEY, {
        last_sync_completion: Date.now(),
        status: 'idle',
        last_result: JSON.stringify({ success: true, processed: 0 })
      });
      
      return { success: true, processed: 0 };
    }
    
    // 并行处理，但限制并发数
    const batchSize = 5;
    const results = {
      total: pendingOperations.length,
      success: 0,
      failed: 0
    };
    
    for (let i = 0; i < pendingOperations.length; i += batchSize) {
      const batch = pendingOperations.slice(i, i + batchSize);
      
      // 并行处理一批操作
      const batchResults = await Promise.allSettled(
        batch.map(operationId => syncOperation(operationId))
      );
      
      // 统计结果
      batchResults.forEach(result => {
        if (result.status === 'fulfilled' && result.value === true) {
          results.success++;
        } else {
          results.failed++;
        }
      });
    }
    
    // 更新同步状态
    await redis.hmset(SYNC_STATUS_KEY, {
      last_sync_completion: Date.now(),
      status: 'idle',
      last_result: JSON.stringify(results)
    });
    
    logger.info(`跨区域同步完成: 总计 ${results.total}, 成功 ${results.success}, 失败 ${results.failed}`);
    
    return {
      success: results.failed === 0,
      ...results
    };
  } catch (error) {
    logger.error(`跨区域同步失败: ${error.message}`);
    
    // 更新同步状态
    await redis.hmset(SYNC_STATUS_KEY, {
      last_sync_completion: Date.now(),
      status: 'error',
      last_error: error.message
    });
    
    return {
      success: false,
      error: error.message
    };
  } finally {
    // 释放锁 (仅当我们持有它时)
    const currentLock = await redis.get(SYNC_LOCK_KEY);
    if (currentLock === lockId) {
      await redis.del(SYNC_LOCK_KEY);
    }
  }
};

/**
 * 获取区域API URL
 * @param {string} region 区域代码
 * @returns {string} API URL
 */
const getRegionApiUrl = (region) => {
  // 从环境变量获取区域服务URL
  const regionUrlVar = `${region.toUpperCase().replace(/-/g, '_')}_API_URL`;
  return process.env[regionUrlVar] || null;
};

/**
 * 生成用于跨区域同步的令牌
 * @param {string} targetRegion 目标区域 
 * @returns {string} 同步令牌
 */
const generateSyncToken = (targetRegion) => {
  // 在生产环境，应该使用更安全的方法生成和验证令牌
  const syncSecret = process.env.SYNC_SECRET || 'default-sync-secret';
  const timestamp = Math.floor(Date.now() / 1000);
  
  return Buffer.from(`${currentRegion}:${targetRegion}:${timestamp}:${syncSecret}`).toString('base64');
};

/**
 * 处理来自其他区域的同步请求
 * @param {Object} syncData 同步数据 
 * @returns {Promise<Object>} 处理结果
 */
const handleIncomingSyncRequest = async (syncData) => {
  try {
    // 验证同步数据
    if (!syncData || !syncData.operation_id || !syncData.table || !syncData.operation_type) {
      return { success: false, message: '同步数据无效或不完整' };
    }
    
    // 检查操作是否已经处理过
    const operationKey = `sync:processed:${syncData.operation_id}`;
    const alreadyProcessed = await redis.exists(operationKey);
    
    if (alreadyProcessed) {
      return { success: true, message: '操作已处理过，已跳过', skipped: true };
    }
    
    // 检查数据版本（避免应用过期的更改）
    if (syncData.data.data_version) {
      const versionKey = `${SYNC_VERSION_PREFIX}${syncData.table}:${syncData.record_id}`;
      const currentVersion = await redis.get(versionKey);
      
      if (currentVersion && parseInt(currentVersion, 10) > syncData.data.data_version) {
        logger.warn(`跳过过期的同步操作: ${syncData.operation_id}, 当前版本 ${currentVersion} > 接收版本 ${syncData.data.data_version}`);
        return { success: true, message: '跳过应用过期数据', skipped: true };
      }
    }
    
    // 根据操作类型执行数据库操作
    switch (syncData.operation_type) {
      case 'insert':
        await db(syncData.table).insert(syncData.data);
        break;
        
      case 'update':
        await db(syncData.table).where('id', syncData.record_id).update(syncData.data);
        break;
        
      case 'delete':
        await db(syncData.table).where('id', syncData.record_id).del();
        break;
        
      default:
        return { success: false, message: `不支持的操作类型: ${syncData.operation_type}` };
    }
    
    // 记录操作已处理（24小时过期）
    await redis.set(operationKey, Date.now(), 'EX', 86400);
    
    // 更新数据版本
    if (syncData.data.data_version) {
      const versionKey = `${SYNC_VERSION_PREFIX}${syncData.table}:${syncData.record_id}`;
      await redis.set(versionKey, syncData.data.data_version);
    }
    
    logger.info(`成功处理来自 ${syncData.source_region} 的同步操作: ${syncData.operation_id}, 表: ${syncData.table}, 操作: ${syncData.operation_type}`);
    
    return { success: true };
  } catch (error) {
    logger.error(`处理同步请求失败: ${error.message}`);
    return { success: false, message: error.message };
  }
};

/**
 * 获取同步状态
 * @returns {Promise<Object>} 同步状态
 */
const getSyncStatus = async () => {
  try {
    const status = await redis.hgetall(SYNC_STATUS_KEY);
    
    if (!status || Object.keys(status).length === 0) {
      return {
        status: 'idle',
        lastSyncAttempt: null,
        lastSyncCompletion: null,
        pendingOperations: 0
      };
    }
    
    // 获取待处理操作数量
    const pendingCount = await redis.zcard('cross_region_sync:queue');
    
    let lastResult = {};
    try {
      lastResult = JSON.parse(status.last_result || '{}');
    } catch (e) {
      lastResult = {};
    }
    
    return {
      status: status.status || 'idle',
      lastSyncAttempt: status.last_sync_attempt ? parseInt(status.last_sync_attempt, 10) : null,
      lastSyncCompletion: status.last_sync_completion ? parseInt(status.last_sync_completion, 10) : null,
      lastError: status.last_error || null,
      lastResult,
      pendingOperations: pendingCount,
      currentRegion,
      primaryRegion,
      backupRegions,
      syncInterval
    };
  } catch (error) {
    logger.error(`获取同步状态失败: ${error.message}`);
    return {
      status: 'error',
      error: error.message
    };
  }
};

module.exports = {
  initialize,
  recordSyncOperation,
  syncOperation,
  syncAllRegions,
  handleIncomingSyncRequest,
  getSyncStatus
}; 