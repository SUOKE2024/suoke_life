/**
 * 问诊服务相关的请求验证模式
 */

import Joi from 'joi';

/**
 * 创建问诊会话验证模式
 */
export const createInquirySessionSchema = Joi.object({
  userId: Joi.string().required().trim().min(3).max(100)
    .message({
      'string.empty': 'userId不能为空',
      'string.min': 'userId至少需要3个字符',
      'string.max': 'userId不能超过100个字符',
      'any.required': '缺少必要参数userId'
    }),
  patientInfo: Joi.object({
    name: Joi.string().min(1).max(50).optional(),
    age: Joi.number().integer().min(0).max(120).optional(),
    gender: Joi.string().valid('male', 'female', 'other').optional(),
    height: Joi.number().min(30).max(250).optional(),
    weight: Joi.number().min(1).max(300).optional(),
    medicalHistory: Joi.array().items(Joi.string()).optional(),
    allergies: Joi.array().items(Joi.string()).optional(),
    medications: Joi.array().items(Joi.string()).optional()
  }).default({}),
  preferences: Joi.object({
    language: Joi.string().valid('zh-CN', 'en-US').default('zh-CN'),
    responseStyle: Joi.string().valid('detailed', 'concise').default('detailed'),
    tcmFocus: Joi.boolean().default(true),
    includeMedicalTerms: Joi.boolean().default(true),
    includeReferences: Joi.boolean().default(false)
  }).default({}),
  metadata: Joi.object().default({})
});

/**
 * 处理问诊请求验证模式
 */
export const processInquirySchema = Joi.object({
  content: Joi.string().required().min(2).max(2000)
    .message({
      'string.empty': '问诊内容不能为空',
      'string.min': '问诊内容至少需要2个字符',
      'string.max': '问诊内容不能超过2000个字符',
      'any.required': '缺少必要的问诊内容'
    }),
  attachments: Joi.array().items(
    Joi.object({
      type: Joi.string().valid('image', 'document', 'audio').required(),
      url: Joi.string().uri().required(),
      description: Joi.string().optional()
    })
  ).optional(),
  metadata: Joi.object({
    source: Joi.string().valid('app', 'web', 'kiosk').default('app'),
    location: Joi.string().optional(),
    device: Joi.string().optional(),
    priority: Joi.string().valid('normal', 'urgent').default('normal')
  }).default({})
});

/**
 * 更新会话偏好验证模式
 */
export const updatePreferencesSchema = Joi.object({
  preferences: Joi.object({
    language: Joi.string().valid('zh-CN', 'en-US'),
    responseStyle: Joi.string().valid('detailed', 'concise'),
    tcmFocus: Joi.boolean(),
    includeMedicalTerms: Joi.boolean(),
    includeReferences: Joi.boolean()
  }).required()
    .message({
      'any.required': '缺少必要的preferences参数'
    })
});

/**
 * 结束问诊会话验证模式
 */
export const endSessionSchema = Joi.object({
  reason: Joi.string().valid(
    'completed', 
    'user_requested', 
    'system_timeout', 
    'transferred', 
    'other'
  ).default('completed'),
  feedback: Joi.object({
    rating: Joi.number().integer().min(1).max(5).optional(),
    comments: Joi.string().max(500).optional()
  }).optional(),
  metadata: Joi.object().default({})
});

/**
 * 获取用户会话历史验证模式
 */
export const getUserSessionsSchema = Joi.object({
  limit: Joi.number().integer().min(1).max(100).default(10),
  offset: Joi.number().integer().min(0).default(0),
  status: Joi.string().valid('active', 'completed', 'abandoned', 'all').default('all'),
  startDate: Joi.date().iso().optional(),
  endDate: Joi.date().iso().optional()
    .when('startDate', {
      is: Joi.exist(),
      then: Joi.date().greater(Joi.ref('startDate'))
        .message('endDate必须晚于startDate')
    })
});