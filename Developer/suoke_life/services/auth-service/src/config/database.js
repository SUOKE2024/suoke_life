/**
 * 数据库配置文件
 */
const knex = require('knex');
const { logger } = require('@suoke/shared').utils;
const config = require('./index');

// 数据库连接实例
let dbInstance = null;

/**
 * 创建数据库连接
 * @returns {Promise<Object>} Knex数据库实例
 */
const connectDatabase = async () => {
  if (dbInstance) {
    return dbInstance;
  }
  
  try {
    // 从环境变量获取数据库配置
    const dbConfig = {
      client: 'mysql2',
      connection: {
        host: config.database.host,
        port: config.database.port,
        user: config.database.user,
        password: config.database.password,
        database: config.database.name,
        charset: 'utf8mb4',
        timezone: '+08:00',
        dateStrings: true
      },
      pool: {
        min: 2,
        max: 10,
        idleTimeoutMillis: 30000,
        createTimeoutMillis: 30000,
        acquireTimeoutMillis: 30000,
        createRetryIntervalMillis: 200,
        propagateCreateError: false, // 连接错误不会导致整个池失效
        afterCreate: (conn, done) => {
          // 设置连接变量
          conn.query('SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED', (err) => {
            if (err) {
              logger.error(`设置数据库连接参数失败: ${err.message}`);
            }
            done(err, conn);
          });
        }
      },
      migrations: {
        tableName: 'knex_migrations',
        directory: './src/models/migrations'
      },
      seeds: {
        directory: './src/models/seeds'
      },
      debug: process.env.NODE_ENV === 'development'
    };
    
    // 创建数据库实例
    dbInstance = knex(dbConfig);
    
    // 测试连接
    await dbInstance.raw('SELECT 1');
    logger.info('数据库连接成功');
    
    // 注册连接错误处理
    dbInstance.on('query-error', (error, { sql, bindings }) => {
      const query = sql.replace(/\?/g, () => bindings.shift());
      logger.error(`数据库查询错误: ${error.message} - 查询: ${query}`);
    });
    
    return dbInstance;
  } catch (error) {
    logger.error(`数据库连接失败: ${error.message}`);
    throw error;
  }
};

/**
 * 获取数据库实例，如果不存在则创建
 * @returns {Object} Knex数据库实例
 */
const getDatabase = () => {
  if (!dbInstance) {
    logger.warn('尝试在连接建立前获取数据库实例');
    // 初始化连接但不等待
    connectDatabase().catch(err => {
      logger.error(`延迟数据库连接失败: ${err.message}`);
    });
  }
  return dbInstance;
};

/**
 * 关闭数据库连接
 * @returns {Promise<void>}
 */
const closeDatabase = async () => {
  if (dbInstance) {
    try {
      await dbInstance.destroy();
      logger.info('数据库连接已关闭');
      dbInstance = null;
    } catch (error) {
      logger.error(`关闭数据库连接失败: ${error.message}`);
      throw error;
    }
  }
};

/**
 * 数据库健康检查
 * @returns {Promise<boolean>}
 */
const healthCheck = async () => {
  try {
    if (!dbInstance) {
      return false;
    }
    await dbInstance.raw('SELECT 1');
    return true;
  } catch (error) {
    logger.error(`数据库健康检查失败: ${error.message}`);
    return false;
  }
};

/**
 * 运行数据库迁移
 * @returns {Promise<void>}
 */
const runMigrations = async () => {
  try {
    if (!dbInstance) {
      await connectDatabase();
    }
    logger.info('开始运行数据库迁移...');
    await dbInstance.migrate.latest();
    logger.info('数据库迁移完成');
  } catch (error) {
    logger.error(`数据库迁移失败: ${error.message}`);
    throw error;
  }
};

/**
 * 添加数据一致性检查时间戳
 * 用于跨区域同步
 * @param {Object} queryBuilder Knex查询构建器
 * @param {string} type 操作类型 ('insert', 'update', 'delete')
 * @returns {Object} 修改后的查询构建器
 */
const addDataConsistencyFields = (queryBuilder, type = 'insert') => {
  const now = new Date();
  const region = process.env.POD_REGION || 'unknown';
  
  if (type === 'insert') {
    queryBuilder.returning('*');
    
    // 添加数据一致性及创建/更新字段
    const originalInsert = queryBuilder.insert;
    queryBuilder.insert = function(...args) {
      const data = args[0];
      
      // 对单个对象或对象数组处理
      if (Array.isArray(data)) {
        data.forEach(item => {
          item.created_at = item.created_at || now;
          item.updated_at = item.updated_at || now;
          item.source_region = region;
          item.data_version = Date.now();
        });
      } else if (data) {
        data.created_at = data.created_at || now;
        data.updated_at = data.updated_at || now;
        data.source_region = region;
        data.data_version = Date.now();
      }
      
      return originalInsert.apply(this, args);
    };
  } else if (type === 'update') {
    queryBuilder.returning('*');
    
    // 添加更新时间和一致性字段
    const originalUpdate = queryBuilder.update;
    queryBuilder.update = function(...args) {
      const data = args[0];
      
      if (data) {
        data.updated_at = now;
        data.source_region = region;
        data.data_version = Date.now();
      }
      
      return originalUpdate.apply(this, args);
    };
  }
  
  return queryBuilder;
};

// 导出实例
module.exports = { db: getDatabase() };

// 导出其他函数
module.exports.connectDatabase = connectDatabase;
module.exports.getDatabase = getDatabase;
module.exports.closeDatabase = closeDatabase;
module.exports.healthCheck = healthCheck;
module.exports.runMigrations = runMigrations;
module.exports.addDataConsistencyFields = addDataConsistencyFields; 