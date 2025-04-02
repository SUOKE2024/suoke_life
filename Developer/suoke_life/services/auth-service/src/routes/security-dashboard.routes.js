/**
 * 安全控制面板路由
 */
const express = require('express');
const router = express.Router();
const securityDashboardController = require('../controllers/security-dashboard.controller');
const { BearerAuth, ApiRateLimit, RoleAuthorization } = require('@suoke/shared').middlewares;

// 仅允许管理员访问安全控制面板
const adminOnly = RoleAuthorization.hasRole(['admin', 'security_admin']);

// 安全控制面板页面
router.get(
  '/', 
  BearerAuth.authenticate, 
  adminOnly,
  securityDashboardController.renderDashboard
);

// 安全统计数据API
router.get(
  '/api/stats', 
  BearerAuth.authenticate, 
  adminOnly,
  ApiRateLimit.createLimiter({ windowMs: 60 * 1000, max: 10 }),
  securityDashboardController.getSecurityStats
);

// 安全活动图表数据API
router.get(
  '/api/chart-data', 
  BearerAuth.authenticate, 
  adminOnly,
  ApiRateLimit.createLimiter({ windowMs: 60 * 1000, max: 5 }),
  securityDashboardController.getSecurityChartData
);

// 最近登录活动API
router.get(
  '/api/login-activities', 
  BearerAuth.authenticate, 
  adminOnly,
  ApiRateLimit.createLimiter({ windowMs: 60 * 1000, max: 10 }),
  securityDashboardController.getRecentLoginActivities
);

// 异常活动API
router.get(
  '/api/anomalies', 
  BearerAuth.authenticate, 
  adminOnly,
  ApiRateLimit.createLimiter({ windowMs: 60 * 1000, max: 10 }),
  securityDashboardController.getAnomalies
);

// 活跃设备API
router.get(
  '/api/active-devices', 
  BearerAuth.authenticate, 
  adminOnly,
  ApiRateLimit.createLimiter({ windowMs: 60 * 1000, max: 10 }),
  securityDashboardController.getActiveDevices
);

// 安全建议API
router.get(
  '/api/recommendations', 
  BearerAuth.authenticate, 
  adminOnly,
  ApiRateLimit.createLimiter({ windowMs: 60 * 1000, max: 5 }),
  securityDashboardController.getSecurityRecommendations
);

module.exports = router;