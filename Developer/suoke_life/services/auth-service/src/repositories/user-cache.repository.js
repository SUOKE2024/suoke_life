/**
 * 带缓存的用户仓库
 */
const knex = require('../config/database');
const cacheService = require('../services/cache.service');
const { logger } = require('@suoke/shared').utils;

// 缓存键前缀
const USER_CACHE_PREFIX = 'user:';
// 缓存时间 (1小时)
const USER_CACHE_TTL = 60 * 60;

/**
 * 创建用户缓存键
 * 
 * @param {string} type - 缓存类型 (id, username, email)
 * @param {string} value - 键值
 * @returns {string} 缓存键
 */
const createUserCacheKey = (type, value) => `${USER_CACHE_PREFIX}${type}:${value}`;

/**
 * 带缓存的用户仓库
 */
const userCacheRepository = {
  /**
   * 根据ID获取用户
   * 
   * @param {string} userId - 用户ID
   * @returns {Promise<Object|null>} 用户对象或null
   */
  async getUserById(userId) {
    try {
      // 尝试从缓存获取
      const cacheKey = createUserCacheKey('id', userId);
      const cachedUser = await cacheService.get(cacheKey);
      
      if (cachedUser) {
        return cachedUser;
      }
      
      // 从数据库获取
      const user = await knex('users')
        .where({ id: userId })
        .select('*')
        .first();
      
      if (user) {
        // 存入缓存
        await cacheService.set(cacheKey, user, USER_CACHE_TTL);
      }
      
      return user || null;
    } catch (error) {
      logger.error(`获取用户失败: ${error.message}`, { userId });
      throw error;
    }
  },
  
  /**
   * 根据用户名获取用户
   * 
   * @param {string} username - 用户名
   * @returns {Promise<Object|null>} 用户对象或null
   */
  async getUserByUsername(username) {
    try {
      // 尝试从缓存获取
      const cacheKey = createUserCacheKey('username', username);
      const cachedUser = await cacheService.get(cacheKey);
      
      if (cachedUser) {
        return cachedUser;
      }
      
      // 从数据库获取 (支持用户名和邮箱登录)
      const user = await knex('users')
        .where({ username })
        .orWhere({ email: username })
        .select('*')
        .first();
      
      if (user) {
        // 存入缓存
        await cacheService.set(cacheKey, user, USER_CACHE_TTL);
        // 同时缓存ID和邮箱键
        await cacheService.set(createUserCacheKey('id', user.id), user, USER_CACHE_TTL);
        await cacheService.set(createUserCacheKey('email', user.email), user, USER_CACHE_TTL);
      }
      
      return user || null;
    } catch (error) {
      logger.error(`获取用户失败: ${error.message}`, { username });
      throw error;
    }
  },
  
  /**
   * 根据邮箱获取用户
   * 
   * @param {string} email - 邮箱
   * @returns {Promise<Object|null>} 用户对象或null
   */
  async getUserByEmail(email) {
    try {
      // 尝试从缓存获取
      const cacheKey = createUserCacheKey('email', email);
      const cachedUser = await cacheService.get(cacheKey);
      
      if (cachedUser) {
        return cachedUser;
      }
      
      // 从数据库获取
      const user = await knex('users')
        .where({ email })
        .select('*')
        .first();
      
      if (user) {
        // 存入缓存
        await cacheService.set(cacheKey, user, USER_CACHE_TTL);
        // 同时缓存ID和用户名键
        await cacheService.set(createUserCacheKey('id', user.id), user, USER_CACHE_TTL);
        await cacheService.set(createUserCacheKey('username', user.username), user, USER_CACHE_TTL);
      }
      
      return user || null;
    } catch (error) {
      logger.error(`获取用户失败: ${error.message}`, { email });
      throw error;
    }
  },
  
  /**
   * 创建用户
   * 
   * @param {Object} userData - 用户数据
   * @returns {Promise<Object>} 创建的用户
   */
  async createUser(userData) {
    const trx = await knex.transaction();
    
    try {
      // 创建用户
      const [userId] = await trx('users')
        .insert({
          ...userData,
          created_at: new Date(),
          updated_at: new Date()
        });
      
      const newUser = await trx('users')
        .where({ id: userId })
        .select('*')
        .first();
      
      await trx.commit();
      
      // 缓存新用户
      await cacheService.set(createUserCacheKey('id', newUser.id), newUser, USER_CACHE_TTL);
      await cacheService.set(createUserCacheKey('username', newUser.username), newUser, USER_CACHE_TTL);
      await cacheService.set(createUserCacheKey('email', newUser.email), newUser, USER_CACHE_TTL);
      
      return newUser;
    } catch (error) {
      await trx.rollback();
      logger.error(`创建用户失败: ${error.message}`, { userData });
      throw error;
    }
  },
  
  /**
   * 更新用户
   * 
   * @param {string} userId - 用户ID
   * @param {Object} userData - 要更新的用户数据
   * @returns {Promise<Object>} 更新后的用户
   */
  async updateUser(userId, userData) {
    const trx = await knex.transaction();
    
    try {
      // 获取旧用户
      const oldUser = await trx('users')
        .where({ id: userId })
        .select('*')
        .first();
      
      if (!oldUser) {
        throw new Error('用户不存在');
      }
      
      // 更新用户
      await trx('users')
        .where({ id: userId })
        .update({
          ...userData,
          updated_at: new Date()
        });
      
      const updatedUser = await trx('users')
        .where({ id: userId })
        .select('*')
        .first();
      
      await trx.commit();
      
      // 删除旧缓存
      await cacheService.del(createUserCacheKey('id', userId));
      await cacheService.del(createUserCacheKey('username', oldUser.username));
      await cacheService.del(createUserCacheKey('email', oldUser.email));
      
      // 设置新缓存
      await cacheService.set(createUserCacheKey('id', updatedUser.id), updatedUser, USER_CACHE_TTL);
      await cacheService.set(createUserCacheKey('username', updatedUser.username), updatedUser, USER_CACHE_TTL);
      await cacheService.set(createUserCacheKey('email', updatedUser.email), updatedUser, USER_CACHE_TTL);
      
      return updatedUser;
    } catch (error) {
      await trx.rollback();
      logger.error(`更新用户失败: ${error.message}`, { userId, userData });
      throw error;
    }
  },
  
  /**
   * 删除用户
   * 
   * @param {string} userId - 用户ID
   * @returns {Promise<boolean>} 是否成功
   */
  async deleteUser(userId) {
    const trx = await knex.transaction();
    
    try {
      // 获取用户
      const user = await trx('users')
        .where({ id: userId })
        .select('*')
        .first();
      
      if (!user) {
        throw new Error('用户不存在');
      }
      
      // 删除用户
      await trx('users')
        .where({ id: userId })
        .del();
      
      await trx.commit();
      
      // 删除缓存
      await cacheService.del(createUserCacheKey('id', userId));
      await cacheService.del(createUserCacheKey('username', user.username));
      await cacheService.del(createUserCacheKey('email', user.email));
      
      return true;
    } catch (error) {
      await trx.rollback();
      logger.error(`删除用户失败: ${error.message}`, { userId });
      throw error;
    }
  },
  
  /**
   * 清除用户缓存
   * 
   * @param {string} userId - 用户ID
   * @returns {Promise<boolean>} 是否成功
   */
  async clearUserCache(userId) {
    try {
      const user = await knex('users')
        .where({ id: userId })
        .select('*')
        .first();
      
      if (user) {
        await cacheService.del(createUserCacheKey('id', userId));
        await cacheService.del(createUserCacheKey('username', user.username));
        await cacheService.del(createUserCacheKey('email', user.email));
      }
      
      return true;
    } catch (error) {
      logger.error(`清除用户缓存失败: ${error.message}`, { userId });
      return false;
    }
  }
};

module.exports = userCacheRepository; 