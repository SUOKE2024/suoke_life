/**
 * 个人资料服务
 */
const { profileRepository, userRepository } = require('../repositories');
const { logger } = require('@suoke/shared').utils;
const config = require('../config');

class ProfileService {
  /**
   * 创建个人资料
   */
  async createProfile(userId, profileData) {
    try {
      // 检查用户是否存在
      const user = await userRepository.getById(userId);
      
      if (!user) {
        throw new Error('用户不存在');
      }

      // 检查是否已有资料
      const existingProfile = await profileRepository.getByUserId(userId);
      
      if (existingProfile) {
        throw new Error('用户已有个人资料');
      }

      // 创建个人资料
      const profile = await profileRepository.create({
        user_id: userId,
        ...profileData
      });

      return profile;
    } catch (error) {
      logger.error('创建个人资料失败', { error: error.message, userId, profileData });
      throw error;
    }
  }

  /**
   * 获取个人资料
   */
  async getProfile(userId) {
    try {
      // 检查用户是否存在
      const user = await userRepository.getById(userId);
      
      if (!user) {
        throw new Error('用户不存在');
      }

      // 获取个人资料
      const profile = await profileRepository.getByUserId(userId);
      
      if (!profile) {
        return null;
      }

      return profile;
    } catch (error) {
      logger.error('获取个人资料失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 更新个人资料
   */
  async updateProfile(userId, profileData) {
    try {
      // 检查用户是否存在
      const user = await userRepository.getById(userId);
      
      if (!user) {
        throw new Error('用户不存在');
      }

      // 获取个人资料
      const profile = await profileRepository.getByUserId(userId);
      
      if (!profile) {
        throw new Error('个人资料不存在');
      }

      // 更新个人资料
      const updatedProfile = await profileRepository.update(profile.id, profileData);

      return updatedProfile;
    } catch (error) {
      logger.error('更新个人资料失败', { error: error.message, userId, profileData });
      throw error;
    }
  }

  /**
   * 删除个人资料
   */
  async deleteProfile(userId) {
    try {
      // 检查用户是否存在
      const user = await userRepository.getById(userId);
      
      if (!user) {
        throw new Error('用户不存在');
      }

      // 获取个人资料
      const profile = await profileRepository.getByUserId(userId);
      
      if (!profile) {
        throw new Error('个人资料不存在');
      }

      // 删除个人资料
      await profileRepository.delete(profile.id);

      return true;
    } catch (error) {
      logger.error('删除个人资料失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 获取用户头像
   */
  async getAvatar(userId) {
    try {
      // 获取个人资料
      const profile = await profileRepository.getByUserId(userId);
      
      if (!profile || !profile.avatar) {
        return null;
      }

      return profile.avatar;
    } catch (error) {
      logger.error('获取用户头像失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 更新用户头像
   */
  async updateAvatar(userId, avatarUrl) {
    try {
      // 检查用户是否存在
      const user = await userRepository.getById(userId);
      
      if (!user) {
        throw new Error('用户不存在');
      }

      // 获取个人资料
      const profile = await profileRepository.getByUserId(userId);
      
      if (!profile) {
        throw new Error('个人资料不存在');
      }

      // 更新头像
      const updatedProfile = await profileRepository.update(profile.id, {
        avatar: avatarUrl
      });

      return updatedProfile;
    } catch (error) {
      logger.error('更新用户头像失败', { error: error.message, userId, avatarUrl });
      throw error;
    }
  }

  /**
   * 搜索个人资料
   */
  async searchProfiles(query, page = 1, pageSize = 10) {
    try {
      return await profileRepository.search(query, page, pageSize);
    } catch (error) {
      logger.error('搜索个人资料失败', { error: error.message, query, page, pageSize });
      throw error;
    }
  }

  /**
   * 检查昵称是否可用
   */
  async checkNicknameAvailability(nickname) {
    try {
      // 实现昵称查询逻辑
      const query = await profileRepository.search(nickname);
      
      const isAvailable = query.data.length === 0 || 
        !query.data.some(profile => profile.nickname.toLowerCase() === nickname.toLowerCase());
      
      return {
        available: isAvailable,
        suggestion: !isAvailable ? this.generateNicknameSuggestion(nickname) : null
      };
    } catch (error) {
      logger.error('检查昵称可用性失败', { error: error.message, nickname });
      throw error;
    }
  }

  /**
   * 生成昵称建议
   */
  generateNicknameSuggestion(nickname) {
    // 简单实现，实际可以基于更复杂的算法
    const randomSuffix = Math.floor(Math.random() * 1000);
    return `${nickname}${randomSuffix}`;
  }
}

module.exports = new ProfileService(); 