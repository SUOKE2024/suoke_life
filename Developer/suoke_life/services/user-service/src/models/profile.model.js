/**
 * 个人资料模型
 */
const Joi = require('joi');

// 个人资料创建验证模式
const createSchema = Joi.object({
  nickname: Joi.string().min(2).max(50).description('昵称'),
  avatar_url: Joi.string().uri().description('头像URL'),
  gender: Joi.string().valid('male', 'female', 'other', 'prefer_not_to_say').description('性别'),
  birth_date: Joi.date().max('now').description('出生日期'),
  location: Joi.string().max(100).description('位置'),
  bio: Joi.string().max(500).description('个人简介')
});

// 个人资料更新验证模式
const updateSchema = Joi.object({
  nickname: Joi.string().min(2).max(50).description('昵称'),
  avatar_url: Joi.string().uri().description('头像URL'),
  gender: Joi.string().valid('male', 'female', 'other', 'prefer_not_to_say').description('性别'),
  birth_date: Joi.date().max('now').description('出生日期'),
  location: Joi.string().max(100).description('位置'),
  bio: Joi.string().max(500).description('个人简介')
});

// 头像更新验证模式
const avatarSchema = Joi.object({
  avatarUrl: Joi.string().uri().required().description('头像URL')
});

// 数据库表结构
const tableStructure = `
  CREATE TABLE IF NOT EXISTS profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) UNIQUE NOT NULL,
    nickname VARCHAR(50),
    avatar_url TEXT,
    gender VARCHAR(10),
    birth_date DATE,
    location VARCHAR(100),
    bio TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  )
`;

module.exports = {
  createSchema,
  updateSchema,
  avatarSchema,
  tableStructure
}; 