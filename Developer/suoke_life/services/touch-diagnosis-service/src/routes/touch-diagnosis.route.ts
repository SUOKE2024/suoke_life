import { Router } from 'express';
import * as touchDiagnosisController from '../controllers/touch-diagnosis.controller';

const router = Router();

/**
 * @route  POST /api/touch-diagnosis
 * @desc   创建触诊记录
 * @access 私有
 */
router.post('/', touchDiagnosisController.createTouchDiagnosis);

/**
 * @route  GET /api/touch-diagnosis/patient/:patientId
 * @desc   获取患者最新触诊记录
 * @access 私有
 */
router.get('/patient/:patientId', touchDiagnosisController.getPatientTouchDiagnosis);

/**
 * @route  GET /api/touch-diagnosis/:diagnosisId
 * @desc   根据ID获取触诊记录
 * @access 私有
 */
router.get('/:diagnosisId', touchDiagnosisController.getTouchDiagnosisById);

/**
 * @route  POST /api/touch-diagnosis/analyze/:patientId
 * @desc   分析患者触诊数据
 * @access 私有
 */
router.post('/analyze/:patientId', touchDiagnosisController.analyzeTouchDiagnosis);

/**
 * @route  GET /api/touch-diagnosis/history/:patientId
 * @desc   获取患者触诊历史记录
 * @access 私有
 */
router.get('/history/:patientId', touchDiagnosisController.getPatientTouchDiagnosisHistory);

export default router; 