/**
 * 内部API路由
 * 用于服务间通信和跨区域同步
 */
const express = require('express');
const router = express.Router();
const { logger } = require('@suoke/shared').utils;
const { handleIncomingSyncRequest, getSyncStatus } = require('../utils/sync');
const { vaultService } = require('../services/vault.service');
const { internalAuthMiddleware } = require('../middlewares/internal-auth');
const healthChecks = require('../utils/health-checks');

// 应用内部认证中间件
router.use(internalAuthMiddleware);

/**
 * @route POST /api/v1/internal/sync
 * @desc 处理从其他区域接收的同步请求
 * @access 内部
 */
router.post('/sync', async (req, res) => {
  try {
    const sourceRegion = req.headers['x-source-region'];
    const syncData = req.body;
    
    if (!sourceRegion) {
      logger.warn('收到缺少源区域标识的同步请求');
      return res.status(400).json({ success: false, message: '缺少源区域标识' });
    }
    
    logger.debug(`接收到来自区域 ${sourceRegion} 的同步请求: ${syncData.operation_id}`);
    
    const result = await handleIncomingSyncRequest(syncData);
    
    if (result.success) {
      return res.json({ success: true, message: result.message || '同步成功' });
    } else {
      return res.status(400).json({ success: false, message: result.message || '同步失败' });
    }
  } catch (error) {
    logger.error(`处理同步请求出错: ${error.message}`);
    return res.status(500).json({ success: false, message: '内部服务器错误' });
  }
});

/**
 * @route GET /api/v1/internal/sync/status
 * @desc 获取同步状态信息
 * @access 内部
 */
router.get('/sync/status', async (req, res) => {
  try {
    const status = await getSyncStatus();
    return res.json(status);
  } catch (error) {
    logger.error(`获取同步状态出错: ${error.message}`);
    return res.status(500).json({ success: false, message: '内部服务器错误' });
  }
});

/**
 * @route POST /api/v1/internal/sync/trigger
 * @desc 手动触发同步
 * @access 内部
 */
router.post('/sync/trigger', async (req, res) => {
  try {
    const { syncAllRegions } = require('../utils/sync');
    const result = await syncAllRegions();
    return res.json(result);
  } catch (error) {
    logger.error(`触发同步出错: ${error.message}`);
    return res.status(500).json({ success: false, message: '内部服务器错误' });
  }
});

/**
 * @route GET /api/v1/internal/health/deep
 * @desc 深度健康检查
 * @access 内部
 */
router.get('/health/deep', async (req, res) => {
  try {
    const result = await healthChecks.deepHealthCheck();
    
    if (result.status === 'healthy') {
      return res.json(result);
    } else {
      return res.status(503).json(result);
    }
  } catch (error) {
    logger.error(`深度健康检查出错: ${error.message}`);
    return res.status(500).json({ 
      status: 'error',
      message: '获取健康状态失败',
      error: error.message
    });
  }
});

/**
 * @route POST /api/v1/internal/secrets/refresh
 * @desc 刷新密钥
 * @access 内部
 */
router.post('/secrets/refresh', async (req, res) => {
  try {
    const result = await vaultService.refreshSecrets();
    
    if (result.success) {
      return res.json({ success: true, message: '密钥刷新成功' });
    } else {
      return res.status(500).json({ success: false, message: result.message || '密钥刷新失败' });
    }
  } catch (error) {
    logger.error(`刷新密钥出错: ${error.message}`);
    return res.status(500).json({ success: false, message: '内部服务器错误' });
  }
});

/**
 * @route GET /api/v1/internal/metrics
 * @desc 获取服务内部指标
 * @access 内部
 */
router.get('/metrics', async (req, res) => {
  try {
    const prometheusClient = require('prom-client');
    const register = prometheusClient.register;
    
    const metrics = await register.metrics();
    res.set('Content-Type', register.contentType);
    return res.end(metrics);
  } catch (error) {
    logger.error(`获取指标出错: ${error.message}`);
    return res.status(500).json({ success: false, message: '内部服务器错误' });
  }
});

module.exports = router; 