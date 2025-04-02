import { Router, Request, Response } from 'express';
import xiaoaiRoutes from './xiaoaiRoutes';
import accessibilityRoutes from './accessibilityRoutes';
import diagnosisRoutes from './diagnosisRoutes';
import dialectRoutes from './dialectRoutes';

const router = Router();

// 健康检查路由
router.get('/health', (req: Request, res: Response) => {
  res.status(200).json({ status: 'OK', timestamp: new Date().toISOString() });
});

// 注册路由
router.use('/xiaoai', xiaoaiRoutes);
router.use('/accessibility', accessibilityRoutes);
router.use('/diagnosis', diagnosisRoutes);
router.use('/dialect', dialectRoutes);

export default router;