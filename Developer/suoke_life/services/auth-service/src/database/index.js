/**
 * 数据库模块
 */
const mysql = require('mysql2/promise');
const config = require('../config');
const logger = require('../utils/logger');

// 连接池
let pool;

/**
 * 初始化数据库连接池
 */
const initializePool = () => {
  try {
    if (!pool) {
      pool = mysql.createPool({
        host: config.database?.host || 'localhost',
        port: config.database?.port || 3306,
        user: config.database?.user || 'root',
        password: config.database?.password || '',
        database: config.database?.name || 'suoke_auth',
        waitForConnections: true,
        connectionLimit: 10,
        queueLimit: 0,
        namedPlaceholders: true
      });
      
      logger.info('数据库连接池初始化成功');
    }
    return pool;
  } catch (error) {
    logger.error('数据库连接池初始化失败', error);
    throw error;
  }
};

/**
 * 获取数据库连接池
 * @returns {Pool} 数据库连接池
 */
const getPool = () => {
  if (!pool) {
    return initializePool();
  }
  return pool;
};

/**
 * 执行SQL查询
 * @param {string} sql - SQL查询语句
 * @param {Object|Array} params - 查询参数
 * @returns {Promise<Array>} 查询结果
 */
const query = async (sql, params = {}) => {
  try {
    const connection = await getPool().getConnection();
    try {
      const [rows] = await connection.query(sql, params);
      return rows;
    } finally {
      connection.release();
    }
  } catch (error) {
    logger.error(`SQL查询失败: ${sql}`, error);
    throw error;
  }
};

/**
 * 在事务中执行操作
 * @param {Function} callback - 事务回调函数
 * @returns {Promise<any>} 事务结果
 */
const transaction = async (callback) => {
  const connection = await getPool().getConnection();
  await connection.beginTransaction();
  
  try {
    const result = await callback({
      query: async (sql, params = {}) => {
        const [rows] = await connection.query(sql, params);
        return rows;
      }
    });
    
    await connection.commit();
    return result;
  } catch (error) {
    await connection.rollback();
    logger.error('事务执行失败', error);
    throw error;
  } finally {
    connection.release();
  }
};

/**
 * 关闭数据库连接池
 */
const closePool = async () => {
  if (pool) {
    await pool.end();
    pool = null;
    logger.info('数据库连接池已关闭');
  }
};

module.exports = {
  getPool,
  query,
  transaction,
  closePool,
  initializePool
}; 