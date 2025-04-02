/**
 * 索儿服务API路由
 */
const express = require('express');
const router = express.Router();
const { createCircuitBreaker } = require('../../utils/circuit-breaker');
const logger = require('../../utils/logger');

// 基本API信息路由
router.get('/', (req, res) => {
  res.json({
    service: 'soer-service',
    description: '索克生活平台 - 索儿微服务',
    version: require('../../config').version,
    endpoints: [
      { path: '/info', description: '获取API基本信息' },
      { path: '/growth', description: '儿童生长发育曲线相关接口' },
      { path: '/nutrition', description: '儿童营养饮食相关接口' },
      { path: '/constitution', description: '儿童体质评估相关接口' },
      { path: '/knowledge', description: '儿童健康知识相关接口' },
      { path: '/recommendations', description: '健康和生活建议推荐相关接口' },
      { path: '/lifestyle', description: '生活方式管理相关接口' },
      { path: '/users', description: '用户相关接口，包括日常活动管理' }
    ]
  });
});

// 引入各个子路由
// 注意：这些路由文件需要单独创建，这里仅为示例
// router.use('/growth', require('./growth'));
// router.use('/nutrition', require('./nutrition'));
// router.use('/constitution', require('./constitution'));
// router.use('/knowledge', require('./knowledge'));

// 使用推荐路由
router.use('/recommendations', require('./recommendations.routes')(router.app));

// 使用生活方式路由
router.use('/lifestyle', require('./lifestyle.routes')(router.app));

// 使用日常活动路由（通过用户路径访问）
router.use('/users', require('../dailyActivities.routes')(router.app));

// 未实现的API占位
router.all('/:apiPath*', (req, res) => {
  logger.warn(`尝试访问未实现的API: ${req.path}`);
  res.status(501).json({
    error: {
      message: '该API尚未实现',
      code: 'NOT_IMPLEMENTED',
      request_id: req.requestId
    }
  });
});

module.exports = router;