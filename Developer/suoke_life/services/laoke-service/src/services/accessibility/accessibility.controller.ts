import { Request, Response, NextFunction } from 'express';
import * as accessibilityService from './accessibility.service';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';

/**
 * 获取用户无障碍配置
 */
export const getUserAccessibilityProfile = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { userId } = req.params;
    const currentUserId = req.user?.id;
    
    // 检查权限：只能查看自己的配置，或者管理员可以查看所有人的配置
    if (userId !== currentUserId && req.user?.role !== 'admin') {
      throw new ApiError(403, '无权限查看其他用户的无障碍配置');
    }
    
    const profile = await accessibilityService.getUserAccessibilityProfile(userId);
    
    res.status(200).json(profile);
  } catch (error) {
    logger.error(`获取用户无障碍配置失败 [用户ID: ${req.params.userId}]:`, error);
    next(error);
  }
};

/**
 * 更新用户无障碍配置
 */
export const updateUserAccessibilityProfile = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { userId } = req.params;
    const currentUserId = req.user?.id;
    const profileData = req.body;
    
    // 检查权限：只能更新自己的配置，或者管理员可以更新所有人的配置
    if (userId !== currentUserId && req.user?.role !== 'admin') {
      throw new ApiError(403, '无权限更新其他用户的无障碍配置');
    }
    
    const updatedProfile = await accessibilityService.updateUserAccessibilityProfile(userId, profileData);
    
    res.status(200).json(updatedProfile);
  } catch (error) {
    logger.error(`更新用户无障碍配置失败 [用户ID: ${req.params.userId}]:`, error);
    next(error);
  }
};

/**
 * 获取无障碍资源
 */
export const getAccessibilityResources = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const resources = await accessibilityService.getAccessibilityResources();
    
    res.status(200).json(resources);
  } catch (error) {
    logger.error('获取无障碍资源失败:', error);
    next(error);
  }
}; 