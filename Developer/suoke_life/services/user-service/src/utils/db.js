/**
 * 数据库工具模块
 * 提供数据库连接池管理和查询功能
 */
const mysql = require('mysql2/promise');
const { v4: uuidv4 } = require('uuid');
const config = require('../config');
const { logger } = require('./logger');
const { encrypt, decrypt } = require('./encryption');

// 数据库连接池
let pool = null;

/**
 * 初始化数据库连接池
 * @returns {Promise<void>}
 */
const init = async () => {
  try {
    pool = mysql.createPool({
      host: config.database.host,
      port: config.database.port,
      user: config.database.user,
      password: config.database.password,
      database: config.database.name,
      waitForConnections: true,
      connectionLimit: config.database.connectionLimit || 10,
      queueLimit: 0,
      timezone: '+08:00',
      charset: 'utf8mb4'
    });
    
    // 测试连接
    const connection = await pool.getConnection();
    connection.release();
    
    logger.info('数据库连接池初始化成功');
  } catch (error) {
    logger.error('数据库连接池初始化失败', { error: error.message });
    throw error;
  }
};

/**
 * 检查数据库连接是否已初始化
 * @returns {boolean} 是否已初始化
 */
const isInitialized = () => {
  try {
    return !!pool && pool.pool && pool.pool.pool && pool.pool.pool._closed === false;
  } catch (error) {
    logger.error('检查数据库初始化状态时出错:', error);
    return false;
  }
};

/**
 * 关闭数据库连接池
 * @returns {Promise<void>}
 */
const close = async () => {
  try {
    if (pool) {
      logger.info('正在关闭数据库连接池...');
      await pool.end();
      logger.info('数据库连接池已关闭');
    }
  } catch (error) {
    logger.error('关闭数据库连接时出错:', error);
    throw error;
  }
};

/**
 * 执行SQL查询
 * @param {string} sql - SQL查询语句
 * @param {Array} params - 查询参数
 * @returns {Promise<Array>} - 查询结果
 */
const query = async (sql, params = []) => {
  if (!pool) {
    await init();
  }
  
  try {
    const [rows] = await pool.execute(sql, params);
    return rows;
  } catch (error) {
    logger.error('SQL查询执行失败', { 
      error: error.message,
      sql: sql.substring(0, 200), // 记录部分SQL以便调试
      params: JSON.stringify(params).substring(0, 200)
    });
    throw error;
  }
};

/**
 * 执行事务
 * @param {Function} callback - 事务回调函数，接收connection参数
 * @returns {Promise<any>} - 事务执行结果
 */
const transaction = async (callback) => {
  if (!pool) {
    await init();
  }
  
  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();
    const result = await callback(connection);
    await connection.commit();
    return result;
  } catch (error) {
    await connection.rollback();
    logger.error('事务执行失败', { error: error.message });
    throw error;
  } finally {
    connection.release();
  }
};

/**
 * 插入记录
 * @param {string} table - 表名
 * @param {Object} data - 要插入的数据
 * @param {Array<string>} encryptFields - 需要加密的字段
 * @returns {Promise<string>} - 插入记录的ID
 */
const insert = async (table, data, encryptFields = []) => {
  // 生成UUID
  const id = data.id || uuidv4();
  const insertData = { ...data, id };
  
  // 加密敏感字段
  for (const field of encryptFields) {
    if (insertData[field]) {
      insertData[field] = await encrypt(insertData[field]);
    }
  }
  
  // 添加时间戳
  if (!insertData.created_at) {
    insertData.created_at = new Date();
  }
  if (!insertData.updated_at) {
    insertData.updated_at = new Date();
  }
  
  const keys = Object.keys(insertData);
  const values = Object.values(insertData);
  const placeholders = keys.map(() => '?').join(', ');
  
  const sql = `INSERT INTO ${table} (${keys.join(', ')}) VALUES (${placeholders})`;
  
  await query(sql, values);
  return id;
};

/**
 * 更新记录
 * @param {string} table - 表名
 * @param {string} id - 记录ID
 * @param {Object} data - 要更新的数据
 * @param {Array<string>} encryptFields - 需要加密的字段
 * @returns {Promise<boolean>} - 更新是否成功
 */
const update = async (table, id, data, encryptFields = []) => {
  const updateData = { ...data, updated_at: new Date() };
  
  // 加密敏感字段
  for (const field of encryptFields) {
    if (updateData[field]) {
      updateData[field] = await encrypt(updateData[field]);
    }
  }
  
  // 移除不可更新的字段
  delete updateData.id;
  delete updateData.created_at;
  
  if (Object.keys(updateData).length === 0) {
    return false;
  }
  
  const setClause = Object.keys(updateData)
    .map(key => `${key} = ?`)
    .join(', ');
  
  const values = [...Object.values(updateData), id];
  
  const sql = `UPDATE ${table} SET ${setClause} WHERE id = ?`;
  
  const result = await query(sql, values);
  return result.affectedRows > 0;
};

/**
 * 查找记录
 * @param {string} table - 表名
 * @param {Object} conditions - 查询条件
 * @param {Array<string>} decryptFields - 需要解密的字段
 * @returns {Promise<Array>} - 查询结果
 */
const find = async (table, conditions = {}, decryptFields = []) => {
  const keys = Object.keys(conditions);
  let whereClause = '';
  let values = [];
  
  if (keys.length > 0) {
    whereClause = 'WHERE ' + keys.map(key => `${key} = ?`).join(' AND ');
    values = Object.values(conditions);
  }
  
  const sql = `SELECT * FROM ${table} ${whereClause}`;
  
  const results = await query(sql, values);
  
  // 解密敏感字段
  if (decryptFields.length > 0 && results.length > 0) {
    for (const result of results) {
      for (const field of decryptFields) {
        if (result[field]) {
          result[field] = await decrypt(result[field]);
        }
      }
    }
  }
  
  return results;
};

/**
 * 查找单条记录
 * @param {string} table - 表名
 * @param {Object} conditions - 查询条件
 * @param {Array<string>} decryptFields - 需要解密的字段
 * @returns {Promise<Object|null>} - 查询结果
 */
const findOne = async (table, conditions = {}, decryptFields = []) => {
  const results = await find(table, conditions, decryptFields);
  return results.length > 0 ? results[0] : null;
};

/**
 * 删除记录
 * @param {string} table - 表名
 * @param {string} id - 记录ID
 * @returns {Promise<boolean>} - 删除是否成功
 */
const remove = async (table, id) => {
  const sql = `DELETE FROM ${table} WHERE id = ?`;
  const result = await query(sql, [id]);
  return result.affectedRows > 0;
};

/**
 * 分页查询
 * @param {string} table - 表名
 * @param {Object} conditions - 查询条件
 * @param {number} page - 页码
 * @param {number} pageSize - 每页记录数
 * @param {string} orderBy - 排序字段
 * @param {string} order - 排序方向
 * @param {Array<string>} decryptFields - 需要解密的字段
 * @returns {Promise<Object>} - 分页结果
 */
const paginate = async (
  table, 
  conditions = {}, 
  page = 1, 
  pageSize = 10, 
  orderBy = 'created_at', 
  order = 'DESC',
  decryptFields = []
) => {
  const keys = Object.keys(conditions);
  let whereClause = '';
  let values = [];
  
  if (keys.length > 0) {
    whereClause = 'WHERE ' + keys.map(key => `${key} = ?`).join(' AND ');
    values = Object.values(conditions);
  }
  
  // 计算总记录数
  const countSql = `SELECT COUNT(*) as total FROM ${table} ${whereClause}`;
  const countResult = await query(countSql, values);
  const total = countResult[0].total;
  
  // 计算总页数
  const totalPages = Math.ceil(total / pageSize);
  
  // 计算偏移量
  const offset = (page - 1) * pageSize;
  
  // 查询数据
  const dataSql = `
    SELECT * FROM ${table} 
    ${whereClause} 
    ORDER BY ${orderBy} ${order} 
    LIMIT ? OFFSET ?
  `;
  
  const dataValues = [...values, pageSize, offset];
  const data = await query(dataSql, dataValues);
  
  // 解密敏感字段
  if (decryptFields.length > 0 && data.length > 0) {
    for (const item of data) {
      for (const field of decryptFields) {
        if (item[field]) {
          item[field] = await decrypt(item[field]);
        }
      }
    }
  }
  
  return {
    data,
    pagination: {
      total,
      totalPages,
      currentPage: page,
      pageSize
    }
  };
};

module.exports = {
  init,
  isInitialized,
  close,
  query,
  transaction,
  insert,
  update,
  find,
  findOne,
  remove,
  paginate
}; 