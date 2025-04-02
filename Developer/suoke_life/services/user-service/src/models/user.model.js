/**
 * 用户模型
 */
const Joi = require('joi');
const bcrypt = require('bcrypt');
const config = require('../config');

// 用户表名
const TABLE_NAME = 'users';

// 用户创建验证模式
const createSchema = Joi.object({
  username: Joi.string().min(3).max(50).required().description('用户名'),
  email: Joi.string().email().description('电子邮箱'),
  phone: Joi.string().pattern(/^1[3-9]\d{9}$/).description('手机号码'),
  password: Joi.string().min(8).max(100).required().description('密码'),
  role: Joi.string().valid('user', 'admin').default('user').description('角色'),
  mfa_enabled: Joi.boolean().default(false).description('是否启用多因素认证'),
  mfa_secret: Joi.string().description('多因素认证密钥'),
  mfa_backup_codes: Joi.array().items(Joi.string()).description('多因素认证备用码')
}).or('email', 'phone');

// 用户更新验证模式
const updateSchema = Joi.object({
  email: Joi.string().email().description('电子邮箱'),
  phone: Joi.string().pattern(/^1[3-9]\d{9}$/).description('手机号码'),
  password: Joi.string().min(8).max(100).description('密码'),
  role: Joi.string().valid('user', 'admin').description('角色'),
  status: Joi.string().valid('active', 'inactive', 'suspended').description('状态'),
  mfa_enabled: Joi.boolean().description('是否启用多因素认证'),
  mfa_secret: Joi.string().description('多因素认证密钥'),
  mfa_backup_codes: Joi.array().items(Joi.string()).description('多因素认证备用码')
});

// 用户登录验证模式
const loginSchema = Joi.object({
  username: Joi.string().description('用户名'),
  email: Joi.string().email().description('电子邮箱'),
  phone: Joi.string().pattern(/^1[3-9]\d{9}$/).description('手机号码'),
  password: Joi.string().required().description('密码'),
  mfa_code: Joi.string().length(6).pattern(/^\d+$/).description('多因素认证码')
}).or('username', 'email', 'phone');

// 重置密码验证模式
const resetPasswordSchema = Joi.object({
  email: Joi.string().email().required().description('电子邮箱'),
  newPassword: Joi.string().min(8).max(100).required().description('新密码')
});

// 验证码发送验证模式
const verificationCodeSchema = Joi.object({
  type: Joi.string().valid('email', 'phone').required().description('验证类型'),
  contact: Joi.alternatives().conditional('type', {
    is: 'email',
    then: Joi.string().email().required(),
    otherwise: Joi.string().pattern(/^1[3-9]\d{9}$/).required()
  }).description('联系方式')
});

// 验证码验证模式
const verifyCodeSchema = Joi.object({
  token: Joi.string().required().description('验证令牌'),
  code: Joi.string().length(6).pattern(/^\d+$/).required().description('验证码')
});

// 多因素认证验证模式
const mfaSchema = Joi.object({
  code: Joi.string().length(6).pattern(/^\d+$/).required().description('多因素认证码'),
  backup_code: Joi.string().description('备用码')
}).or('code', 'backup_code');

// 密码哈希生成
const hashPassword = async (password) => {
  return await bcrypt.hash(password, config.crypto.saltRounds);
};

// 密码验证
const verifyPassword = async (password, hashedPassword) => {
  return await bcrypt.compare(password, hashedPassword);
};

// 数据库表结构
const tableStructure = `
  CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    status VARCHAR(20) NOT NULL DEFAULT 'inactive',
    verification_token VARCHAR(255),
    verification_token_expires TIMESTAMP,
    last_login TIMESTAMP,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(32),
    mfa_backup_codes JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
  )
`;

// 用户会话表结构
const sessionTableStructure = `
  CREATE TABLE IF NOT EXISTS user_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    device_info JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  )
`;

module.exports = {
  TABLE_NAME,
  createSchema,
  updateSchema,
  loginSchema,
  resetPasswordSchema,
  verificationCodeSchema,
  verifyCodeSchema,
  mfaSchema,
  hashPassword,
  verifyPassword,
  tableStructure,
  sessionTableStructure
}; 