/**
 * 指标控制器
 */
const express = require('express');
const metricsService = require('../services/metrics.service');
const router = express.Router();

/**
 * @swagger
 * /api/metrics:
 *   get:
 *     tags: [系统]
 *     summary: 获取系统指标
 *     description: 获取所有系统监控指标
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 成功返回指标数据
 *       401:
 *         description: 未授权访问
 */
router.get('/', (req, res) => {
  res.json(metricsService.getMetrics());
});

/**
 * @swagger
 * /api/metrics:
 *   delete:
 *     tags: [系统]
 *     summary: 重置系统指标
 *     description: 清除所有系统监控指标
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       204:
 *         description: 成功重置指标
 *       401:
 *         description: 未授权访问
 */
router.delete('/', (req, res) => {
  metricsService.reset();
  res.status(204).end();
});

module.exports = router;
