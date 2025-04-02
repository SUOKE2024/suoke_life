import { Router } from 'express';
import { TongueDiagnosisController } from '../controllers/tongue-diagnosis.controller';
import { FaceAnalysisController } from '../controllers/face-analysis.controller';
import { CoordinatorWebhookController } from '../controllers/coordinator-webhook.controller';
import { PostureAnalysisController } from '../controllers/posture-analysis.controller';

const router = Router();
const tongueDiagnosisController = new TongueDiagnosisController();
const faceAnalysisController = new FaceAnalysisController();
const coordinatorWebhookController = new CoordinatorWebhookController();
const postureAnalysisController = new PostureAnalysisController();

/**
 * @swagger
 * /api/looking-diagnosis/health:
 *   get:
 *     summary: 健康检查端点
 *     description: 用于确认服务是否正常运行
 *     tags:
 *       - Health
 *     responses:
 *       200:
 *         description: 服务正常运行
 */
router.get('/health', tongueDiagnosisController.healthCheck.bind(tongueDiagnosisController));

/**
 * @swagger
 * /api/looking-diagnosis/tongue:
 *   post:
 *     summary: 舌诊分析
 *     description: 分析舌象照片并生成中医诊断结果
 *     tags:
 *       - Tongue Diagnosis
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - imageBase64
 *               - sessionId
 *             properties:
 *               imageBase64:
 *                 type: string
 *                 description: Base64编码的舌头图像
 *               sessionId:
 *                 type: string
 *                 description: 诊断会话ID
 *               metadata:
 *                 type: object
 *                 description: 元数据信息
 *                 properties:
 *                   captureTime:
 *                     type: string
 *                     format: date-time
 *                   lightingCondition:
 *                     type: string
 *     responses:
 *       200:
 *         description: 舌诊分析成功
 *       400:
 *         description: 请求参数错误
 *       500:
 *         description: 服务器错误
 */
router.post('/tongue', tongueDiagnosisController.analyzeTongue.bind(tongueDiagnosisController));

/**
 * @swagger
 * /api/looking-diagnosis/tongue/history:
 *   get:
 *     summary: 获取舌诊历史记录
 *     description: 获取用户或会话的舌诊历史记录
 *     tags:
 *       - Tongue Diagnosis
 *     parameters:
 *       - in: query
 *         name: userId
 *         schema:
 *           type: string
 *         description: 用户ID
 *       - in: query
 *         name: sessionId
 *         schema:
 *           type: string
 *         description: 会话ID
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: 返回记录数限制
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *         description: 分页偏移量
 *     responses:
 *       200:
 *         description: 成功获取历史记录
 *       400:
 *         description: 请求参数错误
 *       500:
 *         description: 服务器错误
 */
router.get('/tongue/history', tongueDiagnosisController.getTongueDiagnosisHistory.bind(tongueDiagnosisController));

/**
 * @swagger
 * /api/looking-diagnosis/tongue/{diagnosisId}:
 *   get:
 *     summary: 获取特定舌诊记录
 *     description: 根据诊断ID获取特定的舌诊记录
 *     tags:
 *       - Tongue Diagnosis
 *     parameters:
 *       - in: path
 *         name: diagnosisId
 *         required: true
 *         schema:
 *           type: string
 *         description: 舌诊记录ID
 *     responses:
 *       200:
 *         description: 成功获取舌诊记录
 *       404:
 *         description: 未找到舌诊记录
 *       500:
 *         description: 服务器错误
 */
router.get('/tongue/:diagnosisId', tongueDiagnosisController.getTongueDiagnosisById.bind(tongueDiagnosisController));

/**
 * @swagger
 * /api/looking-diagnosis/face:
 *   post:
 *     summary: 面诊分析
 *     description: 分析面色照片并生成中医诊断结果
 *     tags:
 *       - Face Diagnosis
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - imageBase64
 *               - sessionId
 *             properties:
 *               imageBase64:
 *                 type: string
 *                 description: Base64编码的面部图像
 *               sessionId:
 *                 type: string
 *                 description: 诊断会话ID
 *               metadata:
 *                 type: object
 *                 description: 元数据信息
 *                 properties:
 *                   captureTime:
 *                     type: string
 *                     format: date-time
 *                   lightingCondition:
 *                     type: string
 *     responses:
 *       200:
 *         description: 面诊分析成功
 *       400:
 *         description: 请求参数错误
 *       500:
 *         description: 服务器错误
 */
router.post('/face', faceAnalysisController.analyzeFace.bind(faceAnalysisController));

/**
 * @swagger
 * /api/looking-diagnosis/face/history:
 *   get:
 *     summary: 获取面诊历史记录
 *     description: 获取用户或会话的面诊历史记录
 *     tags:
 *       - Face Diagnosis
 *     parameters:
 *       - in: query
 *         name: userId
 *         schema:
 *           type: string
 *         description: 用户ID
 *       - in: query
 *         name: sessionId
 *         schema:
 *           type: string
 *         description: 会话ID
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: 返回记录数限制
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *         description: 分页偏移量
 *     responses:
 *       200:
 *         description: 成功获取历史记录
 *       400:
 *         description: 请求参数错误
 *       500:
 *         description: 服务器错误
 */
router.get('/face/history', faceAnalysisController.getFaceDiagnosisHistory.bind(faceAnalysisController));

/**
 * @swagger
 * /api/looking-diagnosis/face/{diagnosisId}:
 *   get:
 *     summary: 获取特定面诊记录
 *     description: 根据诊断ID获取特定的面诊记录
 *     tags:
 *       - Face Diagnosis
 *     parameters:
 *       - in: path
 *         name: diagnosisId
 *         required: true
 *         schema:
 *           type: string
 *         description: 面诊记录ID
 *     responses:
 *       200:
 *         description: 成功获取面诊记录
 *       404:
 *         description: 未找到面诊记录
 *       500:
 *         description: 服务器错误
 */
router.get('/face/:diagnosisId', faceAnalysisController.getFaceDiagnosisById.bind(faceAnalysisController));

/**
 * @swagger
 * /api/looking-diagnosis/posture:
 *   post:
 *     summary: 体态分析
 *     description: 分析体态照片并生成中医诊断结果
 *     tags:
 *       - Posture Analysis
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - imageBase64
 *               - sessionId
 *             properties:
 *               imageBase64:
 *                 type: string
 *                 description: Base64编码的体态图像
 *               sessionId:
 *                 type: string
 *                 description: 诊断会话ID
 *               userId:
 *                 type: string
 *                 description: 用户ID（可选）
 *               metadata:
 *                 type: object
 *                 description: 元数据信息
 *                 properties:
 *                   captureTime:
 *                     type: string
 *                     format: date-time
 *                   lightingCondition:
 *                     type: string
 *     responses:
 *       200:
 *         description: 体态分析成功
 *       400:
 *         description: 请求参数错误
 *       500:
 *         description: 服务器错误
 */
router.post('/posture', 
  PostureAnalysisController.postureAnalysisValidation,
  postureAnalysisController.analyzePosture.bind(postureAnalysisController)
);

/**
 * @swagger
 * /api/looking-diagnosis/posture/history:
 *   get:
 *     summary: 获取体态分析历史记录
 *     description: 获取用户或会话的体态分析历史记录
 *     tags:
 *       - Posture Analysis
 *     parameters:
 *       - in: query
 *         name: userId
 *         schema:
 *           type: string
 *         description: 用户ID
 *       - in: query
 *         name: sessionId
 *         schema:
 *           type: string
 *         description: 会话ID
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: 返回记录数限制
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *         description: 分页偏移量
 *     responses:
 *       200:
 *         description: 成功获取历史记录
 *       400:
 *         description: 请求参数错误
 *       500:
 *         description: 服务器错误
 */
router.get('/posture/history',
  PostureAnalysisController.historyValidation,
  postureAnalysisController.getPostureDiagnosisHistory.bind(postureAnalysisController)
);

/**
 * @swagger
 * /api/looking-diagnosis/posture/{diagnosisId}:
 *   get:
 *     summary: 获取特定体态分析记录
 *     description: 根据诊断ID获取特定的体态分析记录
 *     tags:
 *       - Posture Analysis
 *     parameters:
 *       - in: path
 *         name: diagnosisId
 *         required: true
 *         schema:
 *           type: string
 *         description: 体态分析记录ID
 *     responses:
 *       200:
 *         description: 成功获取体态分析记录
 *       404:
 *         description: 未找到体态分析记录
 *       500:
 *         description: 服务器错误
 */
router.get('/posture/:diagnosisId',
  PostureAnalysisController.diagnosisIdValidation,
  postureAnalysisController.getPostureDiagnosisById.bind(postureAnalysisController)
);

/**
 * @swagger
 * /api/looking-diagnosis/webhook/coordinator:
 *   post:
 *     summary: 四诊协调服务webhook
 *     description: 接收来自四诊协调服务的请求
 *     tags:
 *       - Webhook
 *     security:
 *       - ApiKey: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - sessionId
 *               - requestType
 *             properties:
 *               sessionId:
 *                 type: string
 *                 description: 会话ID
 *               userId:
 *                 type: string
 *                 description: 用户ID
 *               requestType:
 *                 type: string
 *                 enum: [GET_TONGUE_DIAGNOSIS, GET_TONGUE_HISTORY]
 *                 description: 请求类型
 *               limit:
 *                 type: integer
 *                 description: 记录数限制(仅GET_TONGUE_HISTORY)
 *               offset:
 *                 type: integer
 *                 description: 分页偏移量(仅GET_TONGUE_HISTORY)
 *     responses:
 *       200:
 *         description: 请求处理成功
 *       400:
 *         description: 请求参数错误
 *       401:
 *         description: 未授权的请求
 *       500:
 *         description: 服务器错误
 */
router.post(
  '/webhook/coordinator',
  coordinatorWebhookController.validateCoordinatorRequest.bind(coordinatorWebhookController),
  coordinatorWebhookController.handleDiagnosisRequest.bind(coordinatorWebhookController)
);

export default router;