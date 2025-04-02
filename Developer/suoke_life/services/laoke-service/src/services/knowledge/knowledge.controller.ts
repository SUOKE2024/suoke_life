import { Request, Response, NextFunction } from 'express';
import * as knowledgeService from './knowledge.service';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';

/**
 * 获取知识内容列表
 */
export const getKnowledgeList = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { page = 1, limit = 10, category, tags } = req.query;
    
    const result = await knowledgeService.getKnowledgeList({
      page: Number(page),
      limit: Number(limit),
      category: category as string,
      tags: tags ? (tags as string).split(',') : undefined
    });
    
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取知识内容列表失败:', error);
    next(error);
  }
};

/**
 * 获取知识内容详情
 */
export const getKnowledgeById = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    
    const knowledge = await knowledgeService.getKnowledgeById(id);
    
    if (!knowledge) {
      throw new ApiError(404, '知识内容不存在');
    }
    
    res.status(200).json(knowledge);
  } catch (error) {
    logger.error(`获取知识内容详情失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 获取推荐知识内容
 */
export const getRecommendedKnowledge = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { limit = 5, userId } = req.query;
    
    const recommendedKnowledge = await knowledgeService.getRecommendedKnowledge({
      limit: Number(limit),
      userId: userId as string
    });
    
    res.status(200).json(recommendedKnowledge);
  } catch (error) {
    logger.error('获取推荐知识内容失败:', error);
    next(error);
  }
};

/**
 * 获取知识分类
 */
export const getKnowledgeCategories = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const categories = await knowledgeService.getKnowledgeCategories();
    
    res.status(200).json(categories);
  } catch (error) {
    logger.error('获取知识分类失败:', error);
    next(error);
  }
};

/**
 * 创建知识内容
 */
export const createKnowledge = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const knowledgeData = req.body;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const newKnowledge = await knowledgeService.createKnowledge({
      ...knowledgeData,
      createdBy: userId
    });
    
    res.status(201).json(newKnowledge);
  } catch (error) {
    logger.error('创建知识内容失败:', error);
    next(error);
  }
};

/**
 * 更新知识内容
 */
export const updateKnowledge = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const knowledgeData = req.body;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const updatedKnowledge = await knowledgeService.updateKnowledge(id, knowledgeData, userId);
    
    if (!updatedKnowledge) {
      throw new ApiError(404, '知识内容不存在或无权更新');
    }
    
    res.status(200).json(updatedKnowledge);
  } catch (error) {
    logger.error(`更新知识内容失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 删除知识内容
 */
export const deleteKnowledge = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const result = await knowledgeService.deleteKnowledge(id, userId);
    
    if (!result) {
      throw new ApiError(404, '知识内容不存在或无权删除');
    }
    
    res.status(200).json({ message: '知识内容已成功删除' });
  } catch (error) {
    logger.error(`删除知识内容失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 搜索知识内容
 */
export const searchKnowledge = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { q, page = 1, limit = 10 } = req.query;
    
    if (!q) {
      throw new ApiError(400, '搜索关键词不能为空');
    }
    
    const searchResults = await knowledgeService.searchKnowledge({
      query: q as string,
      page: Number(page),
      limit: Number(limit)
    });
    
    res.status(200).json(searchResults);
  } catch (error) {
    logger.error(`搜索知识内容失败 [查询: ${req.query.q}]:`, error);
    next(error);
  }
};

/**
 * 为知识内容评分
 */
export const rateKnowledge = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const { rating, feedback } = req.body;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    if (!rating || rating < 1 || rating > 5) {
      throw new ApiError(400, '评分必须在1-5之间');
    }
    
    const result = await knowledgeService.rateKnowledge({
      knowledgeId: id,
      userId,
      rating,
      feedback
    });
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`为知识内容评分失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 获取热门知识内容
 */
export const getTrendingKnowledge = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { period = 'week', limit = 5 } = req.query;
    
    const trendingKnowledge = await knowledgeService.getTrendingKnowledge({
      period: period as 'day' | 'week' | 'month',
      limit: Number(limit)
    });
    
    res.status(200).json(trendingKnowledge);
  } catch (error) {
    logger.error('获取热门知识内容失败:', error);
    next(error);
  }
}; 