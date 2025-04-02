import Joi from 'joi';

/**
 * 四诊协调请求验证模式
 */
export const coordinatorRequestSchema = Joi.object({
  userId: Joi.string().required()
    .message({
      'string.empty': 'userId不能为空',
      'any.required': '缺少必要参数userId'
    }),
  sessionId: Joi.string().required()
    .message({
      'string.empty': 'sessionId不能为空',
      'any.required': '缺少必要参数sessionId'
    }),
  diagnosisTypes: Joi.array()
    .items(Joi.string().valid('face', 'tongue', 'pulse', 'inquiry'))
    .min(1)
    .required()
    .message({
      'array.min': '至少需要一种诊断类型',
      'any.required': '缺少必要参数diagnosisTypes'
    }),
  options: Joi.object({
    useLatestOnly: Joi.boolean().default(true),
    combineWithHistory: Joi.boolean().default(false),
    maxHistoryRecords: Joi.number().integer().min(0).max(10).default(0),
    confidenceThreshold: Joi.number().min(0).max(1).default(0.6)
  }).default({}),
  metadata: Joi.object().default({})
});

/**
 * 四诊数据协调结果验证模式
 */
export const coordinationResultSchema = Joi.object({
  constitutionTypes: Joi.array()
    .items(Joi.object({
      type: Joi.string().required(),
      confidence: Joi.number().min(0).max(1).required(),
      evidence: Joi.array().items(Joi.string()).optional()
    }))
    .min(1)
    .required(),
  patterns: Joi.array()
    .items(Joi.object({
      name: Joi.string().required(),
      confidence: Joi.number().min(0).max(1).required(),
      related: Joi.array().items(Joi.string()).optional()
    }))
    .min(0)
    .default([]),
  organSystems: Joi.array()
    .items(Joi.object({
      name: Joi.string().required(),
      status: Joi.string().valid('deficient', 'excess', 'balanced', 'heat', 'cold', 'mixed').required(),
      confidence: Joi.number().min(0).max(1).required()
    }))
    .min(0)
    .default([]),
  symptoms: Joi.array()
    .items(Joi.object({
      name: Joi.string().required(),
      source: Joi.string().required(),
      intensity: Joi.number().min(0).max(10).optional(),
      duration: Joi.string().optional()
    }))
    .default([]),
  confidence: Joi.number().min(0).max(1).required(),
  timestamp: Joi.date().iso().required()
});

/**
 * 体质评估请求验证模式
 */
export const constitutionAssessmentSchema = Joi.object({
  userId: Joi.string().required()
    .message({
      'string.empty': 'userId不能为空',
      'any.required': '缺少必要参数userId'
    }),
  assessmentData: Joi.object({
    questionnaireResponses: Joi.array().items(
      Joi.object({
        questionId: Joi.string().required(),
        response: Joi.alternatives().try(
          Joi.number(),
          Joi.string(),
          Joi.boolean()
        ).required()
      })
    ).optional(),
    tongueData: Joi.object().optional(),
    faceData: Joi.object().optional(),
    pulseData: Joi.object().optional(),
    inquiryData: Joi.object().optional()
  }).required()
    .message({
      'any.required': '缺少必要参数assessmentData'
    }),
  options: Joi.object({
    comprehensive: Joi.boolean().default(true),
    includeRecommendations: Joi.boolean().default(true)
  }).default({}),
  metadata: Joi.object().default({})
});