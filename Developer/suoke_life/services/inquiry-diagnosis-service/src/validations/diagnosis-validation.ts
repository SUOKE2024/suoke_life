/**
 * 诊断服务相关的请求验证模式
 */

import Joi from 'joi';

/**
 * 创建诊断验证模式
 */
export const createDiagnosisSchema = Joi.object({
  sessionId: Joi.string().required()
    .message({
      'string.empty': 'sessionId不能为空',
      'any.required': '缺少必要参数sessionId'
    }),
  userId: Joi.string().required()
    .message({
      'string.empty': 'userId不能为空',
      'any.required': '缺少必要参数userId'
    }),
  includeRecommendations: Joi.boolean().default(true),
  deepAnalysis: Joi.boolean().default(false),
  preferredCategories: Joi.array().items(
    Joi.string().valid(
      'diet', 'lifestyle', 'exercise', 'herbs', 
      'acupuncture', 'general', 'all'
    )
  ).default(['all']),
  metadata: Joi.object({
    source: Joi.string().valid('app', 'web', 'kiosk', 'api').default('app'),
    priority: Joi.string().valid('normal', 'high').default('normal'),
    requestId: Joi.string().optional()
  }).default({})
});

/**
 * 获取诊断结果验证模式
 */
export const getDiagnosisSchema = Joi.object({
  includeTCMDetails: Joi.boolean().default(false),
  includeSymptomDetails: Joi.boolean().default(false),
  includeHistory: Joi.boolean().default(false)
});

/**
 * 获取用户诊断历史验证模式
 */
export const getDiagnosisHistorySchema = Joi.object({
  limit: Joi.number().integer().min(1).max(100).default(10),
  offset: Joi.number().integer().min(0).default(0),
  startDate: Joi.date().iso().optional(),
  endDate: Joi.date().iso().optional()
    .when('startDate', {
      is: Joi.exist(),
      then: Joi.date().greater(Joi.ref('startDate'))
        .message('endDate必须晚于startDate')
    }),
  sortBy: Joi.string().valid('createdAt', 'updatedAt').default('createdAt'),
  sortOrder: Joi.string().valid('asc', 'desc').default('desc')
});

/**
 * 导出诊断结果验证模式
 */
export const exportDiagnosisSchema = Joi.object({
  format: Joi.string().valid('pdf', 'json', 'csv').default('pdf'),
  includePersonalInfo: Joi.boolean().default(true),
  includeSessionHistory: Joi.boolean().default(false),
  language: Joi.string().valid('zh-CN', 'en-US').default('zh-CN'),
  contentOptions: Joi.object({
    includeTCMDetails: Joi.boolean().default(true),
    includeRecommendations: Joi.boolean().default(true),
    includeWarnings: Joi.boolean().default(true),
    includeSymptomDetails: Joi.boolean().default(false),
    includeFollowUpQuestions: Joi.boolean().default(false)
  }).default({})
});

/**
 * 获取会话的综合四诊结果验证模式
 */
export const getIntegratedDiagnosisSchema = Joi.object({
  detailLevel: Joi.string()
    .valid('minimal', 'standard', 'detailed', 'comprehensive')
    .default('standard'),
  requestTimestamp: Joi.date().iso().optional(),
  includeRawData: Joi.boolean().default(false)
});

/**
 * 添加外部诊断结果验证模式
 */
export const addExternalDiagnosisSchema = Joi.object({
  source: Joi.string().required()
    .message({
      'string.empty': 'source不能为空',
      'any.required': '缺少必要参数source'
    }),
  diagnosisType: Joi.string()
    .valid('face', 'tongue', 'pulse', 'external', 'western', 'other')
    .required()
    .message({
      'string.empty': 'diagnosisType不能为空',
      'any.required': '缺少必要参数diagnosisType'
    }),
  diagnosisData: Joi.object().required()
    .message({
      'any.required': '缺少必要参数diagnosisData'
    }),
  timestamp: Joi.date().iso().default(new Date().toISOString()),
  metadata: Joi.object().default({})
});

/**
 * 通过会话ID获取诊断结果验证模式
 */
export const getDiagnosisBySessionIdSchema = Joi.object({
  sessionId: Joi.string().required().messages({
    'any.required': '会话ID不能为空',
    'string.empty': '会话ID不能为空'
  })
});

/**
 * 反馈验证模式
 */
export const diagnosisFeedbackSchema = Joi.object({
  diagnosisId: Joi.string().required().messages({
    'any.required': '诊断ID不能为空',
    'string.empty': '诊断ID不能为空'
  }),
  userId: Joi.string().required().messages({
    'any.required': '用户ID不能为空',
    'string.empty': '用户ID不能为空'
  }),
  rating: Joi.number().integer().min(1).max(5).required().messages({
    'any.required': '评分不能为空',
    'number.min': '评分不能小于1',
    'number.max': '评分不能大于5'
  }),
  comment: Joi.string().optional(),
  categories: Joi.array().items(Joi.string().valid(
    'accuracy',
    'helpfulness',
    'clarity',
    'completeness',
    'relevance',
    'other'
  )).optional()
});