import { Router } from 'express';
import { Container } from 'typedi';
import { DiagnosisController } from '../controllers/diagnosis.controller';

/**
 * 创建诊断路由
 * @returns Express路由器
 */
export function createDiagnosisRoutes(): Router {
  const router = Router();
  const diagnosisController = Container.get(DiagnosisController);
  
  /**
   * @api {post} /generate 生成诊断结果
   * @apiName GenerateDiagnosis
   * @apiGroup Diagnosis
   * @apiDescription 根据症状和患者信息生成中医诊断结果
   * 
   * @apiParam {String} sessionId 会话ID
   * @apiParam {String} userId 用户ID
   * @apiParam {Object} [patientInfo] 患者信息
   * @apiParam {Number} [patientInfo.age] 患者年龄
   * @apiParam {String} [patientInfo.gender] 患者性别 (男/女/其他)
   * @apiParam {Number} [patientInfo.height] 身高(cm)
   * @apiParam {Number} [patientInfo.weight] 体重(kg)
   * @apiParam {Array} [patientInfo.medicalHistory] 病史记录
   * @apiParam {Array} symptoms 症状列表
   * @apiParam {String} symptoms.name 症状名称
   * @apiParam {String} [symptoms.location] 症状位置
   * @apiParam {Number} [symptoms.severity].severity 症状严重度 (1-10)
   * @apiParam {String} [symptoms.duration] 症状持续时间
   * @apiParam {String} [symptoms.frequency] 症状频率
   * @apiParam {Array} [symptoms.characteristics] 症状特征
   * @apiParam {Array} [symptoms.aggravatingFactors] 加重因素
   * @apiParam {Array} [symptoms.relievingFactors] 缓解因素
   * @apiParam {Array} [symptoms.associatedSymptoms] 相关症状
   * @apiParam {Number} [symptoms.confidence] 置信度 (0-1)
   * @apiParam {Object} [preferences] 偏好设置
   * @apiParam {Boolean} [preferences.useTCMTerminology] 是否使用中医术语
   * @apiParam {String} [preferences.detailLevel] 详细程度 (basic/detailed/expert)
   * @apiParam {Array} [preferences.focusAreas] 关注领域
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {String} message 成功消息
   * @apiSuccess {Object} data 诊断响应数据
   */
  router.post('/generate', diagnosisController.generateDiagnosis.bind(diagnosisController));
  
  /**
   * @api {get} /:diagnosisId 获取诊断结果
   * @apiName GetDiagnosisById
   * @apiGroup Diagnosis
   * @apiDescription 根据诊断ID获取诊断结果
   * 
   * @apiParam {String} diagnosisId 诊断ID
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {String} message 成功消息
   * @apiSuccess {Object} data 诊断结果数据
   */
  router.get('/:diagnosisId', diagnosisController.getDiagnosisById.bind(diagnosisController));
  
  /**
   * @api {get} /user/:userId/history 获取用户诊断历史
   * @apiName GetUserDiagnosisHistory
   * @apiGroup Diagnosis
   * @apiDescription 获取指定用户的诊断历史记录
   * 
   * @apiParam {String} userId 用户ID
   * @apiParam {Number} [limit=10] 结果数量限制
   * @apiParam {Number} [offset=0] 结果偏移量
   * 
   * @apiSuccess {Boolean} success 是否成功
   * @apiSuccess {String} message 成功消息
   * @apiSuccess {Array} data 诊断历史记录
   */
  router.get('/user/:userId/history', diagnosisController.getUserDiagnosisHistory.bind(diagnosisController));
  
  return router;
}