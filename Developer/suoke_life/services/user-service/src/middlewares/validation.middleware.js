/**
 * 数据验证中间件
 */
const Joi = require('joi');
const { logger } = require('@suoke/shared').utils;
const { metrics } = require('../utils');

/**
 * 常用验证规则
 */
const validationRules = {
  // 身份验证相关
  id: Joi.string().trim().pattern(/^[0-9a-fA-F]{24}$/).messages({
    'string.pattern.base': '无效的ID格式',
    'string.empty': 'ID不能为空'
  }),
  email: Joi.string().trim().email().required().messages({
    'string.email': '无效的邮箱格式',
    'string.empty': '邮箱不能为空',
    'any.required': '邮箱是必填字段'
  }),
  phone: Joi.string().trim().pattern(/^1[3-9]\d{9}$/).required().messages({
    'string.pattern.base': '无效的手机号格式',
    'string.empty': '手机号不能为空',
    'any.required': '手机号是必填字段'
  }),
  password: Joi.string().min(8).max(30).pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/).required().messages({
    'string.min': '密码长度最少为8个字符',
    'string.max': '密码长度最多为30个字符',
    'string.pattern.base': '密码必须包含大小写字母、数字和特殊字符',
    'string.empty': '密码不能为空',
    'any.required': '密码是必填字段'
  }),
  code: Joi.string().trim().length(6).pattern(/^\d{6}$/).required().messages({
    'string.length': '验证码必须为6位',
    'string.pattern.base': '验证码必须为数字',
    'string.empty': '验证码不能为空',
    'any.required': '验证码是必填字段'
  }),
  token: Joi.string().required().messages({
    'string.empty': '令牌不能为空',
    'any.required': '令牌是必填字段'
  }),
  
  // 用户资料相关
  username: Joi.string().trim().min(2).max(30).pattern(/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/).required().messages({
    'string.min': '用户名长度最少为2个字符',
    'string.max': '用户名长度最多为30个字符',
    'string.pattern.base': '用户名只能包含中英文、数字和下划线',
    'string.empty': '用户名不能为空',
    'any.required': '用户名是必填字段'
  }),
  nickname: Joi.string().trim().min(2).max(30).pattern(/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/).required().messages({
    'string.min': '昵称长度最少为2个字符',
    'string.max': '昵称长度最多为30个字符',
    'string.pattern.base': '昵称只能包含中英文、数字和下划线',
    'string.empty': '昵称不能为空',
    'any.required': '昵称是必填字段'
  }),
  gender: Joi.string().valid('male', 'female', 'other', 'prefer_not_to_say').required().messages({
    'any.only': '性别必须是male, female, other或prefer_not_to_say',
    'string.empty': '性别不能为空',
    'any.required': '性别是必填字段'
  }),
  birthdate: Joi.date().less('now').messages({
    'date.less': '出生日期必须早于当前日期',
    'date.base': '无效的日期格式'
  }),
  role: Joi.string().valid('user', 'premium_user', 'admin', 'system_admin').default('user').messages({
    'any.only': '角色必须是user, premium_user, admin或system_admin之一'
  }),
  status: Joi.string().valid('active', 'inactive', 'pending', 'banned').default('pending').messages({
    'any.only': '状态必须是active, inactive, pending或banned之一'
  }),
  
  // 健康资料相关
  height: Joi.number().min(50).max(250).messages({
    'number.min': '身高必须大于50cm',
    'number.max': '身高必须小于250cm',
    'number.base': '身高必须是数字'
  }),
  weight: Joi.number().min(2).max(500).messages({
    'number.min': '体重必须大于2kg',
    'number.max': '体重必须小于500kg',
    'number.base': '体重必须是数字'
  }),
  blood_pressure_systolic: Joi.number().min(50).max(250).messages({
    'number.min': '收缩压必须大于50mmHg',
    'number.max': '收缩压必须小于250mmHg',
    'number.base': '收缩压必须是数字'
  }),
  blood_pressure_diastolic: Joi.number().min(30).max(150).messages({
    'number.min': '舒张压必须大于30mmHg',
    'number.max': '舒张压必须小于150mmHg',
    'number.base': '舒张压必须是数字'
  }),
  pulse: Joi.number().min(30).max(250).messages({
    'number.min': '脉搏必须大于30bpm',
    'number.max': '脉搏必须小于250bpm',
    'number.base': '脉搏必须是数字'
  }),
  constitution_type: Joi.string().valid(
    'balanced', 'qi_deficiency', 'yang_deficiency', 'yin_deficiency', 
    'phlegm_dampness', 'damp_heat', 'blood_stasis', 'qi_stagnation', 'special'
  ).messages({
    'any.only': '体质类型无效'
  }),
  
  // 分页和排序相关
  page: Joi.number().integer().min(1).default(1).messages({
    'number.base': '页码必须是数字',
    'number.integer': '页码必须是整数',
    'number.min': '页码最小为1'
  }),
  limit: Joi.number().integer().min(1).max(100).default(20).messages({
    'number.base': '每页条数必须是数字',
    'number.integer': '每页条数必须是整数',
    'number.min': '每页条数最小为1',
    'number.max': '每页条数最大为100'
  }),
  sort_by: Joi.string().messages({
    'string.empty': '排序字段不能为空'
  }),
  sort_order: Joi.string().valid('asc', 'desc').default('desc').messages({
    'any.only': '排序方向必须是asc或desc'
  }),
  
  // 高级查询参数
  search: Joi.string().trim().max(100).messages({
    'string.max': '搜索关键词最多为100个字符'
  }),
  filters: Joi.object().messages({
    'object.base': '筛选条件必须是对象格式'
  }),
  
  // 日期范围
  date_range: Joi.object({
    start_date: Joi.date().required().messages({
      'date.base': '开始日期格式无效',
      'any.required': '开始日期是必填字段'
    }),
    end_date: Joi.date().min(Joi.ref('start_date')).required().messages({
      'date.base': '结束日期格式无效',
      'date.min': '结束日期必须晚于开始日期',
      'any.required': '结束日期是必填字段'
    })
  }),
  
  // 文件相关
  file_size: Joi.number().max(10 * 1024 * 1024).messages({
    'number.max': '文件大小不能超过10MB'
  }),
  file_type: Joi.string().valid('image/jpeg', 'image/png', 'image/gif', 'application/pdf').messages({
    'any.only': '不支持的文件类型'
  }),
  
  // 其他常用
  boolean: Joi.boolean().messages({
    'boolean.base': '必须是布尔值(true/false)'
  }),
  url: Joi.string().uri().messages({
    'string.uri': '无效的URL格式'
  }),
  array: Joi.array().messages({
    'array.base': '必须是数组格式'
  }),
  object: Joi.object().messages({
    'object.base': '必须是对象格式'
  }),
  string: Joi.string().messages({
    'string.base': '必须是字符串格式'
  }),
  number: Joi.number().messages({
    'number.base': '必须是数字格式'
  }),
  
  // 业务相关
  preference_key: Joi.string().trim().min(2).max(50).pattern(/^[a-zA-Z0-9_]+$/).messages({
    'string.min': '偏好设置键长度最少为2个字符',
    'string.max': '偏好设置键长度最多为50个字符',
    'string.pattern.base': '偏好设置键只能包含英文、数字和下划线',
    'string.empty': '偏好设置键不能为空'
  }),
  preference_value: Joi.alternatives().try(
    Joi.string(),
    Joi.number(),
    Joi.boolean(),
    Joi.object(),
    Joi.array()
  ).messages({
    'alternatives.match': '偏好设置值格式无效'
  })
};

/**
 * 验证规则集
 */
const schemas = {
  // 用户相关
  registerUser: Joi.object({
    username: validationRules.username,
    email: validationRules.email,
    phone: validationRules.phone,
    password: validationRules.password,
    nickname: validationRules.nickname.optional(),
    gender: validationRules.gender.optional(),
    birthdate: validationRules.birthdate.optional()
  }),
  
  loginUser: Joi.object({
    username: Joi.alternatives().try(
      validationRules.email,
      validationRules.phone,
      validationRules.username
    ).required().messages({
      'alternatives.match': '用户名/邮箱/手机号格式无效',
      'any.required': '用户名/邮箱/手机号是必填字段'
    }),
    password: validationRules.password,
    remember_me: validationRules.boolean.default(false)
  }),
  
  verifyEmail: Joi.object({
    email: validationRules.email,
    code: validationRules.code
  }),
  
  verifyPhone: Joi.object({
    phone: validationRules.phone,
    code: validationRules.code
  }),
  
  resetPassword: Joi.object({
    token: validationRules.token,
    password: validationRules.password,
    confirm_password: Joi.ref('password')
  }).with('password', 'confirm_password'),
  
  changePassword: Joi.object({
    current_password: validationRules.password,
    new_password: validationRules.password,
    confirm_password: Joi.ref('new_password')
  }).with('new_password', 'confirm_password'),
  
  updateUserProfile: Joi.object({
    nickname: validationRules.nickname.optional(),
    gender: validationRules.gender.optional(),
    birthdate: validationRules.birthdate.optional(),
    avatar: Joi.string().optional(),
    bio: Joi.string().max(500).optional().messages({
      'string.max': '个人简介最多500个字符'
    }),
    location: Joi.string().max(100).optional().messages({
      'string.max': '地区最多100个字符'
    }),
    profession: Joi.string().max(100).optional().messages({
      'string.max': '职业最多100个字符'
    })
  }),
  
  // 健康资料相关
  updateHealthProfile: Joi.object({
    height: validationRules.height.optional(),
    weight: validationRules.weight.optional(),
    blood_pressure_systolic: validationRules.blood_pressure_systolic.optional(),
    blood_pressure_diastolic: validationRules.blood_pressure_diastolic.optional(),
    pulse: validationRules.pulse.optional(),
    constitution_type: validationRules.constitution_type.optional(),
    medical_history: Joi.string().max(1000).optional().messages({
      'string.max': '病史最多1000个字符'
    }),
    allergies: Joi.array().items(Joi.string()).optional(),
    chronic_diseases: Joi.array().items(Joi.string()).optional(),
    medications: Joi.array().items(Joi.string()).optional()
  }),
  
  // 分页查询相关
  pagination: Joi.object({
    page: validationRules.page,
    limit: validationRules.limit,
    sort_by: validationRules.sort_by.optional(),
    sort_order: validationRules.sort_order.optional(),
    search: validationRules.search.optional(),
    filters: validationRules.filters.optional()
  }),
  
  // OpenAI工具相关
  getUserProfile: Joi.object({
    user_id: validationRules.id.optional(),
    fields: Joi.array().items(Joi.string()).optional()
  }),
  
  getConstitutionProfile: Joi.object({
    user_id: validationRules.id.optional(),
    include_history: validationRules.boolean.optional()
  }),
  
  getHealthRecommendations: Joi.object({
    user_id: validationRules.id.optional(),
    category: Joi.string().valid('dietary', 'lifestyle', 'herbal', 'all').default('all').messages({
      'any.only': '类别必须是dietary, lifestyle, herbal或all之一'
    }),
    season: Joi.string().optional()
  }),
  
  updateUserPreference: Joi.object({
    user_id: validationRules.id.optional(),
    preferences: Joi.object().pattern(
      validationRules.preference_key,
      validationRules.preference_value
    ).required().messages({
      'object.base': '偏好设置必须是对象格式',
      'any.required': '偏好设置是必填字段'
    })
  }),
  
  getAchievementStatus: Joi.object({
    user_id: validationRules.id.optional(),
    category: Joi.string().valid(
      'health_tracking', 'learning', 'social', 'lifestyle', 'tcm_knowledge', 'all'
    ).default('all').messages({
      'any.only': '类别无效'
    })
  }),
  
  getVouchers: Joi.object({
    user_id: validationRules.id.optional(),
    status: Joi.string().valid('available', 'used', 'expired', 'all').default('all').messages({
      'any.only': '状态必须是available, used, expired或all之一'
    }),
    type: Joi.string().valid('physical_service', 'product_discount', 'experience_ticket', 'all').default('all').messages({
      'any.only': '类型无效'
    })
  })
};

/**
 * 验证请求体
 * @param {Object} schema - Joi验证模式
 * @param {Boolean} abortEarly - 是否在第一个错误时中止验证
 * @returns {Function} Express中间件
 */
const validateBody = (schema, abortEarly = false) => {
  return (req, res, next) => {
    const startTime = process.hrtime();
    const validationMetricLabels = {
      method: req.method,
      route: req.route?.path || req.path,
      type: 'body'
    };
    
    const { error, value } = schema.validate(req.body, { 
      abortEarly, 
      stripUnknown: true 
    });
    
    const [seconds, nanoseconds] = process.hrtime(startTime);
    const duration = seconds + nanoseconds / 1e9;
    
    // 记录验证耗时
    metrics.validationDurationHistogram?.observe(validationMetricLabels, duration);
    
    if (error) {
      // 记录验证失败
      metrics.validationFailureCounter?.inc(validationMetricLabels);
      
      const errorMessage = error.details.map(detail => detail.message).join(', ');
      
      logger.warn('请求体验证失败', {
        error: errorMessage,
        path: req.path,
        body: JSON.stringify(req.body)
      });
      
      return res.status(400).json({
        status: 'error',
        code: 'validation_error',
        message: '数据验证失败',
        errors: error.details.map(detail => ({
          field: detail.context.key,
          message: detail.message
        }))
      });
    }
    
    // 记录验证成功
    metrics.validationSuccessCounter?.inc(validationMetricLabels);
    
    // 替换请求体为验证后的值
    req.body = value;
    next();
  };
};

/**
 * 验证请求查询参数
 * @param {Object} schema - Joi验证模式
 * @param {Boolean} abortEarly - 是否在第一个错误时中止验证
 * @returns {Function} Express中间件
 */
const validateQuery = (schema, abortEarly = false) => {
  return (req, res, next) => {
    const startTime = process.hrtime();
    const validationMetricLabels = {
      method: req.method,
      route: req.route?.path || req.path,
      type: 'query'
    };
    
    const { error, value } = schema.validate(req.query, { 
      abortEarly, 
      stripUnknown: true 
    });
    
    const [seconds, nanoseconds] = process.hrtime(startTime);
    const duration = seconds + nanoseconds / 1e9;
    
    // 记录验证耗时
    metrics.validationDurationHistogram?.observe(validationMetricLabels, duration);
    
    if (error) {
      // 记录验证失败
      metrics.validationFailureCounter?.inc(validationMetricLabels);
      
      const errorMessage = error.details.map(detail => detail.message).join(', ');
      
      logger.warn('查询参数验证失败', {
        error: errorMessage,
        path: req.path,
        query: JSON.stringify(req.query)
      });
      
      return res.status(400).json({
        status: 'error',
        code: 'validation_error',
        message: '查询参数验证失败',
        errors: error.details.map(detail => ({
          field: detail.context.key,
          message: detail.message
        }))
      });
    }
    
    // 记录验证成功
    metrics.validationSuccessCounter?.inc(validationMetricLabels);
    
    // 替换查询参数为验证后的值
    req.query = value;
    next();
  };
};

/**
 * 验证请求参数
 * @param {Object} schema - Joi验证模式
 * @param {Boolean} abortEarly - 是否在第一个错误时中止验证
 * @returns {Function} Express中间件
 */
const validateParams = (schema, abortEarly = false) => {
  return (req, res, next) => {
    const startTime = process.hrtime();
    const validationMetricLabels = {
      method: req.method,
      route: req.route?.path || req.path,
      type: 'params'
    };
    
    const { error, value } = schema.validate(req.params, { 
      abortEarly, 
      stripUnknown: true 
    });
    
    const [seconds, nanoseconds] = process.hrtime(startTime);
    const duration = seconds + nanoseconds / 1e9;
    
    // 记录验证耗时
    metrics.validationDurationHistogram?.observe(validationMetricLabels, duration);
    
    if (error) {
      // 记录验证失败
      metrics.validationFailureCounter?.inc(validationMetricLabels);
      
      const errorMessage = error.details.map(detail => detail.message).join(', ');
      
      logger.warn('路径参数验证失败', {
        error: errorMessage,
        path: req.path,
        params: JSON.stringify(req.params)
      });
      
      return res.status(400).json({
        status: 'error',
        code: 'validation_error',
        message: '路径参数验证失败',
        errors: error.details.map(detail => ({
          field: detail.context.key,
          message: detail.message
        }))
      });
    }
    
    // 记录验证成功
    metrics.validationSuccessCounter?.inc(validationMetricLabels);
    
    // 替换路径参数为验证后的值
    req.params = value;
    next();
  };
};

/**
 * 验证文件上传
 * @param {Object} options - 上传配置选项
 * @returns {Function} Express中间件
 */
const validateFileUpload = (options = {}) => {
  const defaultOptions = {
    maxSize: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif'],
    maxFiles: 1,
    fieldName: 'file'
  };
  
  const config = { ...defaultOptions, ...options };
  
  return (req, res, next) => {
    if (!req.files || !req.files[config.fieldName]) {
      return res.status(400).json({
        status: 'error',
        code: 'file_upload_error',
        message: '未找到上传文件'
      });
    }
    
    const files = Array.isArray(req.files[config.fieldName]) 
      ? req.files[config.fieldName] 
      : [req.files[config.fieldName]];
    
    // 检查文件数量
    if (files.length > config.maxFiles) {
      return res.status(400).json({
        status: 'error',
        code: 'file_upload_error',
        message: `最多只能上传${config.maxFiles}个文件`
      });
    }
    
    // 验证每个文件
    const errors = [];
    
    files.forEach((file, index) => {
      // 检查文件大小
      if (file.size > config.maxSize) {
        errors.push({
          file: file.name,
          field: `${config.fieldName}[${index}]`,
          message: `文件大小不能超过${config.maxSize / 1024 / 1024}MB`
        });
      }
      
      // 检查文件类型
      if (!config.allowedTypes.includes(file.mimetype)) {
        errors.push({
          file: file.name,
          field: `${config.fieldName}[${index}]`,
          message: `不支持的文件类型，允许的类型: ${config.allowedTypes.join(', ')}`
        });
      }
    });
    
    if (errors.length > 0) {
      return res.status(400).json({
        status: 'error',
        code: 'file_validation_error',
        message: '文件验证失败',
        errors
      });
    }
    
    next();
  };
};

// 内容安全验证
const validateContentSafety = (field, options = {}) => {
  const defaultOptions = {
    maxLength: 1000,
    checkForSensitiveData: true,
    checkForProfanity: true,
    checkForMaliciousContent: true
  };
  
  const config = { ...defaultOptions, ...options };
  
  return (req, res, next) => {
    const content = req.body[field];
    
    if (!content) {
      return next();
    }
    
    // 内容长度检查
    if (content.length > config.maxLength) {
      return res.status(400).json({
        status: 'error',
        code: 'content_validation_error',
        message: `内容长度不能超过${config.maxLength}个字符`
      });
    }
    
    // TODO: 实现更多内容安全检查，如敏感词过滤、恶意内容检测等
    // 这里可以集成第三方服务或自己实现敏感词过滤算法
    
    next();
  };
};

module.exports = {
  schemas,
  validationRules,
  validateBody,
  validateQuery,
  validateParams,
  validateFileUpload,
  validateContentSafety
};