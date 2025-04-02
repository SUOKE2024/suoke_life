import { Request, Response, NextFunction } from 'express';
import * as blogService from './blog.service';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';

/**
 * 获取博客列表
 */
export const getBlogList = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { page = 1, limit = 10, tags } = req.query;
    
    const result = await blogService.getBlogList({
      page: Number(page),
      limit: Number(limit),
      tags: tags ? (tags as string).split(',') : undefined
    });
    
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取博客列表失败:', error);
    next(error);
  }
};

/**
 * 获取博客详情
 */
export const getBlogById = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    
    const blog = await blogService.getBlogById(id);
    
    if (!blog) {
      throw new ApiError(404, '博客不存在或未发布');
    }
    
    res.status(200).json(blog);
  } catch (error) {
    logger.error(`获取博客详情失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 获取我的博客
 */
export const getMyBlogs = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { page = 1, limit = 10, status, tags } = req.query;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const result = await blogService.getMyBlogs(userId, {
      page: Number(page),
      limit: Number(limit),
      status: status as any,
      tags: tags ? (tags as string).split(',') : undefined
    });
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`获取我的博客列表失败:`, error);
    next(error);
  }
};

/**
 * 创建博客
 */
export const createBlog = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const blogData = req.body;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const newBlog = await blogService.createBlog({
      ...blogData,
      author: userId
    });
    
    res.status(201).json(newBlog);
  } catch (error) {
    logger.error('创建博客失败:', error);
    next(error);
  }
};

/**
 * 更新博客
 */
export const updateBlog = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const blogData = req.body;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const updatedBlog = await blogService.updateBlog(id, blogData, userId);
    
    if (!updatedBlog) {
      throw new ApiError(404, '博客不存在或无权更新');
    }
    
    res.status(200).json(updatedBlog);
  } catch (error) {
    logger.error(`更新博客失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 删除博客
 */
export const deleteBlog = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const result = await blogService.deleteBlog(id, userId);
    
    if (!result) {
      throw new ApiError(404, '博客不存在或无权删除');
    }
    
    res.status(200).json({ message: '博客已成功删除' });
  } catch (error) {
    logger.error(`删除博客失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 获取博客评论
 */
export const getBlogComments = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const { page = 1, limit = 10, parentComment } = req.query;
    
    const result = await blogService.getBlogComments({
      page: Number(page),
      limit: Number(limit),
      blog: id,
      parentComment: parentComment as string
    });
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`获取博客评论失败 [博客ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 添加博客评论
 */
export const addBlogComment = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const commentData = req.body;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    const newComment = await blogService.addBlogComment({
      ...commentData,
      blog: id,
      author: userId
    });
    
    res.status(201).json(newComment);
  } catch (error) {
    logger.error(`添加博客评论失败 [博客ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 点赞博客
 */
export const likeBlog = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    
    const result = await blogService.likeBlog(id);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`点赞博客失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 点赞评论
 */
export const likeComment = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id, commentId } = req.params;
    
    const result = await blogService.likeComment(commentId);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`点赞评论失败 [评论ID: ${req.params.commentId}]:`, error);
    next(error);
  }
}; 