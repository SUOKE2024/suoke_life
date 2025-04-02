/**
 * 用户数据存储库
 */
const { v4: uuidv4 } = require('uuid');
const { db } = require('../../config/database');
const { logger } = require('@suoke/shared').utils;
const { recordSyncOperation } = require('../../utils/sync');

const TABLE_NAME = 'users';

class UserRepository {
  /**
   * 根据ID查找用户
   * @param {string} id 用户ID
   * @returns {Promise<Object>} 用户数据
   */
  async findById(id) {
    try {
      return await db(TABLE_NAME).where({ id }).first();
    } catch (error) {
      logger.error(`根据ID查找用户失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 根据用户名查找用户
   * @param {string} username 用户名
   * @returns {Promise<Object>} 用户数据
   */
  async findByUsername(username) {
    try {
      return await db(TABLE_NAME).where({ username }).first();
    } catch (error) {
      logger.error(`根据用户名查找用户失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 根据邮箱查找用户
   * @param {string} email 邮箱
   * @returns {Promise<Object>} 用户数据
   */
  async findByEmail(email) {
    try {
      return await db(TABLE_NAME).where({ email }).first();
    } catch (error) {
      logger.error(`根据邮箱查找用户失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 创建新用户
   * @param {Object} userData 用户数据
   * @returns {Promise<Object>} 创建的用户
   */
  async create(userData) {
    try {
      // 确保用户数据包含ID和时间戳
      const newUser = {
        id: userData.id || uuidv4(),
        ...userData,
        created_at: new Date(),
        updated_at: new Date(),
        // 添加数据一致性字段
        data_version: Date.now(),
        last_region: process.env.POD_REGION || 'unknown'
      };
      
      // 插入用户数据
      await db(TABLE_NAME).insert(newUser);
      
      // 记录同步操作
      await recordSyncOperation(TABLE_NAME, 'insert', newUser, newUser.id);
      
      return newUser;
    } catch (error) {
      logger.error(`创建用户失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 更新用户信息
   * @param {string} id 用户ID
   * @param {Object} userData 更新的用户数据
   * @returns {Promise<Object>} 更新后的用户
   */
  async update(id, userData) {
    try {
      // 更新数据，添加一致性字段
      const updateData = {
        ...userData,
        updated_at: new Date(),
        data_version: Date.now(),
        last_region: process.env.POD_REGION || 'unknown'
      };
      
      await db(TABLE_NAME).where({ id }).update(updateData);
      
      // 记录同步操作
      await recordSyncOperation(TABLE_NAME, 'update', updateData, id);
      
      return { id, ...updateData };
    } catch (error) {
      logger.error(`更新用户失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 删除用户
   * @param {string} id 用户ID
   * @returns {Promise<boolean>} 是否成功
   */
  async delete(id) {
    try {
      await db(TABLE_NAME).where({ id }).del();
      
      // 记录同步操作
      await recordSyncOperation(TABLE_NAME, 'delete', { id }, id);
      
      return true;
    } catch (error) {
      logger.error(`删除用户失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 查找满足条件的多个用户
   * @param {Object} filter 过滤条件
   * @param {Object} options 选项（分页等）
   * @returns {Promise<Array>} 用户列表
   */
  async findMany(filter = {}, options = {}) {
    try {
      const { page = 1, pageSize = 20, sortBy = 'created_at', sortOrder = 'desc' } = options;
      
      const query = db(TABLE_NAME)
        .where(filter)
        .orderBy(sortBy, sortOrder)
        .limit(pageSize)
        .offset((page - 1) * pageSize);
      
      const users = await query;
      const total = await db(TABLE_NAME).where(filter).count('id as count').first();
      
      return {
        users,
        pagination: {
          page,
          pageSize,
          total: total ? total.count : 0,
          totalPages: Math.ceil((total ? total.count : 0) / pageSize)
        }
      };
    } catch (error) {
      logger.error(`查找多个用户失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 验证用户凭据
   * @param {string} username 用户名或邮箱
   * @param {string} password 密码
   * @returns {Promise<Object>} 用户数据
   */
  async validateCredentials(username, password) {
    try {
      // 通过用户名或邮箱查找用户
      const user = await db(TABLE_NAME)
        .where(function() {
          this.where('username', username).orWhere('email', username);
        })
        .first();
      
      return user;
    } catch (error) {
      logger.error(`验证用户凭据失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 更新用户最后登录时间
   * @param {string} id 用户ID
   * @returns {Promise<boolean>} 是否成功
   */
  async updateLastLogin(id) {
    try {
      const updateData = {
        last_login_at: new Date(),
        updated_at: new Date(),
        data_version: Date.now(),
        last_region: process.env.POD_REGION || 'unknown'
      };
      
      await db(TABLE_NAME).where({ id }).update(updateData);
      
      // 记录同步操作
      await recordSyncOperation(TABLE_NAME, 'update', updateData, id);
      
      return true;
    } catch (error) {
      logger.error(`更新用户最后登录时间失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 更新用户状态（启用/禁用）
   * @param {string} id 用户ID
   * @param {boolean} isActive 是否启用
   * @returns {Promise<boolean>} 是否成功
   */
  async updateStatus(id, isActive) {
    try {
      const updateData = {
        is_active: isActive,
        updated_at: new Date(),
        data_version: Date.now(),
        last_region: process.env.POD_REGION || 'unknown'
      };
      
      await db(TABLE_NAME).where({ id }).update(updateData);
      
      // 记录同步操作
      await recordSyncOperation(TABLE_NAME, 'update', updateData, id);
      
      return true;
    } catch (error) {
      logger.error(`更新用户状态失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 健康检查
   * @returns {Promise<boolean>} 是否健康
   */
  async healthCheck() {
    try {
      // 执行一个简单的查询检查数据库连接
      await db(TABLE_NAME).select(db.raw('1 as result')).limit(1);
      return true;
    } catch (error) {
      logger.error(`用户存储库健康检查失败: ${error.message}`);
      return false;
    }
  }
}

module.exports = new UserRepository(); 