/**
 * 数据验证工具模块
 * 提供通用的数据验证功能
 */
const Joi = require('joi');

/**
 * 验证中间件生成器
 * @param {Object} schema - Joi验证模式
 * @param {string} property - 要验证的请求属性 (body, params, query)
 * @returns {Function} Express中间件
 */
const validate = (schema, property = 'body') => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req[property], { 
      abortEarly: false,
      stripUnknown: true,
      allowUnknown: property !== 'body' // 允许params和query中有未知字段
    });
    
    if (error) {
      const details = error.details.map(detail => ({
        message: detail.message,
        path: detail.path.join('.')
      }));
      
      return res.status(400).json({
        success: false,
        message: '数据验证失败',
        details,
        timestamp: new Date().toISOString()
      });
    }
    
    // 替换验证后的值
    req[property] = value;
    next();
  };
};

/**
 * 通用验证规则
 */
const rules = {
  // 字符串规则
  string: {
    email: Joi.string().email().message('必须是有效的电子邮件'),
    password: Joi.string().min(8).max(30).pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/).message('密码必须包含大小写字母和数字，长度8-30字符'),
    name: Joi.string().min(2).max(50).message('名称长度必须在2-50字符之间'),
    phone: Joi.string().pattern(/^1[3-9]\d{9}$/).message('必须是有效的中国手机号码'),
    uuid: Joi.string().guid({ version: 'uuidv4' }).message('必须是有效的UUID v4'),
    date: Joi.string().isoDate().message('必须是有效的ISO日期格式'),
    url: Joi.string().uri().message('必须是有效的URL')
  },
  // 数字规则
  number: {
    id: Joi.number().integer().positive().message('ID必须是正整数'),
    age: Joi.number().integer().min(0).max(120).message('年龄必须在0-120之间'),
    price: Joi.number().precision(2).positive().message('价格必须是正数，最多两位小数'),
    rating: Joi.number().min(0).max(5).message('评分必须在0-5之间')
  },
  // 数组规则
  array: {
    ids: Joi.array().items(Joi.number().integer().positive()).message('ID列表必须是正整数数组'),
    uuids: Joi.array().items(Joi.string().guid({ version: 'uuidv4' })).message('UUID列表必须是有效的UUID v4数组'),
    strings: Joi.array().items(Joi.string())
  },
  // 分页规则
  pagination: {
    page: Joi.number().integer().min(1).default(1).message('页码必须是大于等于1的整数'),
    limit: Joi.number().integer().min(1).max(100).default(10).message('每页数量必须是1-100之间的整数')
  }
};

/**
 * 常用验证模式
 */
const schemas = {
  // 用户相关
  user: {
    login: Joi.object({
      email: rules.string.email.required(),
      password: Joi.string().required()
    }),
    register: Joi.object({
      name: rules.string.name.required(),
      email: rules.string.email.required(),
      password: rules.string.password.required(),
      phone: rules.string.phone
    }),
    update: Joi.object({
      name: rules.string.name,
      phone: rules.string.phone,
      avatar: Joi.string().uri()
    })
  },
  // ID参数
  params: {
    id: Joi.object({
      id: rules.number.id.required()
    }),
    uuid: Joi.object({
      id: rules.string.uuid.required()
    })
  },
  // 分页查询
  query: {
    pagination: Joi.object({
      page: rules.pagination.page,
      limit: rules.pagination.limit
    })
  }
};

module.exports = {
  validate,
  rules,
  schemas
}; 