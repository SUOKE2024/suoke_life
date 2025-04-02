/**
 * API路由入口
 */
const express = require('express');
const router = express.Router();

// 导入各模块路由
const mazeRoutes = require('./maze.routes');
const treasureRoutes = require('./treasure.routes');
const plantRoutes = require('./plant.routes');
const teamRoutes = require('./team.routes');

// API版本
const API_VERSION = '/v1';

// 基础路由
router.get('/', (req, res) => {
  res.json({
    service: 'corn-maze-service',
    version: '1.0.0',
    status: 'running',
    endpoints: [
      '/maze',
      '/treasure',
      '/plant',
      '/team'
    ]
  });
});

// 注册各模块路由
router.use(`${API_VERSION}/maze`, mazeRoutes);
router.use(`${API_VERSION}/treasure`, treasureRoutes);
router.use(`${API_VERSION}/plant`, plantRoutes);
router.use(`${API_VERSION}/team`, teamRoutes);

module.exports = router;
