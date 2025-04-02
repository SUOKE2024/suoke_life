/**
 * 指标控制器
 * @module controllers/metrics
 */
const express = require('express');
const metricsService = require('../services/metrics.service');
const logger = require('../utils/logger');

const router = express.Router();

/**
 * @swagger
 * /api/metrics:
 *   get:
 *     summary: 获取系统指标
 *     description: 获取所有系统指标数据，包括计数器、仪表盘、计时器和直方图
 *     tags: [监控]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 成功返回系统指标
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 counters:
 *                   type: object
 *                   description: 计数器指标
 *                 gauges:
 *                   type: object
 *                   description: 仪表盘指标
 *                 timers:
 *                   type: object
 *                   description: 计时器指标
 *                 histograms:
 *                   type: object
 *                   description: 直方图指标
 *       401:
 *         description: 未授权访问
 *       500:
 *         description: 服务器错误
 */
router.get('/', (req, res) => {
  try {
    const metrics = metricsService.getMetrics();
    res.json(metrics);
    logger.debug('指标获取成功');
  } catch (error) {
    logger.error('获取指标失败', error);
    res.status(500).json({ error: '获取指标失败' });
  }
});

/**
 * @swagger
 * /api/metrics:
 *   delete:
 *     summary: 重置系统指标
 *     description: 重置所有系统指标，包括计数器、仪表盘、计时器和直方图
 *     tags: [监控]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       204:
 *         description: 成功重置系统指标
 *       401:
 *         description: 未授权访问
 *       500:
 *         description: 服务器错误
 */
router.delete('/', (req, res) => {
  try {
    metricsService.reset();
    res.status(204).end();
    logger.debug('指标重置成功');
  } catch (error) {
    logger.error('重置指标失败', error);
    res.status(500).json({ error: '重置指标失败' });
  }
});

module.exports = router; 