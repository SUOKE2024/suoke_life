import Joi from 'joi';

export const questStepSchema = Joi.object({
  data: Joi.alternatives().try(
    Joi.object(),
    Joi.array(),
    Joi.string(),
    Joi.number(),
    Joi.boolean()
  ).required().messages({
    'any.required': '步骤数据不能为空',
  })
});

export const questSchema = Joi.object({
  title: Joi.string().required().max(100).messages({
    'string.empty': '任务标题不能为空',
    'string.max': '任务标题不能超过100个字符',
    'any.required': '任务标题是必填项'
  }),
  description: Joi.string().required().messages({
    'string.empty': '任务描述不能为空',
    'any.required': '任务描述是必填项'
  }),
  type: Joi.string().valid('main', 'side', 'daily', 'event', 'challenge').required().messages({
    'string.empty': '任务类型不能为空',
    'any.only': '任务类型必须是main、side、daily、event或challenge之一',
    'any.required': '任务类型是必填项'
  }),
  difficulty: Joi.string().valid('easy', 'medium', 'hard', 'expert').required().messages({
    'string.empty': '任务难度不能为空',
    'any.only': '任务难度必须是easy、medium、hard或expert之一',
    'any.required': '任务难度是必填项'
  }),
  reward: Joi.object({
    points: Joi.number().required().min(0).messages({
      'number.base': '积分奖励必须是数字',
      'number.min': '积分奖励不能为负数',
      'any.required': '积分奖励是必填项'
    }),
    experience: Joi.number().required().min(0).messages({
      'number.base': '经验奖励必须是数字',
      'number.min': '经验奖励不能为负数',
      'any.required': '经验奖励是必填项'
    }),
    items: Joi.array().items(
      Joi.object({
        itemId: Joi.string().required(),
        quantity: Joi.number().integer().min(1).default(1)
      })
    )
  }).required(),
  requirements: Joi.object({
    level: Joi.number().integer().min(1),
    quests: Joi.array().items(Joi.string()),
    items: Joi.array().items(
      Joi.object({
        itemId: Joi.string().required(),
        quantity: Joi.number().integer().min(1).default(1)
      })
    )
  }),
  steps: Joi.array().items(
    Joi.object({
      order: Joi.number().integer().required().min(0),
      description: Joi.string().required(),
      location: Joi.object({
        latitude: Joi.number().required(),
        longitude: Joi.number().required(),
        radius: Joi.number().required().min(1)
      }),
      actionType: Joi.string().valid('collect', 'interact', 'photo', 'scan', 'answer'),
      target: Joi.string(),
      quantity: Joi.number().integer().min(1)
    })
  ).required().min(1).messages({
    'array.min': '任务至少需要一个步骤',
    'any.required': '任务步骤是必填项'
  }),
  duration: Joi.number().integer().min(0),
  startDate: Joi.date(),
  endDate: Joi.date().greater(Joi.ref('startDate')).messages({
    'date.greater': '结束日期必须晚于开始日期'
  }),
  isActive: Joi.boolean().default(true)
}); 