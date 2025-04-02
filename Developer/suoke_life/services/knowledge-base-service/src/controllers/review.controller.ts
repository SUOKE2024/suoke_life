/**
 * 知识审核控制器
 * 处理知识条目的审核流程
 */
import { Request, Response } from 'express';
import mongoose from 'mongoose';
import { BadRequestError } from '../errors/bad-request-error';
import { NotFoundError } from '../errors/not-found-error';
import { ForbiddenError } from '../errors/forbidden-error';
import logger from '../utils/logger';
import reviewService from '../services/review.service';

export class ReviewController {
  /**
   * 提交知识条目审核
   * @route POST /api/reviews/:knowledgeType/:id/submit
   */
  async submitForReview(req: Request, res: Response) {
    try {
      const { knowledgeType, id } = req.params;
      const { comments } = req.body;
      
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new BadRequestError('无效的知识条目ID');
      }
      
      // 确保用户已登录
      if (!req.currentUser) {
        throw new ForbiddenError('需要登录才能提交审核');
      }
      
      const result = await reviewService.submitForReview(
        knowledgeType,
        id,
        req.currentUser.id,
        comments
      );
      
      logger.info('知识条目已提交审核', { 
        knowledgeType, 
        id, 
        userId: req.currentUser.id 
      });
      
      res.status(201).json({
        success: true,
        data: result,
        message: '已成功提交审核'
      });
    } catch (error) {
      logger.error('提交审核失败', { 
        error: (error as Error).message, 
        knowledgeType: req.params.knowledgeType,
        id: req.params.id
      });
      
      if (error instanceof BadRequestError || error instanceof ForbiddenError) {
        return res.status(400).json({
          success: false,
          message: error.message
        });
      }
      
      if (error instanceof NotFoundError) {
        return res.status(404).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 获取待审核的知识条目列表
   * @route GET /api/reviews/pending
   */
  async getPendingReviews(req: Request, res: Response) {
    try {
      const { page = 1, limit = 20, knowledgeType } = req.query;
      
      // 确保用户是管理员
      if (!req.currentUser || !req.currentUser.isAdmin) {
        throw new ForbiddenError('需要管理员权限');
      }
      
      const filter: any = { status: 'pending' };
      
      // 如果指定了知识类型，添加过滤条件
      if (knowledgeType) {
        filter.knowledgeType = knowledgeType;
      }
      
      const result = await reviewService.getReviews(
        filter,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        data: result.data,
        total: result.total,
        page: result.page,
        limit: result.limit,
        totalPages: result.totalPages
      });
    } catch (error) {
      logger.error('获取待审核列表失败', { 
        error: (error as Error).message, 
        query: req.query
      });
      
      if (error instanceof ForbiddenError) {
        return res.status(403).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 审核通过知识条目
   * @route POST /api/reviews/:reviewId/approve
   */
  async approveReview(req: Request, res: Response) {
    try {
      const { reviewId } = req.params;
      const { comments } = req.body;
      
      if (!mongoose.Types.ObjectId.isValid(reviewId)) {
        throw new BadRequestError('无效的审核ID');
      }
      
      // 确保用户是管理员
      if (!req.currentUser || !req.currentUser.isAdmin) {
        throw new ForbiddenError('需要管理员权限');
      }
      
      const result = await reviewService.approveReview(
        reviewId,
        req.currentUser.id,
        comments
      );
      
      logger.info('审核已通过', { reviewId, adminId: req.currentUser.id });
      
      res.status(200).json({
        success: true,
        data: result,
        message: '审核已通过'
      });
    } catch (error) {
      logger.error('审核通过失败', { 
        error: (error as Error).message, 
        reviewId: req.params.reviewId
      });
      
      if (error instanceof BadRequestError || error instanceof ForbiddenError) {
        return res.status(400).json({
          success: false,
          message: error.message
        });
      }
      
      if (error instanceof NotFoundError) {
        return res.status(404).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 拒绝知识条目审核
   * @route POST /api/reviews/:reviewId/reject
   */
  async rejectReview(req: Request, res: Response) {
    try {
      const { reviewId } = req.params;
      const { comments } = req.body;
      
      if (!comments) {
        throw new BadRequestError('拒绝审核必须提供理由');
      }
      
      if (!mongoose.Types.ObjectId.isValid(reviewId)) {
        throw new BadRequestError('无效的审核ID');
      }
      
      // 确保用户是管理员
      if (!req.currentUser || !req.currentUser.isAdmin) {
        throw new ForbiddenError('需要管理员权限');
      }
      
      const result = await reviewService.rejectReview(
        reviewId,
        req.currentUser.id,
        comments
      );
      
      logger.info('审核已拒绝', { reviewId, adminId: req.currentUser.id });
      
      res.status(200).json({
        success: true,
        data: result,
        message: '审核已拒绝'
      });
    } catch (error) {
      logger.error('审核拒绝失败', { 
        error: (error as Error).message, 
        reviewId: req.params.reviewId
      });
      
      if (error instanceof BadRequestError || error instanceof ForbiddenError) {
        return res.status(400).json({
          success: false,
          message: error.message
        });
      }
      
      if (error instanceof NotFoundError) {
        return res.status(404).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 获取知识条目的审核历史
   * @route GET /api/reviews/:knowledgeType/:id/history
   */
  async getReviewHistory(req: Request, res: Response) {
    try {
      const { knowledgeType, id } = req.params;
      
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new BadRequestError('无效的知识条目ID');
      }
      
      const result = await reviewService.getReviewHistory(knowledgeType, id);
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('获取审核历史失败', { 
        error: (error as Error).message, 
        knowledgeType: req.params.knowledgeType,
        id: req.params.id
      });
      
      if (error instanceof BadRequestError) {
        return res.status(400).json({
          success: false,
          message: error.message
        });
      }
      
      if (error instanceof NotFoundError) {
        return res.status(404).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 获取审核详情
   * @route GET /api/reviews/:reviewId
   */
  async getReviewDetails(req: Request, res: Response) {
    try {
      const { reviewId } = req.params;
      
      if (!mongoose.Types.ObjectId.isValid(reviewId)) {
        throw new BadRequestError('无效的审核ID');
      }
      
      const result = await reviewService.getReviewById(reviewId);
      
      if (!result) {
        throw new NotFoundError('未找到审核记录');
      }
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('获取审核详情失败', { 
        error: (error as Error).message, 
        reviewId: req.params.reviewId
      });
      
      if (error instanceof BadRequestError) {
        return res.status(400).json({
          success: false,
          message: error.message
        });
      }
      
      if (error instanceof NotFoundError) {
        return res.status(404).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }
}

export default new ReviewController();