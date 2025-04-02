/**
 * 数据库初始化脚本
 */
const { db } = require('./db');
const { userModel, sessionModel } = require('../models');
const { logger } = require('@suoke/shared').utils;

async function initializeDatabase() {
  try {
    // 创建用户表
    await db.query(userModel.tableStructure);
    logger.info('用户表创建成功');

    // 创建会话表
    await db.query(sessionModel.tableStructure);
    logger.info('会话表创建成功');

    // 创建索引
    await db.query(`
      CREATE INDEX idx_users_username ON users(username);
      CREATE INDEX idx_users_email ON users(email);
      CREATE INDEX idx_users_phone ON users(phone);
      CREATE INDEX idx_users_status ON users(status);
      CREATE INDEX idx_users_verification_token ON users(verification_token);
      CREATE INDEX idx_users_mfa_enabled ON users(mfa_enabled);
      CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
      CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
      CREATE INDEX idx_user_sessions_last_activity ON user_sessions(last_activity);
    `);
    logger.info('索引创建成功');

    return true;
  } catch (error) {
    logger.error('数据库初始化失败', { error: error.message });
    throw error;
  }
}

module.exports = {
  initializeDatabase
}; 