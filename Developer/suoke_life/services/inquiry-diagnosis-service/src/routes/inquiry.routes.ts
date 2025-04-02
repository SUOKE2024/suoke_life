import { Router } from 'express';
import { Container } from 'typedi';
import { InquiryController } from '../controllers/inquiry.controller';

/**
 * 创建问诊路由
 * @returns Express路由器
 */
export function createInquiryRoutes(): Router {
  const router = Router();
  const inquiryController = Container.get(InquiryController);
  
  /**
   * @api {post} /sessions 创建新的问诊会话
   * @apiName CreateSession
   * @apiGroup Inquiry
   * @apiDescription 创建新的问诊会话
   * 
   * @apiParam {String} userId 用户ID
   * @apiParam {Object} [patientInfo] 患者信息
   * @apiParam {String} [patientInfo.name] 患者姓名
   * @apiParam {Number} [patientInfo.age] 患者年龄
   * @apiParam {String} [patientInfo.gender] 患者性别 (男/女/其他)
   * @apiParam {Number} [patientInfo.height] 身高(cm)
   * @apiParam {Number} [patientInfo.weight] 体重(kg)
   * @apiParam {String[]} [patientInfo.medicalHistory] 病史记录
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {Object} data 会话数据
   */
  router.post('/sessions', inquiryController.createSession.bind(inquiryController));
  
  /**
   * @api {put} /sessions/:id/preferences 更新会话首选项
   * @apiName UpdateSessionPreferences
   * @apiGroup Inquiry
   * @apiDescription 更新问诊会话的首选项设置
   * 
   * @apiParam {String} id 会话ID
   * @apiParam {String} [language] 语言 (zh_CN/en_US)
   * @apiParam {String} [detailLevel] 详细程度 (simple/normal/detailed)
   * @apiParam {String[]} [focusAreas] 关注领域
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {Object} data 更新后的会话数据
   */
  router.put('/sessions/:id/preferences', inquiryController.updateSessionPreferences.bind(inquiryController));
  
  /**
   * @api {post} /process 处理问诊请求
   * @apiName ProcessInquiry
   * @apiGroup Inquiry
   * @apiDescription 处理用户的问诊请求，提取症状并生成回答
   * 
   * @apiParam {String} sessionId 会话ID
   * @apiParam {String} userId 用户ID
   * @apiParam {String} question 用户提问
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {Object} data 问诊响应数据
   * @apiSuccess {String} data.answer 生成的回答
   * @apiSuccess {Object[]} data.extractedSymptoms 提取的症状
   * @apiSuccess {Boolean} data.shouldGenerateDiagnosis 是否应生成诊断
   */
  router.post('/process', inquiryController.processInquiry.bind(inquiryController));
  
  /**
   * @api {get} /sessions/:sessionId/diagnosis 获取诊断结果
   * @apiName GetDiagnosis
   * @apiGroup Inquiry
   * @apiDescription 获取问诊会话的诊断结果
   * 
   * @apiParam {String} sessionId 会话ID
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {Object} data 诊断结果数据
   */
  router.get('/sessions/:sessionId/diagnosis', inquiryController.getDiagnosis.bind(inquiryController));
  
  /**
   * @api {post} /sessions/:sessionId/end 结束问诊会话
   * @apiName EndSession
   * @apiGroup Inquiry
   * @apiDescription 结束问诊会话，生成最终诊断结果
   * 
   * @apiParam {String} sessionId 会话ID
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {Object} data 结束后的会话数据
   */
  router.post('/sessions/:sessionId/end', inquiryController.endSession.bind(inquiryController));
  
  return router;
}