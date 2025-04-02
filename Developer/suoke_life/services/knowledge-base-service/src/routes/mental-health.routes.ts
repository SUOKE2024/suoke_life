/**
 * 心理健康知识路由
 */
import express from 'express';
import { requireAuth } from '../middlewares/require-auth';
import { validateRequest } from '../middlewares/validate-request';
import mentalHealthController from '../controllers/mental-health.controller';

const router = express.Router();

// 获取心理健康知识列表
router.get(
  '/',
  mentalHealthController.getMentalHealthList
);

// 获取心理健康知识详情
router.get(
  '/:id',
  mentalHealthController.getMentalHealth
);

// 按心理问题类型获取心理健康知识
router.get(
  '/issue/:type',
  mentalHealthController.getMentalHealthByIssueType
);

// 按年龄组获取心理健康知识
router.get(
  '/age-group/:ageGroup',
  mentalHealthController.getMentalHealthByAgeGroup
);

// 按干预方法获取心理健康知识
router.get(
  '/intervention/:method',
  mentalHealthController.getMentalHealthByInterventionMethod
);

// 搜索心理健康知识
router.get(
  '/search/:keyword',
  mentalHealthController.searchMentalHealth
);

// 创建心理健康知识（需要认证）
router.post(
  '/',
  requireAuth,
  // 可以添加验证中间件
  mentalHealthController.createMentalHealth
);

// 更新心理健康知识（需要认证）
router.put(
  '/:id',
  requireAuth,
  // 可以添加验证中间件
  mentalHealthController.updateMentalHealth
);

// 删除心理健康知识（需要认证）
router.delete(
  '/:id',
  requireAuth,
  mentalHealthController.deleteMentalHealth
);

export { router as mentalHealthRoutes };