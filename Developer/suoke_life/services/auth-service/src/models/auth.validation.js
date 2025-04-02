/**
 * 认证服务验证规则
 */
const Joi = require('joi');

// 用户注册验证
const register = Joi.object({
  username: Joi.string()
    .min(3)
    .max(30)
    .alphanum()
    .required()
    .messages({
      'string.base': '用户名必须是字符串',
      'string.empty': '用户名不能为空',
      'string.min': '用户名长度不能小于{#limit}个字符',
      'string.max': '用户名长度不能超过{#limit}个字符',
      'string.alphanum': '用户名只能包含字母和数字',
      'any.required': '用户名是必填项'
    }),
  email: Joi.string()
    .email()
    .required()
    .messages({
      'string.base': '邮箱必须是字符串',
      'string.empty': '邮箱不能为空',
      'string.email': '邮箱格式无效',
      'any.required': '邮箱是必填项'
    }),
  password: Joi.string()
    .min(6)
    .max(30)
    .required()
    .messages({
      'string.base': '密码必须是字符串',
      'string.empty': '密码不能为空',
      'string.min': '密码长度不能小于{#limit}个字符',
      'string.max': '密码长度不能超过{#limit}个字符',
      'any.required': '密码是必填项'
    }),
  confirmPassword: Joi.string()
    .valid(Joi.ref('password'))
    .required()
    .messages({
      'string.base': '确认密码必须是字符串',
      'string.empty': '确认密码不能为空',
      'any.only': '确认密码必须与密码相同',
      'any.required': '确认密码是必填项'
    }),
  role: Joi.string()
    .valid('user', 'admin')
    .default('user')
    .messages({
      'string.base': '角色必须是字符串',
      'any.only': '角色只能是以下之一: {#valids}'
    })
});

// 用户登录验证
const login = Joi.object({
  username: Joi.string()
    .required()
    .messages({
      'string.base': '用户名必须是字符串',
      'string.empty': '用户名不能为空',
      'any.required': '用户名是必填项'
    }),
  password: Joi.string()
    .required()
    .messages({
      'string.base': '密码必须是字符串',
      'string.empty': '密码不能为空',
      'any.required': '密码是必填项'
    })
});

// 刷新令牌验证
const refreshToken = Joi.object({
  refreshToken: Joi.string()
    .required()
    .messages({
      'string.base': '刷新令牌必须是字符串',
      'string.empty': '刷新令牌不能为空',
      'any.required': '刷新令牌是必填项'
    })
});

// 忘记密码验证
const forgotPassword = Joi.object({
  email: Joi.string()
    .email()
    .required()
    .messages({
      'string.base': '邮箱必须是字符串',
      'string.empty': '邮箱不能为空',
      'string.email': '邮箱格式无效',
      'any.required': '邮箱是必填项'
    })
});

// 重置密码验证
const resetPassword = Joi.object({
  token: Joi.string()
    .required()
    .messages({
      'string.base': '令牌必须是字符串',
      'string.empty': '令牌不能为空',
      'any.required': '令牌是必填项'
    }),
  password: Joi.string()
    .min(6)
    .max(30)
    .required()
    .messages({
      'string.base': '密码必须是字符串',
      'string.empty': '密码不能为空',
      'string.min': '密码长度不能小于{#limit}个字符',
      'string.max': '密码长度不能超过{#limit}个字符',
      'any.required': '密码是必填项'
    }),
  confirmPassword: Joi.string()
    .valid(Joi.ref('password'))
    .required()
    .messages({
      'string.base': '确认密码必须是字符串',
      'string.empty': '确认密码不能为空',
      'any.only': '确认密码必须与密码相同',
      'any.required': '确认密码是必填项'
    })
});

module.exports = {
  register,
  login,
  refreshToken,
  forgotPassword,
  resetPassword
}; 