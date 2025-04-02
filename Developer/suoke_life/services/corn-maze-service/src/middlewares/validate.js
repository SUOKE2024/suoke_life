/**
 * 验证中间件
 * 提供统一的请求参数验证
 */
const Joi = require('joi');
const { createError } = require('./errorHandler');
const logger = require('../utils/logger');

// 验证模式定义
const schemas = {
  // 坐标验证
  coordinates: Joi.object({
    latitude: Joi.number().required().min(-90).max(90)
      .error(new Error('纬度必须是有效数值，范围-90到90')),
    longitude: Joi.number().required().min(-180).max(180)
      .error(new Error('经度必须是有效数值，范围-180到180')),
    accuracy: Joi.number().min(0).max(1000)
      .error(new Error('精度必须是有效数值，范围0到1000米'))
  }),

  // AR消息验证
  arMessage: Joi.object({
    content: Joi.string().required().min(1).max(500)
      .error(new Error('消息内容必须在1-500字符之间')),
    location: Joi.object({
      latitude: Joi.number().required().min(-90).max(90),
      longitude: Joi.number().required().min(-180).max(180),
      altitude: Joi.number(),
      accuracy: Joi.number().min(0)
    }).required()
      .error(new Error('位置信息无效或不完整')),
    expiresAt: Joi.date()
      .error(new Error('过期时间必须是有效日期')),
    attachments: Joi.array().items(Joi.string())
      .error(new Error('附件必须是字符串数组')),
    isPublic: Joi.boolean().default(true)
      .error(new Error('isPublic必须是布尔值'))
  }),

  // AR扫描结果验证
  arScanResult: Joi.object({
    data: Joi.object({
      recognizedObjects: Joi.array().items(Joi.object({
        type: Joi.string().required(),
        confidence: Joi.number().min(0).max(1).required(),
        boundingBox: Joi.object()
      })).required(),
      capturedAt: Joi.date().required(),
      deviceInfo: Joi.object(),
      location: Joi.object({
        latitude: Joi.number().min(-90).max(90),
        longitude: Joi.number().min(-180).max(180)
      })
    }).required()
  }),

  // 手势收集验证
  gestureCollection: Joi.object({
    gestureData: Joi.object({
      gestureType: Joi.string().required().valid(
        'tap', 'swipe', 'pinch', 'rotate', 'wave', 'grab'
      ),
      duration: Joi.number().min(0),
      intensity: Joi.number().min(0).max(1),
      points: Joi.array().items(Joi.object())
    }).required()
  }),

  // 团队寻宝验证
  teamHunt: Joi.object({
    startPosition: Joi.object({
      x: Joi.number().required(),
      y: Joi.number().required()
    }),
    deviceInfo: Joi.object(),
    sessionSettings: Joi.object()
  }),

  // 宝藏分享验证
  shareTreasure: Joi.object({
    receiverId: Joi.string().required()
      .error(new Error('接收者ID必须提供')),
    message: Joi.string().max(200)
      .error(new Error('消息不能超过200字符'))
  }),

  // NPC交互验证
  npcInteraction: Joi.object({
    message: Joi.string().required().min(1).max(1000)
      .error(new Error('消息内容必须在1-1000字符之间')),
    npcId: Joi.string()
      .error(new Error('NPC ID无效')),
    location: Joi.object({
      latitude: Joi.number().min(-90).max(90),
      longitude: Joi.number().min(-180).max(180)
    }),
    context: Joi.object(),
    sessionId: Joi.string()
  }),

  // 环境扫描验证
  environmentScan: Joi.object({
    scanData: Joi.object({
      pointCloud: Joi.array(),
      imageData: Joi.string(),
      depthMap: Joi.array(),
      scanType: Joi.string().valid(
        'quick', 'detailed', 'room', 'outdoor'
      ),
      scanDuration: Joi.number()
    }).required(),
    location: Joi.object({
      latitude: Joi.number().min(-90).max(90),
      longitude: Joi.number().min(-180).max(180),
      altitude: Joi.number(),
      accuracy: Joi.number().min(0)
    }).required()
  }),

  // 迷宫创建验证
  createMaze: Joi.object({
    name: Joi.string().required().min(2).max(100)
      .error(new Error('迷宫名称必须在2-100字符之间')),
    description: Joi.string().max(500)
      .error(new Error('描述不能超过500字符')),
    difficulty: Joi.number().integer().min(1).max(5)
      .error(new Error('难度必须是1-5之间的整数')),
    width: Joi.number().integer().min(5).max(100)
      .error(new Error('宽度必须是5-100之间的整数')),
    height: Joi.number().integer().min(5).max(100)
      .error(new Error('高度必须是5-100之间的整数')),
    seasonId: Joi.string().required()
      .error(new Error('季节ID必须提供'))
  }),

  // 宝藏创建验证
  createTreasure: Joi.object({
    name: Joi.string().required().min(2).max(100)
      .error(new Error('宝藏名称必须在2-100字符之间')),
    description: Joi.string().max(500)
      .error(new Error('描述不能超过500字符')),
    rewardValue: Joi.number().min(0)
      .error(new Error('奖励值必须大于等于0')),
    rarity: Joi.string().valid(
      'common', 'uncommon', 'rare', 'epic', 'legendary'
    ).required()
      .error(new Error('稀有度必须是有效值')),
    detectionMethod: Joi.string().valid(
      'image', 'location', 'gesture', 'all'
    ).required()
      .error(new Error('检测方法必须是有效值')),
    imageMarker: Joi.string().when('detectionMethod', {
      is: Joi.string().valid('image', 'all'),
      then: Joi.required(),
      otherwise: Joi.optional()
    }).error(new Error('当检测方法包含图像时，图像标记必须提供'))
  }),

  // 团队创建验证
  createTeam: Joi.object({
    name: Joi.string().required().min(2).max(50)
      .error(new Error('团队名称必须在2-50字符之间')),
    description: Joi.string().max(200)
      .error(new Error('描述不能超过200字符')),
    isPrivate: Joi.boolean().default(false)
      .error(new Error('isPrivate必须是布尔值')),
    maxMembers: Joi.number().integer().min(2).max(10).default(5)
      .error(new Error('最大成员数必须是2-10之间的整数'))
  })
};

/**
 * 验证请求参数
 * @param {String} schemaName - 验证模式名称
 * @param {String} property - 请求属性 (body, params, query)
 * @returns {Function} Express中间件
 */
const validate = (schemaName, property = 'body') => {
  if (!schemas[schemaName]) {
    throw new Error(`验证模式${schemaName}不存在`);
  }

  return (req, res, next) => {
    try {
      const schema = schemas[schemaName];
      const dataToValidate = req[property];
      
      if (!dataToValidate) {
        return next(createError(`${property}不能为空`, 400));
      }

      const { error, value } = schema.validate(dataToValidate, {
        abortEarly: false,
        stripUnknown: true
      });

      if (error) {
        // 提取所有验证错误
        const errorDetails = error.details.map(detail => detail.message).join('; ');
        logger.warn(`请求验证失败: ${errorDetails}`);
        return next(createError(`验证失败: ${errorDetails}`, 400));
      }

      // 更新验证后的值
      req[property] = value;
      
      // 验证通过，继续处理请求
      return next();
    } catch (validationError) {
      logger.error('验证中间件错误:', validationError);
      return next(createError('验证处理失败', 500));
    }
  };
};

module.exports = {
  validate,
  schemas
}; 