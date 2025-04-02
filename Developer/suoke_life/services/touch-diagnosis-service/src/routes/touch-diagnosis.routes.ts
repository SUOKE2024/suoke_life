import { Router } from 'express';
import { body } from 'express-validator';
import * as touchDiagnosisController from '../controllers/touch-diagnosis.controller';
import { TouchLocation, PulseType, AbdominalFindingType } from '../interfaces/touch-diagnosis.interface';

const router = Router();

/**
 * @route   POST /api/touch-diagnosis/pulse
 * @desc    提交脉诊数据
 * @access  Private
 */
router.post(
  '/pulse',
  [
    body('patientId').isString().notEmpty().withMessage('患者ID不能为空'),
    body('practitionerId').isString().notEmpty().withMessage('医师ID不能为空'),
    body('pulseData').isArray().withMessage('脉诊数据必须是数组'),
    body('pulseData.*.location').isIn(Object.values(TouchLocation)).withMessage('无效的位置'),
    body('pulseData.*.pulseType').isIn(Object.values(PulseType)).withMessage('无效的脉象类型'),
    body('pulseData.*.strength').isFloat({ min: 0, max: 1 }).withMessage('强度必须是0-1之间的数值'),
    body('pulseData.*.rhythm').isFloat({ min: 0, max: 1 }).withMessage('节律必须是0-1之间的数值'),
    body('pulseData.*.frequency').isInt({ min: 40, max: 120 }).withMessage('脉率必须是40-120之间的整数'),
  ],
  touchDiagnosisController.recordPulseDiagnosis
);

/**
 * @route   POST /api/touch-diagnosis/abdominal
 * @desc    提交腹诊数据
 * @access  Private
 */
router.post(
  '/abdominal',
  [
    body('patientId').isString().notEmpty().withMessage('患者ID不能为空'),
    body('practitionerId').isString().notEmpty().withMessage('医师ID不能为空'),
    body('abdominalData').isArray().withMessage('腹诊数据必须是数组'),
    body('abdominalData.*.location').isIn(Object.values(TouchLocation)).withMessage('无效的位置'),
    body('abdominalData.*.findingType').isIn(Object.values(AbdominalFindingType)).withMessage('无效的发现类型'),
    body('abdominalData.*.intensity').isFloat({ min: 0, max: 1 }).withMessage('强度必须是0-1之间的数值'),
  ],
  touchDiagnosisController.recordAbdominalDiagnosis
);

/**
 * @route   POST /api/touch-diagnosis/analyze
 * @desc    分析触诊数据并生成结论
 * @access  Private
 */
router.post(
  '/analyze',
  [
    body('patientId').isString().notEmpty().withMessage('患者ID不能为空'),
  ],
  touchDiagnosisController.analyzeTouchDiagnosis
);

/**
 * @route   GET /api/touch-diagnosis/:patientId
 * @desc    获取患者的触诊记录
 * @access  Private
 */
router.get(
  '/:patientId',
  touchDiagnosisController.getPatientTouchDiagnosis
);

/**
 * @route   GET /api/touch-diagnosis/:patientId/history
 * @desc    获取患者的触诊历史记录
 * @access  Private
 */
router.get(
  '/:patientId/history',
  touchDiagnosisController.getPatientTouchDiagnosisHistory
);

export default router; 