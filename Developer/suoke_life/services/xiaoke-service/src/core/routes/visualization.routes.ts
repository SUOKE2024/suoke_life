import { Router } from 'express';
import { Server } from 'socket.io';
import visualizationController from '../../controllers/visualization.controller';
import { auth } from '../middleware/auth.middleware';

/**
 * 溯源可视化路由
 * 处理与溯源数据可视化相关的HTTP路由
 */
export default function(io: Server): Router {
  const router = Router();

  /**
   * @route   GET /api/v1/visualization/chain/:id
   * @desc    获取溯源链数据（用于前端绘制流程图）
   * @access  Public
   */
  router.get('/chain/:id', (req, res) => {
    visualizationController.getTraceabilityChain(req, res);
  });

  /**
   * @route   GET /api/v1/visualization/geo-distribution
   * @desc    获取供应链地理分布数据（用于地图可视化）
   * @access  Private (Admin, Producer)
   */
  router.get('/geo-distribution', auth(['admin', 'producer']), (req, res) => {
    visualizationController.getSupplyChainGeoDistribution(req, res);
  });

  /**
   * @route   GET /api/v1/visualization/analytics
   * @desc    获取溯源数据分析和趋势
   * @access  Private (Admin)
   */
  router.get('/analytics', auth(['admin']), (req, res) => {
    visualizationController.getTraceabilityAnalytics(req, res);
  });

  /**
   * @route   GET /api/v1/visualization/quality-monitoring
   * @desc    获取质量监控数据
   * @access  Private (Admin, Producer)
   */
  router.get('/quality-monitoring', auth(['admin', 'producer']), (req, res) => {
    visualizationController.getQualityMonitoringData(req, res);
  });

  return router;
} 