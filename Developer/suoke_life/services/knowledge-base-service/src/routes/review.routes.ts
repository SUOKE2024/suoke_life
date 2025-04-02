/**
 * 知识审核路由
 */
import express from 'express';
import { requireAuth } from '../middlewares/require-auth';
import { requireAdmin } from '../middlewares/require-admin';
import reviewController from '../controllers/review.controller';

const router = express.Router();

// 提交知识条目审核
router.post(
  '/:knowledgeType/:id/submit',
  requireAuth,
  reviewController.submitForReview
);

// 列出待审核的知识条目（需要管理员权限）
router.get(
  '/pending',
  requireAuth,
  requireAdmin,
  reviewController.getPendingReviews
);

// 审核通过知识条目（需要管理员权限）
router.post(
  '/:reviewId/approve',
  requireAuth,
  requireAdmin,
  reviewController.approveReview
);

// 拒绝知识条目审核（需要管理员权限）
router.post(
  '/:reviewId/reject',
  requireAuth,
  requireAdmin,
  reviewController.rejectReview
);

// 获取知识条目的审核历史
router.get(
  '/:knowledgeType/:id/history',
  requireAuth,
  reviewController.getReviewHistory
);

// 获取审核详情
router.get(
  '/:reviewId',
  requireAuth,
  reviewController.getReviewDetails
);

export { router as reviewRoutes };