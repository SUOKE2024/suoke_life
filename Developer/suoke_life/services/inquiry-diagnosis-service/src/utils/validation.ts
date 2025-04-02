import Joi from 'joi';
import { ValidationError } from './error-handler';

/**
 * 验证对象
 * @param schema Joi验证模式
 * @param data 需要验证的数据
 * @returns 经过验证和转换的数据
 * @throws ValidationError 如果验证失败
 */
export function validate<T>(schema: Joi.Schema, data: any): T {
  const options: Joi.ValidationOptions = {
    abortEarly: false, // 返回所有错误
    stripUnknown: true, // 移除未知字段
    convert: true // 类型转换
  };

  const { error, value } = schema.validate(data, options);
  
  if (error) {
    // 构建所有验证错误的消息
    const errorMessages = error.details
      .map(detail => detail.message.replace(/"/g, ''))
      .join('; ');
    
    throw new ValidationError(errorMessages);
  }
  
  return value as T;
}

/**
 * 常用的验证模式
 */
export const ValidationSchemas = {
  /**
   * ID验证模式
   */
  id: Joi.string().trim().required().messages({
    'string.empty': 'ID不能为空',
    'any.required': '必须提供ID'
  }),
  
  /**
   * 用户ID验证模式
   */
  userId: Joi.string().trim().required().messages({
    'string.empty': '用户ID不能为空',
    'any.required': '必须提供用户ID'
  }),
  
  /**
   * 会话ID验证模式
   */
  sessionId: Joi.string().trim().required().messages({
    'string.empty': '会话ID不能为空',
    'any.required': '必须提供会话ID'
  }),
  
  /**
   * 文本内容验证模式
   */
  text: Joi.string().trim().required().messages({
    'string.empty': '文本内容不能为空',
    'any.required': '必须提供文本内容'
  }),
  
  /**
   * 文本内容验证模式(可选)
   */
  optionalText: Joi.string().trim().allow('').optional(),
  
  /**
   * 症状名称验证模式
   */
  symptomName: Joi.string().trim().min(1).max(100).required().messages({
    'string.empty': '症状名称不能为空',
    'string.min': '症状名称至少需要1个字符',
    'string.max': '症状名称不能超过100个字符',
    'any.required': '必须提供症状名称'
  }),
  
  /**
   * 症状位置验证模式(可选)
   */
  symptomLocation: Joi.string().trim().max(100).optional().allow('').messages({
    'string.max': '症状位置不能超过100个字符'
  }),
  
  /**
   * 症状严重程度验证模式(可选)
   */
  symptomSeverity: Joi.number().min(1).max(10).optional().messages({
    'number.min': '症状严重程度不能小于1',
    'number.max': '症状严重程度不能大于10'
  }),
  
  /**
   * 症状持续时间验证模式(可选)
   */
  symptomDuration: Joi.string().trim().max(100).optional().allow('').messages({
    'string.max': '症状持续时间不能超过100个字符'
  }),
  
  /**
   * 症状频率验证模式(可选)
   */
  symptomFrequency: Joi.string().trim().max(100).optional().allow('').messages({
    'string.max': '症状频率不能超过100个字符'
  }),
  
  /**
   * 病人年龄验证模式
   */
  patientAge: Joi.number().integer().min(0).max(120).optional().messages({
    'number.base': '年龄必须是数字',
    'number.integer': '年龄必须是整数',
    'number.min': '年龄不能小于0',
    'number.max': '年龄不能大于120'
  }),

  /**
   * 病人性别验证模式
   */
  patientGender: Joi.string().valid('男', '女', '其他').optional().messages({
    'any.only': '性别必须是"男"、"女"或"其他"'
  }),
  
  /**
   * 分页参数验证模式
   */
  pagination: {
    page: Joi.number().integer().min(1).default(1).messages({
      'number.base': '页码必须是数字',
      'number.integer': '页码必须是整数',
      'number.min': '页码不能小于1'
    }),
    limit: Joi.number().integer().min(1).max(100).default(10).messages({
      'number.base': '每页数量必须是数字',
      'number.integer': '每页数量必须是整数',
      'number.min': '每页数量不能小于1',
      'number.max': '每页数量不能大于100'
    })
  }
};