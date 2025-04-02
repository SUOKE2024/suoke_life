/**
 * 版本管理路由
 */
import express from 'express';
import { requireAuth } from '../middlewares/require-auth';
import versionController from '../controllers/version.controller';

const router = express.Router();

// 获取知识条目的所有版本历史
router.get(
  '/:knowledgeType/:id',
  versionController.getVersionHistory
);

// 获取特定版本的知识条目
router.get(
  '/:knowledgeType/:id/:version',
  versionController.getSpecificVersion
);

// 创建新版本（回滚到特定版本）
router.post(
  '/:knowledgeType/:id/rollback/:version',
  requireAuth,
  versionController.rollbackToVersion
);

// 比较两个版本的差异
router.get(
  '/:knowledgeType/:id/compare',
  versionController.compareVersions
);

export { router as versionRoutes };