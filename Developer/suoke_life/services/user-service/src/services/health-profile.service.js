/**
 * 健康档案服务
 * 负责处理用户健康档案相关业务逻辑
 */
const { HealthProfileRepository } = require('../repositories');
const { logger } = require('@suoke/shared').utils;
const { BusinessError } = require('@suoke/shared').utils;

class HealthProfileService {
  constructor() {
    this.healthProfileRepository = new HealthProfileRepository();
  }

  /**
   * 创建健康档案
   * @param {Object} data 健康档案数据
   * @param {string} userId 用户ID
   * @returns {Promise<Object>} 创建的健康档案
   */
  async createHealthProfile(data, userId) {
    try {
      logger.info(`创建用户 ${userId} 的健康档案`);
      
      // 检查用户是否已有健康档案
      const existingProfile = await this.healthProfileRepository.findByUserId(userId);
      if (existingProfile) {
        throw new BusinessError('用户已存在健康档案', 409);
      }
      
      // 创建健康档案
      const healthProfile = await this.healthProfileRepository.create({
        ...data,
        userId
      });
      
      return healthProfile;
    } catch (error) {
      logger.error(`创建健康档案失败: ${error.message}`, { userId, error });
      throw error;
    }
  }

  /**
   * 获取用户健康档案
   * @param {string} userId 用户ID
   * @returns {Promise<Object>} 健康档案
   */
  async getHealthProfileByUserId(userId) {
    try {
      logger.info(`获取用户 ${userId} 的健康档案`);
      
      const healthProfile = await this.healthProfileRepository.findByUserId(userId);
      if (!healthProfile) {
        throw new BusinessError('未找到健康档案', 404);
      }
      
      return healthProfile;
    } catch (error) {
      logger.error(`获取健康档案失败: ${error.message}`, { userId, error });
      throw error;
    }
  }

  /**
   * 更新健康档案
   * @param {string} userId 用户ID
   * @param {Object} data 更新数据
   * @returns {Promise<Object>} 更新后的健康档案
   */
  async updateHealthProfile(userId, data) {
    try {
      logger.info(`更新用户 ${userId} 的健康档案`);
      
      // 检查健康档案是否存在
      const healthProfile = await this.healthProfileRepository.findByUserId(userId);
      if (!healthProfile) {
        throw new BusinessError('未找到健康档案', 404);
      }
      
      // 更新健康档案
      const updatedProfile = await this.healthProfileRepository.update(healthProfile.id, data);
      
      return updatedProfile;
    } catch (error) {
      logger.error(`更新健康档案失败: ${error.message}`, { userId, error });
      throw error;
    }
  }

  /**
   * 删除健康档案
   * @param {string} userId 用户ID
   * @returns {Promise<boolean>} 是否成功删除
   */
  async deleteHealthProfile(userId) {
    try {
      logger.info(`删除用户 ${userId} 的健康档案`);
      
      // 检查健康档案是否存在
      const healthProfile = await this.healthProfileRepository.findByUserId(userId);
      if (!healthProfile) {
        throw new BusinessError('未找到健康档案', 404);
      }
      
      // 删除健康档案
      await this.healthProfileRepository.delete(healthProfile.id);
      
      return true;
    } catch (error) {
      logger.error(`删除健康档案失败: ${error.message}`, { userId, error });
      throw error;
    }
  }

  /**
   * 获取体质测评结果
   * @param {string} userId 用户ID
   * @returns {Promise<Object>} 体质测评结果
   */
  async getConstitutionAssessment(userId) {
    try {
      logger.info(`获取用户 ${userId} 的体质测评结果`);
      
      const healthProfile = await this.healthProfileRepository.findByUserId(userId);
      if (!healthProfile || !healthProfile.constitutionAssessment) {
        throw new BusinessError('未找到体质测评数据', 404);
      }
      
      return healthProfile.constitutionAssessment;
    } catch (error) {
      logger.error(`获取体质测评结果失败: ${error.message}`, { userId, error });
      throw error;
    }
  }

  /**
   * 保存体质测评结果
   * @param {string} userId 用户ID
   * @param {Object} assessmentData 体质测评数据
   * @returns {Promise<Object>} 更新后的健康档案
   */
  async saveConstitutionAssessment(userId, assessmentData) {
    try {
      logger.info(`保存用户 ${userId} 的体质测评结果`);
      
      // 检查健康档案是否存在
      let healthProfile = await this.healthProfileRepository.findByUserId(userId);
      
      if (!healthProfile) {
        // 如果不存在，创建一个新的健康档案
        healthProfile = await this.healthProfileRepository.create({
          userId,
          constitutionAssessment: assessmentData
        });
      } else {
        // 如果存在，更新体质测评结果
        healthProfile = await this.healthProfileRepository.update(healthProfile.id, {
          constitutionAssessment: assessmentData
        });
      }
      
      return healthProfile;
    } catch (error) {
      logger.error(`保存体质测评结果失败: ${error.message}`, { userId, error });
      throw error;
    }
  }
}

module.exports = HealthProfileService;