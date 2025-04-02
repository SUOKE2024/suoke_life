/**
 * 索儿服务健康检查路由
 * 提供基本健康检查和详细就绪状态检查
 */
const express = require('express');
const router = express.Router();
const { getCircuitBreakerStatus } = require('../../utils/circuit-breaker');
const { incrementCounter } = require('../../metrics');
const config = require('../../config');
const logger = require('../../utils/logger');

// 基本健康检查
router.get('/health', (req, res) => {
  incrementCounter('health_checks_total', { type: 'liveness' });
  
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'soer-service',
    version: config.version
  });
});

// 详细就绪状态检查
router.get('/health/ready', async (req, res) => {
  incrementCounter('health_checks_total', { type: 'readiness' });
  
  try {
    const startTime = Date.now();
    
    const [dbStatus, redisStatus, dependenciesStatus, circuitBreakerStatus] = await Promise.all([
      checkDatabaseConnection(),
      checkRedisConnection(),
      checkDependencies(),
      getCircuitBreakerStatus()
    ]);
    
    const responseTime = Date.now() - startTime;
    
    // 整体状态由所有子检查决定
    const overallStatus = 
      dbStatus.status === 'ok' && 
      redisStatus.status === 'ok' && 
      dependenciesStatus.status === 'ok' && 
      circuitBreakerStatus.status === 'ok' ? 'ok' : 'degraded';
    
    res.json({
      status: overallStatus,
      timestamp: new Date().toISOString(),
      responseTime: `${responseTime}ms`,
      checks: {
        database: dbStatus,
        redis: redisStatus,
        dependencies: dependenciesStatus,
        circuitBreaker: circuitBreakerStatus
      }
    });
  } catch (error) {
    logger.error('就绪检查失败', { error: error.message });
    res.status(500).json({
      status: 'error',
      timestamp: new Date().toISOString(),
      error: '就绪检查执行过程中发生错误'
    });
  }
});

// 数据库连接检查
async function checkDatabaseConnection() {
  const startTime = Date.now();
  try {
    // 从连接池获取连接并执行简单查询
    const db = require('../../db');
    await db.query('SELECT 1');
    
    const responseTime = Date.now() - startTime;
    return {
      status: 'ok',
      responseTime: `${responseTime}ms`
    };
  } catch (error) {
    logger.error('数据库健康检查失败', { error: error.message });
    const responseTime = Date.now() - startTime;
    return {
      status: 'error',
      responseTime: `${responseTime}ms`,
      error: error.message
    };
  }
}

// Redis连接检查
async function checkRedisConnection() {
  const startTime = Date.now();
  try {
    // 尝试设置和获取一个健康检查键
    const redis = require('../../redis');
    const testKey = 'health:test:' + Date.now();
    await redis.set(testKey, 'ok', 'EX', 5); // 5秒过期
    const value = await redis.get(testKey);
    
    const responseTime = Date.now() - startTime;
    return {
      status: value === 'ok' ? 'ok' : 'error',
      responseTime: `${responseTime}ms`
    };
  } catch (error) {
    logger.error('Redis健康检查失败', { error: error.message });
    const responseTime = Date.now() - startTime;
    return {
      status: 'error',
      responseTime: `${responseTime}ms`,
      error: error.message
    };
  }
}

// 依赖服务检查
async function checkDependencies() {
  const startTime = Date.now();
  try {
    // 检查必要的外部服务依赖
    const services = config.dependencies || [];
    const results = {};
    let allOk = true;
    
    for (const service of services) {
      try {
        // 简单的健康检查请求
        const axios = require('axios');
        const response = await axios.get(`${service.url}/health`, { 
          timeout: 2000,
          headers: { 'User-Agent': 'SoerService/HealthCheck' }
        });
        
        results[service.name] = {
          status: response.status === 200 ? 'ok' : 'error',
          statusCode: response.status
        };
        
        if (response.status !== 200) {
          allOk = false;
        }
      } catch (error) {
        results[service.name] = {
          status: 'error',
          error: error.message
        };
        allOk = false;
      }
    }
    
    const responseTime = Date.now() - startTime;
    return {
      status: allOk ? 'ok' : 'degraded',
      responseTime: `${responseTime}ms`,
      services: results
    };
  } catch (error) {
    logger.error('依赖健康检查失败', { error: error.message });
    const responseTime = Date.now() - startTime;
    return {
      status: 'error',
      responseTime: `${responseTime}ms`,
      error: error.message
    };
  }
}

module.exports = router;