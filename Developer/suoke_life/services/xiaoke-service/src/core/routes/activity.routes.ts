import express from 'express';
import { Server } from 'socket.io';
import { requireAuth } from '../middleware/auth.middleware';
import controller from '../../controllers/activity.controller';

/**
 * 活动路由
 */
export default (io: Server): express.Router => {
  const router = express.Router();

  // 获取活动列表
  router.get('/', controller.getActivities);

  // 获取热门活动
  router.get('/popular', controller.getPopularActivities);

  // 获取活动详情
  router.get('/:id', controller.getActivityById);

  // 活动预约（需要登录）
  router.post('/:id/register', requireAuth, controller.registerForActivity);

  // 提交活动评价（需要登录）
  router.post('/:id/review', requireAuth, controller.addActivityReview);

  return router;
}; 