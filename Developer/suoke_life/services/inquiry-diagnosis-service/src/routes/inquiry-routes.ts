import { Router } from 'express';
import { Container } from 'typedi';
import { InquiryController } from '../controllers/inquiry.controller';
import { validationMiddleware, authMiddleware } from '../middlewares';
import { 
  SessionCreateSchema, 
  SessionPreferencesUpdateSchema, 
  InquiryRequestSchema 
} from '../utils/validators';

const router = Router();
const inquiryController = Container.get(InquiryController);

/**
 * @route   POST /api/inquiry/sessions
 * @desc    创建问诊会话
 * @access  需要认证
 */
router.post(
  '/sessions',
  [authMiddleware, validationMiddleware(SessionCreateSchema)],
  inquiryController.createSession
);

/**
 * @route   PUT /api/inquiry/sessions/:id/preferences
 * @desc    更新会话偏好设置
 * @access  需要认证
 */
router.put(
  '/sessions/:id/preferences',
  [authMiddleware, validationMiddleware(SessionPreferencesUpdateSchema)],
  inquiryController.updateSessionPreferences
);

/**
 * @route   POST /api/inquiry/process
 * @desc    处理问诊请求
 * @access  需要认证
 */
router.post(
  '/process',
  [authMiddleware, validationMiddleware(InquiryRequestSchema)],
  inquiryController.processInquiry
);

/**
 * @route   GET /api/inquiry/sessions/:sessionId/symptoms
 * @desc    获取会话中已提取的症状
 * @access  需要认证
 */
router.get(
  '/sessions/:sessionId/symptoms',
  authMiddleware,
  inquiryController.getExtractedSymptoms
);

/**
 * @route   POST /api/inquiry/sessions/:sessionId/end
 * @desc    结束问诊会话
 * @access  需要认证
 */
router.post(
  '/sessions/:sessionId/end',
  authMiddleware,
  inquiryController.endSession
);

/**
 * @route   GET /api/inquiry/health-records/:userId
 * @desc    获取用户健康记录
 * @access  需要认证
 */
router.get(
  '/health-records/:userId',
  authMiddleware,
  inquiryController.getUserHealthRecords
);

/**
 * @route   POST /api/inquiry/health-records
 * @desc    创建健康记录
 * @access  需要认证
 */
router.post(
  '/health-records',
  authMiddleware,
  inquiryController.createHealthRecord
);

export default router;