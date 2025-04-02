/**
 * 用户存储库
 */
const { v4: uuidv4 } = require('uuid');
const { db } = require('../utils/db');
const { redis, getCache, deleteCache, deleteCacheByPattern } = require('../utils/redis');
const { logger } = require('@suoke/shared').utils;
const { userModel } = require('../models');

class UserRepository {
  constructor() {
    this.tableName = userModel.TABLE_NAME;
    this.cacheKeyPrefix = 'user:';
  }

  /**
   * 根据ID获取用户
   */
  async getById(id) {
    try {
      const cacheKey = `${this.cacheKeyPrefix}id:${id}`;
      return getCache(cacheKey, async () => {
        const user = await db(this.tableName).where({ id }).first();
        return user || null;
      });
    } catch (error) {
      logger.error('获取用户失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 根据用户名获取用户
   */
  async getByUsername(username) {
    try {
      const cacheKey = `${this.cacheKeyPrefix}username:${username}`;
      return getCache(cacheKey, async () => {
        const user = await db(this.tableName).where({ username }).first();
        return user || null;
      });
    } catch (error) {
      logger.error('根据用户名获取用户失败', { error: error.message, username });
      throw error;
    }
  }

  /**
   * 根据邮箱获取用户
   */
  async getByEmail(email) {
    try {
      const cacheKey = `${this.cacheKeyPrefix}email:${email}`;
      return getCache(cacheKey, async () => {
        const user = await db(this.tableName).where({ email }).first();
        return user || null;
      });
    } catch (error) {
      logger.error('根据邮箱获取用户失败', { error: error.message, email });
      throw error;
    }
  }

  /**
   * 根据手机号获取用户
   */
  async getByPhone(phone) {
    try {
      const cacheKey = `${this.cacheKeyPrefix}phone:${phone}`;
      return getCache(cacheKey, async () => {
        const user = await db(this.tableName).where({ phone }).first();
        return user || null;
      });
    } catch (error) {
      logger.error('根据手机号获取用户失败', { error: error.message, phone });
      throw error;
    }
  }

  /**
   * 创建用户
   */
  async create(userData) {
    try {
      const now = new Date();
      const user = {
        id: uuidv4(),
        ...userData,
        created_at: now,
        updated_at: now
      };

      await db(this.tableName).insert(user);
      
      // 清除缓存
      await this.clearUserCache(user);
      
      return user;
    } catch (error) {
      logger.error('创建用户失败', { error: error.message, userData });
      throw error;
    }
  }

  /**
   * 更新用户
   */
  async update(id, userData) {
    try {
      const now = new Date();
      const updateData = {
        ...userData,
        updated_at: now
      };

      await db(this.tableName).where({ id }).update(updateData);
      
      // 清除缓存
      await this.clearUserCache({ id, ...userData });
      
      return this.getById(id);
    } catch (error) {
      logger.error('更新用户失败', { error: error.message, id, userData });
      throw error;
    }
  }

  /**
   * 删除用户
   */
  async delete(id) {
    try {
      const user = await this.getById(id);
      
      if (!user) {
        return false;
      }
      
      await db(this.tableName).where({ id }).del();
      
      // 清除缓存
      await this.clearUserCache(user);
      
      return true;
    } catch (error) {
      logger.error('删除用户失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 获取分页用户列表
   */
  async list(page = 1, pageSize = 10, filters = {}) {
    try {
      const offset = (page - 1) * pageSize;
      
      const query = db(this.tableName);
      
      // 应用过滤条件
      if (filters.role) {
        query.where('role', filters.role);
      }
      
      if (filters.status) {
        query.where('status', filters.status);
      }
      
      if (filters.verified !== undefined) {
        query.where('verified', filters.verified);
      }
      
      // 获取总数
      const countQuery = query.clone();
      const totalItems = await countQuery.count('id as count').first();
      
      // 获取分页数据
      const users = await query
        .select('*')
        .orderBy('created_at', 'desc')
        .offset(offset)
        .limit(pageSize);
      
      return {
        data: users,
        pagination: {
          page,
          pageSize,
          totalItems: totalItems ? totalItems.count : 0,
          totalPages: Math.ceil((totalItems ? totalItems.count : 0) / pageSize)
        }
      };
    } catch (error) {
      logger.error('获取用户列表失败', { error: error.message, page, pageSize, filters });
      throw error;
    }
  }

  /**
   * 更新用户最后登录时间
   */
  async updateLastLogin(id) {
    try {
      const now = new Date();
      await db(this.tableName).where({ id }).update({ last_login: now, updated_at: now });
      
      // 清除缓存
      await deleteCache(`${this.cacheKeyPrefix}id:${id}`);
      
      return true;
    } catch (error) {
      logger.error('更新用户最后登录时间失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 验证用户
   */
  async verifyUser(id) {
    try {
      await db(this.tableName).where({ id }).update({
        verified: true,
        status: 'active',
        verification_token: null,
        verification_expires: null,
        updated_at: new Date()
      });
      
      // 清除缓存
      await deleteCache(`${this.cacheKeyPrefix}id:${id}`);
      
      return this.getById(id);
    } catch (error) {
      logger.error('验证用户失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 更新验证令牌
   */
  async updateVerificationToken(id, token, expiresIn = 86400) {
    try {
      const now = new Date();
      const expiresAt = new Date(now.getTime() + expiresIn * 1000);
      
      await db(this.tableName).where({ id }).update({
        verification_token: token,
        verification_expires: expiresAt,
        updated_at: now
      });
      
      // 清除缓存
      await deleteCache(`${this.cacheKeyPrefix}id:${id}`);
      
      return true;
    } catch (error) {
      logger.error('更新验证令牌失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 检查验证令牌
   */
  async checkVerificationToken(token) {
    try {
      const now = new Date();
      
      const user = await db(this.tableName)
        .where({ verification_token: token })
        .where('verification_expires', '>', now)
        .first();
      
      return user || null;
    } catch (error) {
      logger.error('检查验证令牌失败', { error: error.message, token });
      throw error;
    }
  }

  /**
   * 清除用户相关缓存
   */
  async clearUserCache(user) {
    try {
      if (!user) return;
      
      const cacheKeys = [];
      
      if (user.id) {
        cacheKeys.push(`${this.cacheKeyPrefix}id:${user.id}`);
      }
      
      if (user.username) {
        cacheKeys.push(`${this.cacheKeyPrefix}username:${user.username}`);
      }
      
      if (user.email) {
        cacheKeys.push(`${this.cacheKeyPrefix}email:${user.email}`);
      }
      
      if (user.phone) {
        cacheKeys.push(`${this.cacheKeyPrefix}phone:${user.phone}`);
      }
      
      if (cacheKeys.length > 0) {
        await Promise.all(cacheKeys.map(key => deleteCache(key)));
      }
      
      // 清除包含用户ID的所有缓存
      if (user.id) {
        await deleteCacheByPattern(`*:${user.id}:*`);
      }
      
      return true;
    } catch (error) {
      logger.error('清除用户缓存失败', { error: error.message, user });
      return false;
    }
  }
}

module.exports = new UserRepository(); 