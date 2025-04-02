/**
 * 知识审核服务
 * 管理知识条目的审核流程
 */
import mongoose from 'mongoose';
import { NotFoundError } from '../errors/not-found-error';
import { BadRequestError } from '../errors/bad-request-error';
import logger from '../utils/logger';
import ReviewModel from '../models/review.model';
import versionService from './version.service';

export class ReviewService {
  /**
   * 提交知识条目审核
   * @param knowledgeType 知识类型
   * @param documentId 知识条目ID
   * @param userId 提交者ID
   * @param comments 提交备注
   * @returns 审核记录
   */
  async submitForReview(
    knowledgeType: string, 
    documentId: string, 
    userId: string,
    comments?: string
  ): Promise<any> {
    try {
      logger.info('提交知识条目审核', { knowledgeType, documentId, userId });
      
      // 检查是否已有待审核的记录
      const existingReview = await ReviewModel.findOne({
        knowledgeType,
        documentId,
        status: 'pending'
      });
      
      if (existingReview) {
        throw new BadRequestError('该知识条目已有待审核的记录');
      }
      
      // 获取知识条目数据
      const data = await versionService.getSpecificVersion(knowledgeType, documentId, -1);
      
      if (!data) {
        throw new NotFoundError(`未找到${knowledgeType}知识条目`);
      }
      
      // 创建审核记录
      const review = new ReviewModel({
        knowledgeType,
        documentId,
        documentVersion: data.version,
        submittedBy: userId,
        submittedAt: new Date(),
        status: 'pending',
        submitterComments: comments || '',
        content: JSON.parse(JSON.stringify(data)) // 深拷贝数据
      });
      
      await review.save();
      
      logger.info('审核记录已创建', { reviewId: review._id });
      
      return review;
    } catch (error) {
      logger.error('提交审核失败', { 
        error: (error as Error).message, 
        knowledgeType, 
        documentId, 
        userId 
      });
      throw error;
    }
  }

  /**
   * 审核通过
   * @param reviewId 审核ID
   * @param reviewerId 审核者ID
   * @param comments 审核备注
   * @returns 更新后的审核记录
   */
  async approveReview(reviewId: string, reviewerId: string, comments?: string): Promise<any> {
    try {
      logger.info('审核通过', { reviewId, reviewerId });
      
      // 查找审核记录
      const review = await ReviewModel.findById(reviewId);
      
      if (!review) {
        throw new NotFoundError('未找到审核记录');
      }
      
      if (review.status !== 'pending') {
        throw new BadRequestError('该审核记录已处理');
      }
      
      // 更新审核记录
      review.status = 'approved';
      review.reviewedBy = reviewerId;
      review.reviewedAt = new Date();
      review.reviewerComments = comments || '';
      
      await review.save();
      
      logger.info('审核已通过并更新状态', { reviewId });
      
      return review;
    } catch (error) {
      logger.error('审核通过处理失败', { 
        error: (error as Error).message, 
        reviewId, 
        reviewerId 
      });
      throw error;
    }
  }

  /**
   * 拒绝审核
   * @param reviewId 审核ID
   * @param reviewerId 审核者ID
   * @param comments 拒绝原因
   * @returns 更新后的审核记录
   */
  async rejectReview(reviewId: string, reviewerId: string, comments: string): Promise<any> {
    try {
      logger.info('拒绝审核', { reviewId, reviewerId });
      
      // 查找审核记录
      const review = await ReviewModel.findById(reviewId);
      
      if (!review) {
        throw new NotFoundError('未找到审核记录');
      }
      
      if (review.status !== 'pending') {
        throw new BadRequestError('该审核记录已处理');
      }
      
      if (!comments) {
        throw new BadRequestError('拒绝审核必须提供理由');
      }
      
      // 更新审核记录
      review.status = 'rejected';
      review.reviewedBy = reviewerId;
      review.reviewedAt = new Date();
      review.reviewerComments = comments;
      
      await review.save();
      
      logger.info('审核已拒绝并更新状态', { reviewId });
      
      return review;
    } catch (error) {
      logger.error('拒绝审核处理失败', { 
        error: (error as Error).message, 
        reviewId, 
        reviewerId 
      });
      throw error;
    }
  }

  /**
   * 获取审核记录
   * @param filter 过滤条件
   * @param page 页码
   * @param limit 每页数量
   * @returns 审核记录列表和分页信息
   */
  async getReviews(filter: any = {}, page: number = 1, limit: number = 20): Promise<{
    data: any[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    try {
      logger.info('获取审核记录', { filter, page, limit });
      
      // 确保页码和限制是有效的数字
      const validPage = Math.max(1, page);
      const validLimit = Math.max(1, Math.min(100, limit)); // 限制最大为100
      
      // 计算跳过的文档数量
      const skip = (validPage - 1) * validLimit;
      
      // 查询数据库
      const [data, total] = await Promise.all([
        ReviewModel.find(filter)
          .sort({ submittedAt: -1 })
          .skip(skip)
          .limit(validLimit),
        ReviewModel.countDocuments(filter)
      ]);
      
      // 计算总页数
      const totalPages = Math.ceil(total / validLimit);
      
      return {
        data,
        total,
        page: validPage,
        limit: validLimit,
        totalPages
      };
    } catch (error) {
      logger.error('获取审核记录失败', { 
        error: (error as Error).message, 
        filter
      });
      throw error;
    }
  }

  /**
   * 获取知识条目的审核历史
   * @param knowledgeType 知识类型
   * @param documentId 知识条目ID
   * @returns 审核历史列表
   */
  async getReviewHistory(knowledgeType: string, documentId: string): Promise<any[]> {
    try {
      logger.info('获取审核历史', { knowledgeType, documentId });
      
      // 查询数据库
      const reviews = await ReviewModel.find({
        knowledgeType,
        documentId
      }).sort({ submittedAt: -1 });
      
      return reviews;
    } catch (error) {
      logger.error('获取审核历史失败', { 
        error: (error as Error).message, 
        knowledgeType, 
        documentId
      });
      throw error;
    }
  }

  /**
   * 根据ID获取审核记录
   * @param reviewId 审核ID
   * @returns 审核记录
   */
  async getReviewById(reviewId: string): Promise<any> {
    try {
      logger.info('获取审核记录详情', { reviewId });
      
      // if (!mongoose.Types.ObjectId.isValid(reviewId)) {
      //   throw new BadRequestError('无效的审核ID');
      // }
      
      // 查询数据库
      const review = await ReviewModel.findById(reviewId);
      
      if (!review) {
        throw new NotFoundError('未找到审核记录');
      }
      
      return review;
    } catch (error) {
      logger.error('获取审核记录详情失败', { 
        error: (error as Error).message, 
        reviewId
      });
      throw error;
    }
  }
}

export default new ReviewService();