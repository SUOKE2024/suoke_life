import { Request, Response, NextFunction } from 'express';
import * as gameService from './game.service';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';

/**
 * 获取任务列表
 */
export const getQuestList = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { page = 1, limit = 10, type, difficulty, isActive } = req.query;
    
    const result = await gameService.getQuestList({
      page: Number(page),
      limit: Number(limit),
      type: type as any,
      difficulty: difficulty as any,
      isActive: isActive === 'true'
    });
    
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取任务列表失败:', error);
    next(error);
  }
};

/**
 * 获取任务详情
 */
export const getQuestById = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const userId = req.user?.id;
    
    const quest = await gameService.getQuestById(id, userId);
    
    if (!quest) {
      throw new ApiError(404, '任务不存在或不可用');
    }
    
    res.status(200).json(quest);
  } catch (error) {
    logger.error(`获取任务详情失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 接受任务
 */
export const acceptQuest = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const result = await gameService.acceptQuest(id, userId);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`接受任务失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 更新任务步骤
 */
export const updateQuestStep = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id, stepIndex } = req.params;
    const data = req.body;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const result = await gameService.updateQuestStep(id, Number(stepIndex), data, userId);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`更新任务步骤失败 [ID: ${req.params.id}, 步骤: ${req.params.stepIndex}]:`, error);
    next(error);
  }
};

/**
 * 完成任务
 */
export const completeQuest = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const result = await gameService.completeQuest(id, userId);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`完成任务失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 获取用户进度
 */
export const getUserProgress = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const progress = await gameService.getUserProgress(userId);
    
    res.status(200).json(progress);
  } catch (error) {
    logger.error('获取用户进度失败:', error);
    next(error);
  }
}; 