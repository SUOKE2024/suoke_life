import { Router } from 'express';
import { diagnosisController } from '../controllers/diagnosisController';

const router = Router();

/**
 * @route POST /api/diagnosis/initiate
 * @desc 启动诊断流程
 * @access Public
 */
router.post('/initiate', diagnosisController.initiateDiagnosisFlow);

/**
 * @route GET /api/diagnosis/services
 * @desc 获取所有可用的诊断服务
 * @access Public
 */
router.get('/services', diagnosisController.getAvailableDiagnosticServices);

/**
 * @route GET /api/diagnosis/status/:userId
 * @desc 获取用户当前的诊断状态
 * @access Public
 */
router.get('/status/:userId', diagnosisController.getUserDiagnosisStatus);

/**
 * @route POST /api/diagnosis/coordinate
 * @desc 协调多个诊断服务之间的操作
 * @access Public
 */
router.post('/coordinate', diagnosisController.coordinateDiagnosticServices);

/**
 * @route POST /api/diagnosis/complete/:userId
 * @desc 完成诊断流程
 * @access Public
 */
router.post('/complete/:userId', diagnosisController.completeDiagnosisFlow);

/**
 * @route GET /api/diagnosis/history/:userId
 * @desc 获取用户的诊断历史
 * @access Public
 */
router.get('/history/:userId', diagnosisController.getUserDiagnosisHistory);

export default router;