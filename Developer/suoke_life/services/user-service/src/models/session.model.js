/**
 * 用户会话模型
 */
const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');

// 会话表名
const TABLE_NAME = 'user_sessions';

// 会话创建验证模式
const createSchema = Joi.object({
  user_id: Joi.string().uuid().required().description('用户ID'),
  device_info: Joi.object().description('设备信息'),
  ip_address: Joi.string().ip().description('IP地址'),
  user_agent: Joi.string().description('用户代理'),
  expires_at: Joi.date().iso().required().description('过期时间')
});

// 会话更新验证模式
const updateSchema = Joi.object({
  device_info: Joi.object().description('设备信息'),
  ip_address: Joi.string().ip().description('IP地址'),
  user_agent: Joi.string().description('用户代理'),
  last_activity: Joi.date().iso().description('最后活动时间'),
  expires_at: Joi.date().iso().description('过期时间')
});

// 会话查询验证模式
const querySchema = Joi.object({
  user_id: Joi.string().uuid().description('用户ID'),
  ip_address: Joi.string().ip().description('IP地址'),
  active: Joi.boolean().description('是否活跃'),
  page: Joi.number().min(1).description('页码'),
  page_size: Joi.number().min(1).max(100).description('每页数量')
});

// 生成会话ID
const generateSessionId = () => {
  return uuidv4();
};

// 数据库表结构
const tableStructure = `
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
  querySchema,
  generateSessionId,
  tableStructure
}; 