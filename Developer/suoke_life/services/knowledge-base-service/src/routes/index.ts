/**
 * 路由索引文件
 * 整合所有路由
 */
import express from 'express';
import { knowledgeRoutes } from './knowledge.routes';
import { tagRoutes } from './tag.routes';
import { categoryRoutes } from './category.routes';
import { nutritionRoutes } from './nutrition.routes';
import { lifestyleRoutes } from './lifestyle.routes';
import { medicalRoutes } from './medical.routes';
import { tcmRoutes } from './tcm.routes';
import { environmentalHealthRoutes } from './environmental-health.routes';
import { mentalHealthRoutes } from './mental-health.routes';
import { versionRoutes } from './version.routes';
import { reviewRoutes } from './review.routes';

const router = express.Router();

// 各知识领域路由
router.use('/knowledge', knowledgeRoutes);
router.use('/tags', tagRoutes);
router.use('/categories', categoryRoutes);
router.use('/nutrition', nutritionRoutes);
router.use('/lifestyle', lifestyleRoutes);
router.use('/medical', medicalRoutes);
router.use('/tcm', tcmRoutes);
router.use('/environmental-health', environmentalHealthRoutes);
router.use('/mental-health', mentalHealthRoutes);

// 版本管理路由
router.use('/versions', versionRoutes);

// 知识审核路由
router.use('/reviews', reviewRoutes);

export { router as apiRoutes };