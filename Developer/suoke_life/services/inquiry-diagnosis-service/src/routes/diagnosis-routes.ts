import express from 'express';
import { Container } from 'typedi';
import { DiagnosisController } from '../controllers/diagnosis.controller';
import * as validationMiddleware from '../middlewares/validation.middleware';
import * as authMiddleware from '../middlewares/auth.middleware';
import * as rateLimitMiddleware from '../middlewares/rate-limit.middleware';
import Joi from 'joi';

/**
 * 诊断路由模块
 */
const router = express.Router();
const diagnosisController = new DiagnosisController();

/**
 * 诊断请求验证模式
 */
const diagnosisRequestSchema = Joi.object({
  sessionId: Joi.string().required(),
  userId: Joi.string().required(),
  symptoms: Joi.array().items(Joi.object({
    name: Joi.string().required(),
    severity: Joi.number().min(1).max(10).optional(),
    duration: Joi.string().optional(),
    characteristics: Joi.array().items(Joi.string()).optional(),
    confidence: Joi.number().min(0).max(1).optional()
  })).min(1).required(),
  patientInfo: Joi.object({
    age: Joi.number().optional(),
    gender: Joi.string().optional(),
    medicalHistory: Joi.array().items(Joi.string()).optional()
  }).optional(),
  preferences: Joi.object().optional()
});

/**
 * @api {post} /api/diagnosis 生成诊断
 * @apiName GenerateDiagnosis
 * @apiGroup Diagnosis
 * @apiDescription 基于问诊会话和症状生成诊断结果
 * 
 * @apiBody {String} sessionId 会话ID
 * @apiBody {String} userId 用户ID
 * @apiBody {Array} symptoms 症状数组
 * @apiBody {Object} [patientInfo] 患者信息
 * @apiBody {Object} [preferences] 偏好设置
 * 
 * @apiSuccess {Object} diagnosis 诊断结果
 * @apiSuccess {Boolean} success 成功标志
 * @apiSuccess {Number} processingTime 处理时间(毫秒)
 */
router.post(
  '/',
  authMiddleware.authenticate,
  rateLimitMiddleware.applyRateLimit(10, 60), // 每分钟限制10次请求
  validationMiddleware.validateBody(diagnosisRequestSchema),
  (req, res, next) => diagnosisController.generateDiagnosis(req, res, next)
);

/**
 * @api {get} /api/diagnosis/:diagnosisId 通过ID获取诊断结果
 * @apiName GetDiagnosisById
 * @apiGroup Diagnosis
 * @apiDescription 通过诊断ID获取特定的诊断结果
 * 
 * @apiParam {String} diagnosisId 诊断ID
 * 
 * @apiSuccess {Object} diagnosis 诊断结果详情
 */
router.get(
  '/:diagnosisId',
  authMiddleware.authenticate,
  (req, res, next) => diagnosisController.getDiagnosisById(req, res, next)
);

/**
 * @api {get} /api/diagnosis/session/:sessionId 通过会话ID获取诊断结果
 * @apiName GetDiagnosisBySessionId
 * @apiGroup Diagnosis
 * @apiDescription 通过会话ID获取关联的诊断结果
 * 
 * @apiParam {String} sessionId 会话ID
 * 
 * @apiSuccess {Object} diagnosis 诊断结果详情
 */
router.get(
  '/session/:sessionId',
  authMiddleware.authenticate,
  (req, res, next) => diagnosisController.getDiagnosisBySessionId(req, res, next)
);

/**
 * @api {get} /api/diagnosis/user/:userId 获取用户诊断历史
 * @apiName GetUserDiagnosisHistory
 * @apiGroup Diagnosis
 * @apiDescription 获取特定用户的诊断历史记录
 * 
 * @apiParam {String} userId 用户ID
 * @apiQuery {Number} [limit=10] 结果限制数量
 * @apiQuery {Number} [offset=0] 结果偏移量
 * 
 * @apiSuccess {Array} diagnoses 诊断结果数组
 * @apiSuccess {Object} pagination 分页信息
 */
router.get(
  '/user/:userId',
  authMiddleware.authenticate,
  (req, res, next) => diagnosisController.getUserDiagnosisHistory(req, res, next)
);

export default router;