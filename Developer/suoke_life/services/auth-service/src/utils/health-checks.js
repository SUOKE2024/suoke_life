/**
 * 健康检查工具模块
 */
const { db } = require('../config/database');
const redis = require('../config/redis');
const { logger } = require('@suoke/shared').utils;

// 服务启动时间
const startTime = Date.now();

/**
 * 检查数据库连接
 * @returns {Promise<{status: string, details: Object}>}
 */
const checkDatabase = async () => {
  try {
    // 执行简单查询检查数据库连接
    await db.raw('SELECT 1');
    return {
      status: 'UP',
      details: { message: '数据库连接正常' }
    };
  } catch (error) {
    logger.error(`数据库健康检查失败: ${error.message}`);
    return {
      status: 'DOWN',
      details: { 
        error: error.message,
        code: error.code
      }
    };
  }
};

/**
 * 检查Redis连接
 * @returns {Promise<{status: string, details: Object}>}
 */
const checkRedis = async () => {
  try {
    // 执行简单命令检查Redis连接
    await redis.ping();
    return {
      status: 'UP',
      details: { message: 'Redis连接正常' }
    };
  } catch (error) {
    logger.error(`Redis健康检查失败: ${error.message}`);
    return {
      status: 'DOWN',
      details: {
        error: error.message,
        code: error.code
      }
    };
  }
};

/**
 * 检查内存使用情况
 * @returns {Object} 内存使用状态
 */
const checkMemory = () => {
  const memoryUsage = process.memoryUsage();
  const totalMemoryMB = Math.round(memoryUsage.rss / 1024 / 1024);
  const heapTotalMB = Math.round(memoryUsage.heapTotal / 1024 / 1024);
  const heapUsedMB = Math.round(memoryUsage.heapUsed / 1024 / 1024);
  
  // 根据内存使用阈值确定状态
  const memoryThresholdMB = parseInt(process.env.MEMORY_THRESHOLD_MB || '1536', 10);
  const status = totalMemoryMB < memoryThresholdMB ? 'UP' : 'WARNING';
  
  return {
    status,
    details: {
      totalMemoryMB,
      heapTotalMB,
      heapUsedMB,
      threshold: memoryThresholdMB
    }
  };
};

/**
 * 检查磁盘空间
 * 注：这是一个简化版本，实际生产中应使用更可靠的方法
 * @returns {Object} 磁盘使用状态
 */
const checkDiskSpace = () => {
  // 在容器环境中，由于安全限制，通常无法直接读取磁盘空间
  // 这里我们假设磁盘空间充足，实际生产环境可能需要更复杂的检查
  return {
    status: 'UP',
    details: {
      message: '磁盘空间检查已跳过（容器环境）'
    }
  };
};

/**
 * 检查服务就绪状态
 * @returns {Promise<Object>} 健康状态对象
 */
const checkReadiness = async () => {
  // 并行执行所有检查
  const [dbStatus, redisStatus, memoryStatus, diskStatus] = await Promise.all([
    checkDatabase(),
    checkRedis(),
    checkMemory(),
    checkDiskSpace()
  ]);
  
  // 任何组件DOWN，整体服务就认为DOWN
  const overallStatus = dbStatus.status === 'UP' && 
                       redisStatus.status === 'UP' && 
                       (memoryStatus.status === 'UP' || memoryStatus.status === 'WARNING') && 
                       diskStatus.status === 'UP' ? 'UP' : 'DOWN';
  
  const uptime = Math.floor((Date.now() - startTime) / 1000);
  
  return {
    status: overallStatus,
    uptime,
    checks: {
      database: dbStatus,
      redis: redisStatus,
      memory: memoryStatus,
      disk: diskStatus
    },
    service: 'auth-service',
    timestamp: new Date().toISOString()
  };
};

/**
 * 检查启动状态
 * @returns {Promise<Object>} 启动状态对象
 */
const checkStartup = async () => {
  // 在启动阶段，我们只关心基本依赖是否可用
  const [dbStatus, redisStatus] = await Promise.all([
    checkDatabase(),
    checkRedis()
  ]);
  
  // 只要基本依赖可用，就认为服务可以启动
  const overallStatus = dbStatus.status === 'UP' && redisStatus.status === 'UP' ? 'UP' : 'DOWN';
  
  return {
    status: overallStatus,
    startupTime: startTime,
    checks: {
      database: dbStatus,
      redis: redisStatus
    },
    service: 'auth-service',
    timestamp: new Date().toISOString()
  };
};

/**
 * 检查活跃状态 (Liveness)
 * @returns {Promise<Object>} 活跃状态对象
 */
const checkLiveness = async () => {
  // 服务存活检查通常比就绪性检查宽松，主要确保服务进程正常
  const memoryStatus = checkMemory();
  
  return {
    status: 'UP',
    uptime: Math.floor((Date.now() - startTime) / 1000),
    checks: {
      memory: memoryStatus
    },
    service: 'auth-service',
    timestamp: new Date().toISOString()
  };
};

module.exports = {
  checkReadiness,
  checkStartup,
  checkLiveness,
  checkDatabase,
  checkRedis,
  checkMemory,
  checkDiskSpace
}; 