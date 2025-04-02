/**
 * 主路由模块
 */
const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const controllers = require('../controllers');
const canaryRoutes = require('./canary');

// 健康检查路由
router.get('/health', controllers.healthCheck);
router.get('/health/ready', controllers.readinessCheck);

// Prometheus指标路由
router.get('/metrics/prometheus', controllers.getMetrics);

// 系统信息路由
router.get('/system/info', controllers.getSystemInfo);

// 灰度发布管理API
router.use('/api/canary', canaryRoutes);

// API文档路由
router.get('/docs', (req, res) => {
  const docPath = path.join(__dirname, '../../API.md');
  if (fs.existsSync(docPath)) {
    res.sendFile(docPath);
  } else {
    res.status(404).send('API文档未找到');
  }
});

// 路由根路径默认返回API信息
router.get('/', (req, res) => {
  res.json({
    service: '索克生活API网关',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      ready: '/health/ready',
      metrics: '/metrics',
      docs: '/docs',
      canary: '/api/canary'
    },
    message: '欢迎使用索克生活API网关服务'
  });
});

module.exports = router;