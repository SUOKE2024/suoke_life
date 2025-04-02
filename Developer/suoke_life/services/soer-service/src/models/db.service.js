/**
 * 数据库服务
 * 提供数据库连接池管理和基本数据库操作功能
 */
const mysql = require('mysql2/promise');
const { v4: uuidv4 } = require('uuid');
const config = require('../config');
const { logger } = require('../utils/logger');

/**
 * 数据库服务类
 */
class DbService {
  constructor() {
    this.pool = null;
    this.initialized = false;
  }

  /**
   * 连接数据库
   * @returns {Promise<void>}
   */
  async connect() {
    try {
      if (this.initialized && this.pool) {
        logger.info('数据库连接池已初始化，无需重复连接');
        return;
      }

      this.pool = mysql.createPool({
        host: config.database?.host || 'localhost',
        port: config.database?.port || 3306,
        user: config.database?.user || 'root',
        password: config.database?.password || '',
        database: config.database?.name || 'suoke_soer',
        waitForConnections: true,
        connectionLimit: config.database?.connectionLimit || 10,
        queueLimit: 0,
        timezone: '+08:00',
        charset: 'utf8mb4',
        namedPlaceholders: true
      });

      // 测试连接
      const connection = await this.pool.getConnection();
      connection.release();

      this.initialized = true;
      logger.info('数据库连接池初始化成功');
    } catch (error) {
      logger.error('数据库连接池初始化失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 断开数据库连接
   * @returns {Promise<void>}
   */
  async disconnect() {
    try {
      if (this.pool) {
        await this.pool.end();
        this.pool = null;
        this.initialized = false;
        logger.info('数据库连接池已关闭');
      }
    } catch (error) {
      logger.error('关闭数据库连接时出错:', { error: error.message });
      throw error;
    }
  }

  /**
   * 执行SQL查询
   * @param {string} sql - SQL查询语句
   * @param {Array|Object} params - 查询参数
   * @returns {Promise<Array>} - 查询结果
   */
  async query(sql, params = []) {
    if (!this.initialized || !this.pool) {
      await this.connect();
    }

    try {
      const [rows] = await this.pool.execute(sql, params);
      return rows;
    } catch (error) {
      logger.error('SQL查询执行失败', {
        error: error.message,
        sql: sql.substring(0, 200), // 记录部分SQL以便调试
        params: JSON.stringify(params).substring(0, 200)
      });
      throw error;
    }
  }

  /**
   * 根据ID获取记录
   * @param {string} table - 表名
   * @param {string} id - 记录ID
   * @returns {Promise<Object|null>} - 记录对象，不存在则返回null
   */
  async getById(table, id) {
    try {
      const sql = `SELECT * FROM ${table} WHERE id = ?`;
      const results = await this.query(sql, [id]);
      return results.length > 0 ? results[0] : null;
    } catch (error) {
      logger.error(`获取记录失败: ${table}`, { id, error: error.message });
      throw error;
    }
  }

  /**
   * 创建新记录
   * @param {string} table - 表名
   * @param {Object} data - 记录数据
   * @returns {Promise<Object>} - 创建的记录对象
   */
  async create(table, data) {
    try {
      // 生成UUID作为主键
      if (!data.id) {
        data.id = uuidv4();
      }

      // 添加创建和更新时间
      const now = new Date();
      if (!data.created_at) {
        data.created_at = now;
      }
      if (!data.updated_at) {
        data.updated_at = now;
      }

      const keys = Object.keys(data);
      const placeholders = keys.map(() => '?').join(', ');
      const values = Object.values(data);

      const sql = `INSERT INTO ${table} (${keys.join(', ')}) VALUES (${placeholders})`;
      await this.query(sql, values);

      return data;
    } catch (error) {
      logger.error(`创建记录失败: ${table}`, { data, error: error.message });
      throw error;
    }
  }

  /**
   * 更新记录
   * @param {string} table - 表名
   * @param {string} id - 记录ID
   * @param {Object} data - 更新数据
   * @returns {Promise<Object>} - 更新后的记录对象
   */
  async update(table, id, data) {
    try {
      // 添加更新时间
      data.updated_at = new Date();

      const updates = Object.entries(data)
        .map(([key]) => `${key} = ?`)
        .join(', ');
      const values = [...Object.values(data), id];

      const sql = `UPDATE ${table} SET ${updates} WHERE id = ?`;
      await this.query(sql, values);

      return { id, ...data };
    } catch (error) {
      logger.error(`更新记录失败: ${table}`, { id, data, error: error.message });
      throw error;
    }
  }

  /**
   * 删除记录
   * @param {string} table - 表名
   * @param {string} id - 记录ID
   * @returns {Promise<boolean>} - 删除成功返回true，记录不存在返回false
   */
  async delete(table, id) {
    try {
      const sql = `DELETE FROM ${table} WHERE id = ?`;
      const result = await this.query(sql, [id]);
      return result.affectedRows > 0;
    } catch (error) {
      logger.error(`删除记录失败: ${table}`, { id, error: error.message });
      throw error;
    }
  }

  /**
   * 查询符合条件的记录
   * @param {string} table - 表名
   * @param {Object} conditions - 查询条件
   * @param {Object} options - 查询选项，如排序、分页等
   * @returns {Promise<Array>} - 记录数组
   */
  async find(table, conditions = {}, options = {}) {
    try {
      const { sort, limit, offset } = options;
      
      // 构建WHERE条件
      const whereConditions = Object.keys(conditions).length > 0
        ? 'WHERE ' + Object.keys(conditions)
            .map(key => `${key} = ?`)
            .join(' AND ')
        : '';
      
      // 构建ORDER BY条件
      const orderBy = sort
        ? `ORDER BY ${Array.isArray(sort) ? sort.join(', ') : sort}`
        : '';
      
      // 构建LIMIT和OFFSET条件
      const limitClause = limit ? `LIMIT ${parseInt(limit)}` : '';
      const offsetClause = offset ? `OFFSET ${parseInt(offset)}` : '';
      
      const sql = `
        SELECT * FROM ${table}
        ${whereConditions}
        ${orderBy}
        ${limitClause}
        ${offsetClause}
      `;
      
      const values = Object.values(conditions);
      
      return await this.query(sql, values);
    } catch (error) {
      logger.error(`查询记录失败: ${table}`, { 
        conditions, 
        options, 
        error: error.message 
      });
      throw error;
    }
  }

  /**
   * 批量创建记录
   * @param {string} table - 表名
   * @param {Array<Object>} records - 记录数组
   * @returns {Promise<Array<Object>>} - 创建的记录数组
   */
  async bulkCreate(table, records) {
    try {
      if (!Array.isArray(records) || records.length === 0) {
        return [];
      }
      
      const now = new Date();
      
      // 为所有记录添加ID和时间戳
      const processedRecords = records.map(record => {
        const newRecord = { ...record };
        if (!newRecord.id) {
          newRecord.id = uuidv4();
        }
        if (!newRecord.created_at) {
          newRecord.created_at = now;
        }
        if (!newRecord.updated_at) {
          newRecord.updated_at = now;
        }
        return newRecord;
      });
      
      // 准备批量插入
      const keys = Object.keys(processedRecords[0]);
      const placeholders = processedRecords
        .map(() => `(${keys.map(() => '?').join(', ')})`)
        .join(', ');
      
      // 展平所有值到一个数组
      const values = processedRecords.flatMap(record => 
        keys.map(key => record[key])
      );
      
      const sql = `INSERT INTO ${table} (${keys.join(', ')}) VALUES ${placeholders}`;
      await this.query(sql, values);
      
      return processedRecords;
    } catch (error) {
      logger.error(`批量创建记录失败: ${table}`, { 
        recordCount: records.length, 
        error: error.message 
      });
      throw error;
    }
  }

  /**
   * 在事务中执行操作
   * @param {Function} callback - 回调函数，接收connection参数
   * @returns {Promise<any>} - 事务执行结果
   */
  async transaction(callback) {
    if (!this.initialized || !this.pool) {
      await this.connect();
    }
    
    const connection = await this.pool.getConnection();
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
  }
}

// 创建实例
const dbService = new DbService();

module.exports = dbService; 