/**
 * 健康检查路由
 */
const express = require('express');
const router = express.Router();
const os = require('os');
const { db } = require('../config/database');
const redis = require('../utils/redis');
const config = require('../config');
const logger = require('../utils/logger');

/**
 * @route GET /health
 * @route GET /api/health
 * @desc 基本健康检查端点
 * @access Public
 */
router.get('/', async (req, res) => {
  try {
    res.status(200).json({
      status: 'ok',
      service: 'auth-service',
      version: process.env.npm_package_version || '1.0.0',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`健康检查错误: ${error.message}`, { error });
    res.status(500).json({
      status: 'error',
      message: '健康检查失败',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @route GET /health/liveness
 * @route GET /api/health/liveness
 * @desc Kubernetes存活探针端点
 * @access Public
 */
router.get('/liveness', async (req, res) => {
  try {
    // 检查基本服务是否存活
    // 在这里只检查应用本身是否响应
    res.status(200).json({
      status: 'ok',
      service: 'auth-service',
      version: process.env.npm_package_version || '1.0.0',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`存活探针错误: ${error.message}`, { error });
    res.status(500).json({
      status: 'error',
      message: '存活探针检查失败',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @route GET /health/readiness
 * @route GET /api/health/readiness
 * @desc Kubernetes就绪探针端点
 * @access Public
 */
router.get('/readiness', async (req, res) => {
  try {
    // 检查所有依赖服务是否就绪
    const checks = {
      database: false,
      redis: false,
      memory: false
    };
    
    // 检查数据库连接
    try {
      await db.raw('SELECT 1');
      checks.database = true;
    } catch (dbError) {
      logger.error(`数据库连接错误: ${dbError.message}`, { error: dbError });
    }
    
    // 检查Redis连接
    try {
      const redisResult = await redis.ping();
      checks.redis = redisResult === 'PONG';
    } catch (redisError) {
      logger.error(`Redis连接错误: ${redisError.message}`, { error: redisError });
    }
    
    // 检查内存使用情况
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const memoryUsage = 1 - (freeMemory / totalMemory);
    
    // 如果内存使用率超过95%，视为不健康
    checks.memory = memoryUsage < 0.95;
    
    // 所有检查通过才视为就绪
    const isReady = Object.values(checks).every(Boolean);
    
    if (isReady) {
      res.status(200).json({
        status: 'ok',
        service: 'auth-service',
        version: process.env.npm_package_version || '1.0.0',
        checks,
        memoryUsage: Math.round(memoryUsage * 100) + '%',
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(503).json({
        status: 'not_ready',
        message: '服务尚未就绪',
        checks,
        memoryUsage: Math.round(memoryUsage * 100) + '%',
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    logger.error(`就绪探针错误: ${error.message}`, { error });
    res.status(500).json({
      status: 'error',
      message: '就绪探针检查失败',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @route GET /health/detailed
 * @route GET /api/health/detailed
 * @desc 详细健康检查端点
 * @access Public
 */
router.get('/detailed', async (req, res) => {
  try {
    // 检查所有依赖服务是否就绪
    const checks = {
      database: {
        status: 'unknown',
        latency: null
      },
      redis: {
        status: 'unknown',
        latency: null
      },
      system: {
        status: 'unknown',
        memoryUsage: null,
        cpuUsage: null,
        uptime: process.uptime()
      }
    };
    
    // 检查数据库连接
    try {
      const dbStart = Date.now();
      await db.raw('SELECT 1');
      const dbEnd = Date.now();
      checks.database.status = 'ok';
      checks.database.latency = dbEnd - dbStart;
    } catch (dbError) {
      checks.database.status = 'error';
      checks.database.message = dbError.message;
      logger.error(`数据库连接错误: ${dbError.message}`, { error: dbError });
    }
    
    // 检查Redis连接
    try {
      const redisStart = Date.now();
      const redisResult = await redis.ping();
      const redisEnd = Date.now();
      checks.redis.status = redisResult === 'PONG' ? 'ok' : 'error';
      checks.redis.latency = redisEnd - redisStart;
    } catch (redisError) {
      checks.redis.status = 'error';
      checks.redis.message = redisError.message;
      logger.error(`Redis连接错误: ${redisError.message}`, { error: redisError });
    }
    
    // 检查系统资源
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const memoryUsage = 1 - (freeMemory / totalMemory);
    
    // 获取CPU使用率
    const cpus = os.cpus();
    let idleTime = 0;
    let totalTime = 0;
    
    for (const cpu of cpus) {
      idleTime += cpu.times.idle;
      totalTime += cpu.times.user + cpu.times.nice + cpu.times.sys + cpu.times.idle + cpu.times.irq;
    }
    
    const cpuUsage = 1 - idleTime / totalTime;
    
    checks.system.status = 'ok';
    checks.system.memoryUsage = Math.round(memoryUsage * 100) / 100;
    checks.system.cpuUsage = Math.round(cpuUsage * 100) / 100;
    checks.system.totalMemory = totalMemory;
    checks.system.freeMemory = freeMemory;
    checks.system.loadAvg = os.loadavg();
    
    // 检查环境信息
    const envInfo = {
      nodeEnv: process.env.NODE_ENV || 'development',
      region: process.env.REGION || 'unknown',
      hostname: os.hostname()
    };
    
    // 所有检查通过才视为就绪
    const isReady = checks.database.status === 'ok' && checks.redis.status === 'ok';
    
    if (isReady) {
      res.status(200).json({
        status: 'ok',
        service: 'auth-service',
        version: process.env.npm_package_version || '1.0.0',
        checks,
        env: envInfo,
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(503).json({
        status: 'degraded',
        message: '服务部分功能可能不可用',
        checks,
        env: envInfo,
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    logger.error(`详细健康检查错误: ${error.message}`, { error });
    res.status(500).json({
      status: 'error',
      message: '健康检查失败',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @route GET /health/startup
 * @route GET /api/health/startup
 * @desc Kubernetes启动探针端点
 * @access Public
 */
router.get('/startup', async (req, res) => {
  try {
    // 检查应用程序是否已正确启动
    // 这个探针用于确定服务是否已完成启动过程
    
    // 这里可以增加特定的启动检查逻辑，例如：
    // 1. 检查是否完成了所有必要的初始化
    // 2. 检查重要的配置是否已加载
    
    // 简单起见，我们这里只检查应用是否已运行一段时间
    const uptime = process.uptime();
    const isReady = uptime > 5; // 假设5秒后应用程序应该完成启动
    
    if (isReady) {
      res.status(200).json({
        status: 'ok',
        service: 'auth-service',
        version: process.env.npm_package_version || '1.0.0',
        uptime,
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(503).json({
        status: 'starting',
        message: '服务正在启动中',
        uptime,
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    logger.error(`启动探针错误: ${error.message}`, { error });
    res.status(500).json({
      status: 'error',
      message: '启动探针检查失败',
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router; 