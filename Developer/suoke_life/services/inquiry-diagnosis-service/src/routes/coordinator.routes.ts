import { Router } from 'express';
import { Container } from 'typedi';
import { CoordinatorWebhookController } from '../controllers/coordinator-webhook.controller';

/**
 * 创建四诊协调服务webhook路由
 * @returns Express路由器
 */
export function createCoordinatorRoutes(): Router {
  const router = Router();
  const coordinatorWebhookController = Container.get(CoordinatorWebhookController);
  
  /**
   * @api {post} /webhook 处理四诊协调服务请求
   * @apiName HandleCoordinatorRequest
   * @apiGroup Coordinator
   * @apiDescription 处理来自四诊协调服务的请求
   * 
   * @apiHeader {String} x-api-key API密钥
   * 
   * @apiParam {String} sessionId 会话ID
   * @apiParam {String} [userId] 用户ID
   * @apiParam {String} requestType 请求类型
   * @apiParam {String} [diagnosisId] 诊断ID (用于GET_DIAGNOSIS_RESULT请求)
   * @apiParam {Number} [limit] 返回数量限制 (用于分页请求)
   * @apiParam {Number} [offset] 结果偏移量 (用于分页请求)
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {Object} data 响应数据
   * 
   * @apiError {Boolean} success 始终为false
   * @apiError {String} message 错误信息
   * @apiError {String} error 错误代码
   */
  router.post(
    '/webhook',
    coordinatorWebhookController.validateCoordinatorRequest.bind(coordinatorWebhookController),
    coordinatorWebhookController.handleCoordinatorRequest.bind(coordinatorWebhookController)
  );
  
  return router;
} 