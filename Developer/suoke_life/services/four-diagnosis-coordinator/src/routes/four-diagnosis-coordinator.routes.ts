import { Router } from 'express';
import { body, param } from 'express-validator';
import * as fourDiagnosisController from '../controllers/four-diagnosis-coordinator.controller';

const router = Router();

/**
 * @route   GET /api/four-diagnosis/:patientId
 * @desc    获取患者四诊数据
 * @access  Private
 */
router.get(
  '/:patientId',
  [
    param('patientId').isString().notEmpty().withMessage('患者ID不能为空')
  ],
  fourDiagnosisController.getPatientFourDiagnosisData
);

/**
 * @route   POST /api/four-diagnosis/analyze
 * @desc    分析患者四诊数据，提供综合诊断
 * @access  Private
 */
router.post(
  '/analyze',
  [
    body('patientId').isString().notEmpty().withMessage('患者ID不能为空')
  ],
  fourDiagnosisController.analyzeFourDiagnosis
);

/**
 * @route   GET /api/four-diagnosis/:patientId/history
 * @desc    获取患者诊断历史记录
 * @access  Private
 */
router.get(
  '/:patientId/history',
  [
    param('patientId').isString().notEmpty().withMessage('患者ID不能为空')
  ],
  fourDiagnosisController.getPatientDiagnosisHistory
);

/**
 * @route   GET /health
 * @desc    健康检查端点
 * @access  Public
 */
router.get('/health', fourDiagnosisController.healthCheck);

export default router; 