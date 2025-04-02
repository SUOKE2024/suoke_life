import { Router } from 'express';
import inquiryRoutes from './inquiry.routes';
import diagnosisRoutes from './diagnosis.routes';
import coordinatorRoutes from './coordinator.routes';

const router = Router();

/**
 * @swagger
 * components:
 *   securitySchemes:
 *     bearerAuth:
 *       type: http
 *       scheme: bearer
 *       bearerFormat: JWT
 *     apiKeyAuth:
 *       type: apiKey
 *       in: header
 *       name: X-API-KEY
 */

/**
 * @swagger
 * tags:
 *   - name: 问诊
 *     description: 问诊会话管理和交互API
 *   - name: 诊断
 *     description: 中医辨证分析和诊断结果API
 *   - name: 四诊协调
 *     description: 四诊协调服务集成API
 */

// 注册路由
router.use('/inquiry', inquiryRoutes);
router.use('/diagnosis', diagnosisRoutes);
router.use('/coordinator', coordinatorRoutes);

// 健康检查路由
/**
 * @swagger
 * /api/health:
 *   get:
 *     summary: 服务健康检查
 *     description: 返回服务的健康状态和基本信息
 *     tags: [系统]
 *     responses:
 *       200:
 *         description: 服务正常运行
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: "UP"
 *                 service:
 *                   type: string
 *                   example: "inquiry-diagnosis-service"
 *                 version:
 *                   type: string
 *                   example: "1.0.0"
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 */
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'inquiry-diagnosis-service',
    version: process.env.npm_package_version || '1.0.0',
    timestamp: new Date().toISOString()
  });
});

export default router;