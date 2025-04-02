/**
 * 数据库初始化
 * 负责在服务启动时创建必要的数据库表
 */
const { logger } = require('@suoke/shared').utils;
const { db, connectDatabase } = require('./database');
const dbSchema = require('./database-schema');

/**
 * 初始化数据库表结构
 * @returns {Promise<void>}
 */
const initDatabase = async () => {
  try {
    logger.info('开始初始化数据库表结构...');

    // 确保数据库连接已建立
    await connectDatabase();

    // 创建用户表(如果不存在)
    if (dbSchema.USERS_SCHEMA) {
      await db.raw(dbSchema.USERS_SCHEMA);
      logger.info('用户表结构初始化成功');
    }

    // 创建令牌表(如果不存在)
    if (dbSchema.TOKENS_SCHEMA) {
      await db.raw(dbSchema.TOKENS_SCHEMA);
      logger.info('令牌表结构初始化成功');
    }

    // 创建验证码表(如果不存在)
    if (dbSchema.VERIFICATION_CODES_SCHEMA) {
      await db.raw(dbSchema.VERIFICATION_CODES_SCHEMA);
      logger.info('验证码表结构初始化成功');
    }

    // 创建安全日志表(如果不存在)
    if (dbSchema.SECURITY_LOGS_SCHEMA) {
      await db.raw(dbSchema.SECURITY_LOGS_SCHEMA);
      logger.info('安全日志表结构初始化成功');
    }

    // 创建用户会话表(如果不存在)
    if (dbSchema.USER_SESSIONS_SCHEMA) {
      await db.raw(dbSchema.USER_SESSIONS_SCHEMA);
      logger.info('用户会话表结构初始化成功');
    }

    // 创建二因素认证恢复码表(如果不存在)
    if (dbSchema.TWO_FACTOR_RECOVERY_CODES_SCHEMA) {
      await db.raw(dbSchema.TWO_FACTOR_RECOVERY_CODES_SCHEMA);
      logger.info('二因素认证恢复码表结构初始化成功');
    }

    // 创建用户安全设置表(如果不存在)
    if (dbSchema.USER_SECURITY_SETTINGS_SCHEMA) {
      await db.raw(dbSchema.USER_SECURITY_SETTINGS_SCHEMA);
      logger.info('用户安全设置表结构初始化成功');
    }

    // 创建用户设备表(如果不存在)
    if (dbSchema.USER_DEVICES_SCHEMA) {
      await db.raw(dbSchema.USER_DEVICES_SCHEMA);
      logger.info('用户设备表结构初始化成功');
    }

    // 创建其他表...
    
    logger.info('数据库表结构初始化完成');
  } catch (error) {
    logger.error(`数据库表结构初始化失败: ${error.message}`, { error });
    throw error;
  }
};

/**
 * 检查数据库表是否存在
 * @param {string} tableName 表名
 * @returns {Promise<boolean>} 是否存在
 */
const tableExists = async (tableName) => {
  try {
    const result = await db.raw(
      `SELECT COUNT(*) as count FROM information_schema.tables 
       WHERE table_schema = ? AND table_name = ?`,
      [process.env.MYSQL_DATABASE || 'auth_service', tableName]
    );
    
    return result[0][0].count > 0;
  } catch (error) {
    logger.error(`检查表 ${tableName} 是否存在时出错: ${error.message}`);
    return false;
  }
};

/**
 * 创建数据库索引
 * @param {string} tableName 表名
 * @param {string} columnName 列名
 * @param {string} indexName 索引名
 * @returns {Promise<void>}
 */
const createIndex = async (tableName, columnName, indexName) => {
  try {
    // 检查索引是否已存在
    const indexExists = await db.raw(
      `SELECT COUNT(*) as count FROM information_schema.statistics 
       WHERE table_schema = ? AND table_name = ? AND index_name = ?`,
      [process.env.MYSQL_DATABASE || 'auth_service', tableName, indexName]
    );
    
    if (indexExists[0][0].count === 0) {
      await db.raw(`CREATE INDEX ${indexName} ON ${tableName} (${columnName})`);
      logger.info(`创建索引 ${indexName} 成功`);
    }
  } catch (error) {
    logger.error(`创建索引 ${indexName} 失败: ${error.message}`);
  }
};

module.exports = {
  initDatabase,
  tableExists,
  createIndex
}; 