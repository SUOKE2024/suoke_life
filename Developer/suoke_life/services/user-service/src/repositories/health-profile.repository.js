/**
 * 健康资料存储库
 */
const { v4: uuidv4 } = require('uuid');
const { db } = require('../utils/db');
const { getCache, deleteCache, deleteCacheByPattern } = require('../utils/redis');
const { logger } = require('@suoke/shared').utils;
const { healthProfileModel } = require('../models');

class HealthProfileRepository {
  constructor() {
    this.tableName = healthProfileModel.TABLE_NAME;
    this.cacheKeyPrefix = 'health_profile:';
  }

  /**
   * 根据ID获取健康资料
   */
  async getById(id) {
    try {
      const cacheKey = `${this.cacheKeyPrefix}id:${id}`;
      return getCache(cacheKey, async () => {
        const healthProfile = await db(this.tableName).where({ id }).first();
        return healthProfile || null;
      });
    } catch (error) {
      logger.error('获取健康资料失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 根据用户ID获取健康资料
   */
  async getByUserId(userId) {
    try {
      const cacheKey = `${this.cacheKeyPrefix}user:${userId}`;
      return getCache(cacheKey, async () => {
        const healthProfile = await db(this.tableName).where({ user_id: userId }).first();
        return healthProfile || null;
      });
    } catch (error) {
      logger.error('根据用户ID获取健康资料失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 创建健康资料
   */
  async create(healthProfileData) {
    try {
      const now = new Date();
      const healthProfile = {
        id: uuidv4(),
        ...healthProfileData,
        created_at: now,
        updated_at: now
      };

      await db(this.tableName).insert(healthProfile);
      
      // 清除缓存
      await this.clearHealthProfileCache(healthProfile);
      
      return healthProfile;
    } catch (error) {
      logger.error('创建健康资料失败', { error: error.message, healthProfileData });
      throw error;
    }
  }

  /**
   * 更新健康资料
   */
  async update(id, healthProfileData) {
    try {
      const healthProfile = await this.getById(id);
      
      if (!healthProfile) {
        throw new Error('健康资料不存在');
      }
      
      const now = new Date();
      const updateData = {
        ...healthProfileData,
        updated_at: now
      };

      await db(this.tableName).where({ id }).update(updateData);
      
      // 清除缓存
      await this.clearHealthProfileCache({ ...healthProfile, ...updateData });
      
      return this.getById(id);
    } catch (error) {
      logger.error('更新健康资料失败', { error: error.message, id, healthProfileData });
      throw error;
    }
  }

  /**
   * 根据用户ID更新健康资料
   */
  async updateByUserId(userId, healthProfileData) {
    try {
      const healthProfile = await this.getByUserId(userId);
      
      if (!healthProfile) {
        throw new Error('健康资料不存在');
      }
      
      return this.update(healthProfile.id, healthProfileData);
    } catch (error) {
      logger.error('根据用户ID更新健康资料失败', { error: error.message, userId, healthProfileData });
      throw error;
    }
  }

  /**
   * 删除健康资料
   */
  async delete(id) {
    try {
      const healthProfile = await this.getById(id);
      
      if (!healthProfile) {
        return false;
      }
      
      await db(this.tableName).where({ id }).del();
      
      // 清除缓存
      await this.clearHealthProfileCache(healthProfile);
      
      return true;
    } catch (error) {
      logger.error('删除健康资料失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 根据用户ID删除健康资料
   */
  async deleteByUserId(userId) {
    try {
      const healthProfile = await this.getByUserId(userId);
      
      if (!healthProfile) {
        return false;
      }
      
      return this.delete(healthProfile.id);
    } catch (error) {
      logger.error('根据用户ID删除健康资料失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 更新最后检查时间
   */
  async updateLastCheckup(id) {
    try {
      const now = new Date();
      await db(this.tableName).where({ id }).update({ 
        last_checkup: now,
        updated_at: now
      });
      
      // 清除缓存
      await deleteCache(`${this.cacheKeyPrefix}id:${id}`);
      
      return true;
    } catch (error) {
      logger.error('更新最后检查时间失败', { error: error.message, id });
      throw error;
    }
  }

  /**
   * 根据体质类型获取健康资料
   */
  async getByConstitutionType(constitutionType, page = 1, pageSize = 10, privacyLevel = ['public']) {
    try {
      const offset = (page - 1) * pageSize;
      
      // 构建查询
      const query = db(this.tableName)
        .where({ constitution_type: constitutionType })
        .whereIn('privacy_level', Array.isArray(privacyLevel) ? privacyLevel : [privacyLevel]);
      
      // 获取总数
      const countQuery = query.clone();
      const totalItems = await countQuery.count('id as count').first();
      
      // 获取分页数据
      const healthProfiles = await query
        .select('*')
        .orderBy('updated_at', 'desc')
        .offset(offset)
        .limit(pageSize);
      
      return {
        data: healthProfiles,
        pagination: {
          page,
          pageSize,
          totalItems: totalItems ? totalItems.count : 0,
          totalPages: Math.ceil((totalItems ? totalItems.count : 0) / pageSize)
        }
      };
    } catch (error) {
      logger.error('根据体质类型获取健康资料失败', { 
        error: error.message, 
        constitutionType, 
        page, 
        pageSize, 
        privacyLevel 
      });
      throw error;
    }
  }

  /**
   * 更新体质类型
   */
  async updateConstitutionType(id, constitutionType) {
    try {
      const now = new Date();
      await db(this.tableName).where({ id }).update({ 
        constitution_type: constitutionType,
        updated_at: now
      });
      
      // 清除缓存
      await deleteCache(`${this.cacheKeyPrefix}id:${id}`);
      
      return this.getById(id);
    } catch (error) {
      logger.error('更新体质类型失败', { error: error.message, id, constitutionType });
      throw error;
    }
  }

  /**
   * 清除健康资料相关缓存
   */
  async clearHealthProfileCache(healthProfile) {
    try {
      if (!healthProfile) return;
      
      const cacheKeys = [];
      
      if (healthProfile.id) {
        cacheKeys.push(`${this.cacheKeyPrefix}id:${healthProfile.id}`);
      }
      
      if (healthProfile.user_id) {
        cacheKeys.push(`${this.cacheKeyPrefix}user:${healthProfile.user_id}`);
      }
      
      if (cacheKeys.length > 0) {
        await Promise.all(cacheKeys.map(key => deleteCache(key)));
      }
      
      return true;
    } catch (error) {
      logger.error('清除健康资料缓存失败', { error: error.message, healthProfile });
      return false;
    }
  }
}

module.exports = new HealthProfileRepository(); 