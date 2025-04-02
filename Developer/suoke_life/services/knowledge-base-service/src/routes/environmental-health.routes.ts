/**
 * 环境健康知识路由
 */
import express from 'express';
import { requireAuth } from '../middlewares/require-auth';
import { validateRequest } from '../middlewares/validate-request';
import environmentalHealthController from '../controllers/environmental-health.controller';

const router = express.Router();

// 获取环境健康知识列表
router.get(
  '/',
  environmentalHealthController.getEnvironmentalHealthList
);

// 获取环境健康知识详情
router.get(
  '/:id',
  environmentalHealthController.getEnvironmentalHealth
);

// 按环境类型获取环境健康知识
router.get(
  '/type/:type',
  environmentalHealthController.getEnvironmentalHealthByType
);

// 按污染物类型获取环境健康知识
router.get(
  '/pollutant/:pollutant',
  environmentalHealthController.getEnvironmentalHealthByPollutant
);

// 按健康影响获取环境健康知识
router.get(
  '/impact/:impact',
  environmentalHealthController.getEnvironmentalHealthByHealthImpact
);

// 按地区获取环境健康知识
router.get(
  '/region/:region',
  environmentalHealthController.getEnvironmentalHealthByRegion
);

// 按风险级别获取环境健康知识
router.get(
  '/risk/:level',
  environmentalHealthController.getEnvironmentalHealthByRiskLevel
);

// 搜索环境健康知识
router.get(
  '/search/:keyword',
  environmentalHealthController.searchEnvironmentalHealth
);

// 创建环境健康知识（需要认证）
router.post(
  '/',
  requireAuth,
  // 可以添加验证中间件
  environmentalHealthController.createEnvironmentalHealth
);

// 更新环境健康知识（需要认证）
router.put(
  '/:id',
  requireAuth,
  // 可以添加验证中间件
  environmentalHealthController.updateEnvironmentalHealth
);

// 删除环境健康知识（需要认证）
router.delete(
  '/:id',
  requireAuth,
  environmentalHealthController.deleteEnvironmentalHealth
);

export { router as environmentalHealthRoutes };