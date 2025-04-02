/**
 * 用户资料存储库
 */
const { v4: uuidv4 } = require('uuid');
const { db } = require('../utils/db');
const { getCache, deleteCache, deleteCacheByPattern } = require('../utils/redis');
const { logger } = require('@suoke/shared').utils;
const { profileModel } = require('../models');

class ProfileRepository {
  constructor() {
    this.tableName = profileModel.TABLE_NAME;
    this.cacheKeyPrefix = 'profile:';
  }

  /**
   * 根据ID获取用户资料
   */
  async getById(id) {
    try {
      const cacheKey = `${this.cacheKeyPrefix}id:${id}`;
      return getCache(cacheKey, async () => {
        const profile = await db(this.tableName).where({ id }).first();
        return profile || null;
      });
    } catch (error) {
      logger.error('获取用户资料失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 根据用户ID获取用户资料
   */
  async getByUserId(userId) {
    try {
      const cacheKey = `${this.cacheKeyPrefix}user:${userId}`;
      return getCache(cacheKey, async () => {
        const profile = await db(this.tableName).where({ user_id: userId }).first();
        return profile || null;
      });
    } catch (error) {
      logger.error('根据用户ID获取资料失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 创建用户资料
   */
  async create(profileData) {
    try {
      const now = new Date();
      const profile = {
        id: uuidv4(),
        ...profileData,
        created_at: now,
        updated_at: now
      };

      await db(this.tableName).insert(profile);
      
      // 清除缓存
      await this.clearProfileCache(profile);
      
      return profile;
    } catch (error) {
      logger.error('创建用户资料失败', { error: error.message, profileData });
      throw error;
    }
  }

  /**
   * 更新用户资料
   */
  async update(id, profileData) {
    try {
      const profile = await this.getById(id);
      
      if (!profile) {
        throw new Error('用户资料不存在');
      }
      
      const now = new Date();
      const updateData = {
        ...profileData,
        updated_at: now
      };

      await db(this.tableName).where({ id }).update(updateData);
      
      // 清除缓存
      await this.clearProfileCache({ ...profile, ...updateData });
      
      return this.getById(id);
    } catch (error) {
      logger.error('更新用户资料失败', { error: error.message, id, profileData });
      throw error;
    }
  }

  /**
   * 根据用户ID更新用户资料
   */
  async updateByUserId(userId, profileData) {
    try {
      const profile = await this.getByUserId(userId);
      
      if (!profile) {
        throw new Error('用户资料不存在');
      }
      
      return this.update(profile.id, profileData);
    } catch (error) {
      logger.error('根据用户ID更新资料失败', { error: error.message, userId, profileData });
      throw error;
    }
  }

  /**
   * 删除用户资料
   */
  async delete(id) {
    try {
      const profile = await this.getById(id);
      
      if (!profile) {
        return false;
      }
      
      await db(this.tableName).where({ id }).del();
      
      // 清除缓存
      await this.clearProfileCache(profile);
      
      return true;
    } catch (error) {
      logger.error('删除用户资料失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 根据用户ID删除用户资料
   */
  async deleteByUserId(userId) {
    try {
      const profile = await this.getByUserId(userId);
      
      if (!profile) {
        return false;
      }
      
      return this.delete(profile.id);
    } catch (error) {
      logger.error('根据用户ID删除资料失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 搜索用户资料
   */
  async search(query, page = 1, pageSize = 10) {
    try {
      const offset = (page - 1) * pageSize;
      
      const dbQuery = db(this.tableName)
        .whereRaw('LOWER(nickname) LIKE ?', [`%${query.toLowerCase()}%`])
        .orWhereRaw('LOWER(location) LIKE ?', [`%${query.toLowerCase()}%`])
        .orWhereRaw('LOWER(profession) LIKE ?', [`%${query.toLowerCase()}%`]);
      
      // 获取总数
      const countQuery = dbQuery.clone();
      const totalItems = await countQuery.count('id as count').first();
      
      // 获取分页数据
      const profiles = await dbQuery
        .select('*')
        .orderBy('updated_at', 'desc')
        .offset(offset)
        .limit(pageSize);
      
      return {
        data: profiles,
        pagination: {
          page,
          pageSize,
          totalItems: totalItems ? totalItems.count : 0,
          totalPages: Math.ceil((totalItems ? totalItems.count : 0) / pageSize)
        }
      };
    } catch (error) {
      logger.error('搜索用户资料失败', { error: error.message, query, page, pageSize });
      throw error;
    }
  }

  /**
   * 清除用户资料相关缓存
   */
  async clearProfileCache(profile) {
    try {
      if (!profile) return;
      
      const cacheKeys = [];
      
      if (profile.id) {
        cacheKeys.push(`${this.cacheKeyPrefix}id:${profile.id}`);
      }
      
      if (profile.user_id) {
        cacheKeys.push(`${this.cacheKeyPrefix}user:${profile.user_id}`);
      }
      
      if (cacheKeys.length > 0) {
        await Promise.all(cacheKeys.map(key => deleteCache(key)));
      }
      
      return true;
    } catch (error) {
      logger.error('清除用户资料缓存失败', { error: error.message, profile });
      return false;
    }
  }
}

module.exports = new ProfileRepository(); 