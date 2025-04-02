import express from 'express';
import * as trainingController from '../../services/training/training.controller';
import { authenticate } from '../middleware/auth.middleware';

const router = express.Router();

/**
 * 课程管理路由
 */

/**
 * @route GET /api/v1/training/courses
 * @desc 获取所有课程
 * @access 公开
 */
router.get('/courses', trainingController.getAllCourses);

/**
 * @route GET /api/v1/training/courses/search
 * @desc 搜索课程
 * @access 公开
 */
router.get('/courses/search', trainingController.searchCourses);

/**
 * @route GET /api/v1/training/courses/:id
 * @desc 获取课程详情
 * @access 公开
 */
router.get('/courses/:id', trainingController.getCourseById);

/**
 * @route POST /api/v1/training/courses
 * @desc 创建课程
 * @access 仅管理员
 */
router.post('/courses', authenticate, trainingController.createCourse);

/**
 * @route PUT /api/v1/training/courses/:id
 * @desc 更新课程
 * @access 仅管理员
 */
router.put('/courses/:id', authenticate, trainingController.updateCourse);

/**
 * @route DELETE /api/v1/training/courses/:id
 * @desc 删除课程
 * @access 仅管理员
 */
router.delete('/courses/:id', authenticate, trainingController.deleteCourse);

/**
 * @route GET /api/v1/training/courses/:courseId/reviews
 * @desc 获取课程评价
 * @access 公开
 */
router.get('/courses/:courseId/reviews', trainingController.getCourseReviews);

/**
 * 课程注册路由
 */

/**
 * @route POST /api/v1/training/enrollments/:courseId
 * @desc 注册课程
 * @access 需要认证
 */
router.post('/enrollments/:courseId', authenticate, trainingController.enrollCourse);

/**
 * @route GET /api/v1/training/enrollments
 * @desc 获取用户课程注册列表
 * @access 需要认证
 */
router.get('/enrollments', authenticate, trainingController.getUserEnrollments);

/**
 * @route GET /api/v1/training/enrollments/:courseId
 * @desc 获取课程注册详情
 * @access 需要认证
 */
router.get('/enrollments/:courseId', authenticate, trainingController.getEnrollmentDetails);

/**
 * @route PUT /api/v1/training/enrollments/:courseId/status
 * @desc 更新课程注册状态
 * @access 需要认证
 */
router.put('/enrollments/:courseId/status', authenticate, trainingController.updateEnrollmentStatus);

/**
 * 课程进度路由
 */

/**
 * @route GET /api/v1/training/progress/:courseId
 * @desc 获取课程的所有章节进度
 * @access 需要认证
 */
router.get('/progress/:courseId', authenticate, trainingController.getCourseProgress);

/**
 * @route GET /api/v1/training/progress/:courseId/:chapterId
 * @desc 获取章节进度
 * @access 需要认证
 */
router.get('/progress/:courseId/:chapterId', authenticate, trainingController.getChapterProgress);

/**
 * @route PUT /api/v1/training/progress/:courseId/:chapterId
 * @desc 更新章节进度
 * @access 需要认证
 */
router.put('/progress/:courseId/:chapterId', authenticate, trainingController.updateChapterProgress);

/**
 * 课程评价路由
 */

/**
 * @route POST /api/v1/training/reviews/:courseId
 * @desc 提交课程评价
 * @access 需要认证
 */
router.post('/reviews/:courseId', authenticate, trainingController.submitCourseReview);

export default router; 