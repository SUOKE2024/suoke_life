/**
 * 指标收集路由
 */
const express = require('express');
const router = express.Router();
const config = require('../config');
const logger = require('../utils/logger');
const metricsService = require('../services/metrics.service');

/**
 * @route GET /metrics
 * @route GET /api/metrics
 * @desc Prometheus指标端点
 * @access Public (通常应限制访问)
 */
router.get('/', async (req, res) => {
  try {
    // 检查访问令牌（如果配置了）
    const token = req.query.token || req.headers['x-metrics-token'];
    
    if (config.metrics?.requireToken && config.metrics?.token) {
      if (token !== config.metrics.token) {
        return res.status(401).send('未授权：缺少有效的指标访问令牌');
      }
    }
    
    // 获取并返回指标数据
    const metrics = await metricsService.getMetrics();
    
    // 设置正确的内容类型
    res.setHeader('Content-Type', 'text/plain');
    res.status(200).send(metrics);
  } catch (error) {
    logger.error(`获取指标数据错误: ${error.message}`, { error });
    res.status(500).send('获取指标数据失败');
  }
});

/**
 * @route GET /metrics/info
 * @route GET /api/metrics/info
 * @desc 指标概况信息
 * @access Public (通常应限制访问)
 */
router.get('/info', async (req, res) => {
  try {
    // 检查访问令牌（如果配置了）
    const token = req.query.token || req.headers['x-metrics-token'];
    
    if (config.metrics?.requireToken && config.metrics?.token) {
      if (token !== config.metrics.token) {
        return res.status(401).json({
          success: false,
          message: '未授权：缺少有效的指标访问令牌'
        });
      }
    }
    
    // 获取指标信息（这不是原始指标数据，而是有关指标的元信息）
    // 首先检查指标收集是否启用
    if (!config.metrics?.enabled) {
      return res.status(200).json({
        success: true,
        enabled: false,
        message: '指标收集已禁用'
      });
    }
    
    res.status(200).json({
      success: true,
      enabled: true,
      prefix: config.metrics?.prefix || 'auth_service_',
      endpoint: '/metrics',
      requireToken: !!config.metrics?.requireToken,
      collectSystemMetrics: config.metrics?.collectSystemMetrics !== false,
      systemMetricsInterval: config.metrics?.systemMetricsInterval || 15000,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`获取指标信息错误: ${error.message}`, { error });
    res.status(500).json({
      success: false,
      message: '获取指标信息失败',
      error: error.message
    });
  }
});

/**
 * @route POST /metrics/reset
 * @route POST /api/metrics/reset
 * @desc 重置指标计数器（仅用于测试环境）
 * @access Protected (仅限管理员)
 */
router.post('/reset', async (req, res) => {
  try {
    // 这个端点应该仅在非生产环境中使用
    if (config.env === 'production') {
      return res.status(403).json({
        success: false,
        message: '在生产环境中不允许重置指标'
      });
    }
    
    // 检查管理员访问令牌
    const token = req.query.token || req.headers['x-admin-token'] || req.body.token;
    
    if (!token || token !== config.admin?.token) {
      return res.status(401).json({
        success: false,
        message: '未授权：需要管理员访问令牌'
      });
    }
    
    // 目前我们没有实现重置功能，这通常需要重新注册指标收集器
    res.status(501).json({
      success: false,
      message: '重置指标功能尚未实现'
    });
  } catch (error) {
    logger.error(`重置指标错误: ${error.message}`, { error });
    res.status(500).json({
      success: false,
      message: '重置指标失败',
      error: error.message
    });
  }
});

module.exports = router; 