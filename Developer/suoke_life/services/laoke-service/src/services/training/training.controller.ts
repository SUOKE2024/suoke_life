import { Request, Response, NextFunction } from 'express';
import * as trainingService from './training.service';
import { EnrollmentStatus, ChapterStatus } from '../../models/training.model';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';

/**
 * 获取所有课程
 */
export const getAllCourses = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { 
      limit = 20, 
      skip = 0, 
      courseType, 
      difficultyLevel,
      sortBy = 'createdAt',
      sortOrder = 'desc'
    } = req.query;
    
    // 构建查询条件
    const query: Record<string, any> = {};
    if (courseType) query.courseType = courseType;
    if (difficultyLevel) query.difficultyLevel = difficultyLevel;
    
    // 构建排序条件
    const sort: Record<string, number> = {};
    sort[sortBy as string] = sortOrder === 'desc' ? -1 : 1;
    
    const result = await trainingService.getAllCourses(
      query,
      Number(limit),
      Number(skip),
      sort
    );
    
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取课程列表失败:', error);
    next(error);
  }
};

/**
 * 获取课程详情
 */
export const getCourseById = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    
    const course = await trainingService.getCourseById(id);
    
    res.status(200).json(course);
  } catch (error) {
    logger.error(`获取课程详情失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 搜索课程
 */
export const searchCourses = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { 
      searchTerm, 
      limit = 20, 
      skip = 0, 
      courseType, 
      difficultyLevel 
    } = req.query;
    
    if (!searchTerm) {
      throw new ApiError(400, '搜索关键词不能为空');
    }
    
    // 构建过滤条件
    const filters: Record<string, any> = {};
    if (courseType) filters.courseType = courseType;
    if (difficultyLevel) filters.difficultyLevel = difficultyLevel;
    
    const result = await trainingService.searchCourses(
      searchTerm as string,
      filters,
      Number(limit),
      Number(skip)
    );
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`搜索课程失败 [关键词: ${req.query.searchTerm}]:`, error);
    next(error);
  }
};

/**
 * 创建课程
 */
export const createCourse = async (req: Request, res: Response, next: NextFunction) => {
  try {
    // 检查权限
    if (!req.user?.roles?.includes('admin')) {
      throw new ApiError(403, '无权创建课程');
    }
    
    const courseData = req.body;
    
    const course = await trainingService.createCourse(courseData);
    
    res.status(201).json(course);
  } catch (error) {
    logger.error('创建课程失败:', error);
    next(error);
  }
};

/**
 * 更新课程
 */
export const updateCourse = async (req: Request, res: Response, next: NextFunction) => {
  try {
    // 检查权限
    if (!req.user?.roles?.includes('admin')) {
      throw new ApiError(403, '无权更新课程');
    }
    
    const { id } = req.params;
    const updateData = req.body;
    
    const course = await trainingService.updateCourse(id, updateData);
    
    res.status(200).json(course);
  } catch (error) {
    logger.error(`更新课程失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 删除课程
 */
export const deleteCourse = async (req: Request, res: Response, next: NextFunction) => {
  try {
    // 检查权限
    if (!req.user?.roles?.includes('admin')) {
      throw new ApiError(403, '无权删除课程');
    }
    
    const { id } = req.params;
    
    const result = await trainingService.deleteCourse(id);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`删除课程失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 注册课程
 */
export const enrollCourse = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { courseId } = req.params;
    const { paymentInfo } = req.body;
    
    const enrollment = await trainingService.enrollCourse(userId, courseId, paymentInfo);
    
    res.status(201).json(enrollment);
  } catch (error) {
    logger.error(`注册课程失败 [课程ID: ${req.params.courseId}]:`, error);
    next(error);
  }
};

/**
 * 获取用户课程注册列表
 */
export const getUserEnrollments = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { status, limit = 20, skip = 0 } = req.query;
    
    const result = await trainingService.getUserEnrollments(
      userId,
      status as EnrollmentStatus | undefined,
      Number(limit),
      Number(skip)
    );
    
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取用户课程注册列表失败:', error);
    next(error);
  }
};

/**
 * 获取课程注册详情
 */
export const getEnrollmentDetails = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { courseId } = req.params;
    
    const enrollment = await trainingService.getEnrollmentDetails(userId, courseId);
    
    res.status(200).json(enrollment);
  } catch (error) {
    logger.error(`获取课程注册详情失败 [课程ID: ${req.params.courseId}]:`, error);
    next(error);
  }
};

/**
 * 更新课程注册状态
 */
export const updateEnrollmentStatus = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { courseId } = req.params;
    const { status } = req.body;
    
    if (!status || !Object.values(EnrollmentStatus).includes(status)) {
      throw new ApiError(400, '无效的状态值');
    }
    
    const enrollment = await trainingService.updateEnrollmentStatus(userId, courseId, status);
    
    res.status(200).json(enrollment);
  } catch (error) {
    logger.error(`更新课程注册状态失败 [课程ID: ${req.params.courseId}]:`, error);
    next(error);
  }
};

/**
 * 更新章节进度
 */
export const updateChapterProgress = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { courseId, chapterId } = req.params;
    const { status, timeSpent, quizScore, notes } = req.body;
    
    if (!status || !Object.values(ChapterStatus).includes(status)) {
      throw new ApiError(400, '无效的状态值');
    }
    
    const progress = await trainingService.updateChapterProgress(
      userId,
      courseId,
      chapterId,
      {
        status,
        timeSpent,
        quizScore,
        notes
      }
    );
    
    res.status(200).json(progress);
  } catch (error) {
    logger.error(`更新章节进度失败 [课程ID: ${req.params.courseId}, 章节ID: ${req.params.chapterId}]:`, error);
    next(error);
  }
};

/**
 * 获取章节进度
 */
export const getChapterProgress = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { courseId, chapterId } = req.params;
    
    const progress = await trainingService.getChapterProgress(userId, courseId, chapterId);
    
    if (!progress) {
      return res.status(200).json({
        status: ChapterStatus.NOT_STARTED,
        timeSpent: 0
      });
    }
    
    res.status(200).json(progress);
  } catch (error) {
    logger.error(`获取章节进度失败 [课程ID: ${req.params.courseId}, 章节ID: ${req.params.chapterId}]:`, error);
    next(error);
  }
};

/**
 * 获取课程的所有章节进度
 */
export const getCourseProgress = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { courseId } = req.params;
    
    const progress = await trainingService.getCourseProgress(userId, courseId);
    
    res.status(200).json(progress);
  } catch (error) {
    logger.error(`获取课程进度失败 [课程ID: ${req.params.courseId}]:`, error);
    next(error);
  }
};

/**
 * 提交课程评价
 */
export const submitCourseReview = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { courseId } = req.params;
    const { rating, comment } = req.body;
    
    if (rating === undefined || rating < 1 || rating > 5) {
      throw new ApiError(400, '评分必须在1-5之间');
    }
    
    const review = await trainingService.submitCourseReview(
      userId,
      courseId,
      rating,
      comment
    );
    
    res.status(200).json(review);
  } catch (error) {
    logger.error(`提交课程评价失败 [课程ID: ${req.params.courseId}]:`, error);
    next(error);
  }
};

/**
 * 获取课程评价
 */
export const getCourseReviews = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { courseId } = req.params;
    const { limit = 20, skip = 0 } = req.query;
    
    const result = await trainingService.getCourseReviews(
      courseId,
      Number(limit),
      Number(skip)
    );
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`获取课程评价失败 [课程ID: ${req.params.courseId}]:`, error);
    next(error);
  }
}; 