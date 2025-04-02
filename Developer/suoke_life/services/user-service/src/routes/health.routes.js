/**
 * 健康检查路由
 */
const express = require('express');
const router = express.Router();
const { db } = require('../utils/db');
const { redis } = require('../utils/redis');
const { register } = require('../utils/metrics');
const config = require('../config');

// 基础健康检查 - 用于Kubernetes liveness probe
router.get('/', async (req, res) => {
  res.status(200).json({
    status: 'success',
    service: config.serviceName,
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  });
});

// 就绪健康检查 - 用于Kubernetes readiness probe
router.get('/ready', async (req, res) => {
  try {
    // 检查数据库连接
    const dbCheck = await checkDatabaseConnection();
    
    // 检查Redis连接
    const redisCheck = await checkRedisConnection();
    
    // 所有依赖服务都正常
    if (dbCheck.status === 'ok' && redisCheck.status === 'ok') {
      return res.status(200).json({
        status: 'success',
        message: '用户服务准备就绪',
        timestamp: new Date().toISOString(),
        checks: {
          database: dbCheck,
          redis: redisCheck
        }
      });
    }
    
    // 有依赖服务异常
    return res.status(503).json({
      status: 'error',
      message: '用户服务未准备就绪',
      timestamp: new Date().toISOString(),
      checks: {
        database: dbCheck,
        redis: redisCheck
      }
    });
  } catch (error) {
    return res.status(500).json({
      status: 'error',
      message: '健康检查执行失败',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// 启动健康检查 - 用于Kubernetes startup probe
router.get('/startup', async (req, res) => {
  try {
    // 检查数据库是否可以执行查询
    const dbCheck = await checkDatabaseQuery();
    
    // 检查Redis是否可以执行命令
    const redisCheck = await checkRedisCommand();
    
    // 检查初始化状态
    const initStatus = checkInitializationStatus();
    
    // 所有依赖服务都正常且初始化完成
    if (dbCheck.status === 'ok' && redisCheck.status === 'ok' && initStatus.status === 'ok') {
      return res.status(200).json({
        status: 'success',
        message: '用户服务启动完成',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        checks: {
          database: dbCheck,
          redis: redisCheck,
          initialization: initStatus
        }
      });
    }
    
    // 有依赖服务异常或初始化未完成
    return res.status(503).json({
      status: 'error',
      message: '用户服务启动未完成',
      timestamp: new Date().toISOString(),
      checks: {
        database: dbCheck,
        redis: redisCheck,
        initialization: initStatus
      }
    });
  } catch (error) {
    return res.status(500).json({
      status: 'error',
      message: '启动健康检查执行失败',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// 详细健康检查 - 提供更多系统状态信息
router.get('/details', async (req, res) => {
  try {
    const memoryUsage = process.memoryUsage();
    const uptime = process.uptime();
    
    // 检查数据库连接
    const dbCheck = await checkDatabaseConnection();
    
    // 检查Redis连接
    const redisCheck = await checkRedisConnection();
    
    // 检查依赖服务是否可用
    const dependencyChecks = await checkDependencyServices();
    
    res.status(200).json({
      status: 'success',
      service: config.serviceName,
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      uptime: uptime,
      memory: {
        rss: `${Math.round(memoryUsage.rss / 1024 / 1024)} MB`,
        heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)} MB`,
        heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)} MB`,
        external: `${Math.round(memoryUsage.external / 1024 / 1024)} MB`
      },
      checks: {
        database: dbCheck,
        redis: redisCheck,
        dependencies: dependencyChecks
      }
    });
  } catch (error) {
    return res.status(500).json({
      status: 'error',
      message: '详细健康检查执行失败',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Prometheus指标端点
router.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: '指标收集失败',
      error: error.message
    });
  }
});

// 辅助函数：检查数据库连接
async function checkDatabaseConnection() {
  try {
    await db.ping();
    return { status: 'ok', message: '数据库连接正常' };
  } catch (error) {
    return { 
      status: 'error', 
      message: '数据库连接异常', 
      error: error.message 
    };
  }
}

// 辅助函数：检查数据库查询
async function checkDatabaseQuery() {
  try {
    const result = await db.query('SELECT 1 as dbCheck');
    return { 
      status: 'ok', 
      message: '数据库查询正常',
      result: result[0]?.dbCheck === 1
    };
  } catch (error) {
    return { 
      status: 'error', 
      message: '数据库查询异常', 
      error: error.message 
    };
  }
}

// 辅助函数：检查Redis连接
async function checkRedisConnection() {
  try {
    const client = await redis.getClient();
    return { status: 'ok', message: 'Redis连接正常' };
  } catch (error) {
    return { 
      status: 'error', 
      message: 'Redis连接异常', 
      error: error.message 
    };
  }
}

// 辅助函数：检查Redis命令
async function checkRedisCommand() {
  try {
    const client = await redis.getClient();
    const result = await client.ping();
    return { 
      status: 'ok', 
      message: 'Redis命令执行正常',
      result: result === 'PONG'
    };
  } catch (error) {
    return { 
      status: 'error', 
      message: 'Redis命令执行异常', 
      error: error.message 
    };
  }
}

// 辅助函数：检查依赖服务
async function checkDependencyServices() {
  // 这里可以检查各个依赖的微服务是否可用
  // 例如认证服务、存储服务等
  // 根据实际情况实现
  return {
    status: 'ok',
    message: '依赖服务检查完成'
  };
}

/**
 * 检查初始化状态
 * 验证所有必要的服务组件是否已完成初始化
 */
function checkInitializationStatus() {
  try {
    // 检查应用程序的各个组件是否已初始化
    const components = [
      { name: 'config', initialized: !!config },
      { name: 'database', initialized: db.isInitialized() },
      { name: 'redis', initialized: redis.isConnected() },
      { name: 'metrics', initialized: !!register }
    ];
    
    const notInitialized = components.filter(c => !c.initialized);
    
    if (notInitialized.length === 0) {
      return {
        status: 'ok',
        message: '所有组件已初始化'
      };
    } else {
      return {
        status: 'error',
        message: '部分组件未初始化',
        pendingComponents: notInitialized.map(c => c.name)
      };
    }
  } catch (error) {
    return {
      status: 'error',
      message: '初始化状态检查失败',
      error: error.message
    };
  }
}

module.exports = router; 