/**
 * 推荐控制器
 * 处理健康和生活建议推荐的API请求控制
 */

const { createError } = require('../utils/error-handler');
const logger = require('../utils/logger');

class RecommendationsController {
  constructor(recommendationsService) {
    this.recommendationsService = recommendationsService;
    this.getUserRecommendations = this.getUserRecommendations.bind(this);
    this.getRecommendationDetail = this.getRecommendationDetail.bind(this);
    this.getDailyAdvice = this.getDailyAdvice.bind(this);
    this.provideRecommendationFeedback = this.provideRecommendationFeedback.bind(this);
    
    logger.info('推荐控制器初始化完成');
  }
  
  /**
   * 获取用户个性化推荐
   * @param {Request} req - Express请求对象
   * @param {Response} res - Express响应对象
   * @param {NextFunction} next - Express下一个中间件函数
   */
  async getUserRecommendations(req, res, next) {
    try {
      const { userId } = req.params;
      const { category = 'all', count = 5 } = req.query;
      
      // 调用推荐服务获取个性化推荐
      const recommendations = await this.recommendationsService.getUserRecommendations(userId, {
        category,
        count: parseInt(count, 10)
      });
      
      // 返回结果
      return res.json(recommendations);
    } catch (error) {
      logger.error(`获取用户推荐失败: ${error.message}`, { userId: req.params.userId });
      
      // 如果是已知错误类型，直接传递给错误处理中间件
      if (error.isCustom) {
        return next(error);
      }
      
      // 未知错误，创建通用错误并传递
      return next(createError(
        'recommendation_retrieval_failed',
        '获取用户推荐失败',
        500
      ));
    }
  }
  
  /**
   * 获取推荐详情
   * @param {Request} req - Express请求对象
   * @param {Response} res - Express响应对象
   * @param {NextFunction} next - Express下一个中间件函数
   */
  async getRecommendationDetail(req, res, next) {
    try {
      const { userId, recommendationId } = req.params;
      
      // 调用推荐服务获取推荐详情
      const detail = await this.recommendationsService.getRecommendationDetail(userId, recommendationId);
      
      // 返回结果
      return res.json(detail);
    } catch (error) {
      logger.error(`获取推荐详情失败: ${error.message}`, {
        userId: req.params.userId,
        recommendationId: req.params.recommendationId
      });
      
      // 如果是已知错误类型，直接传递给错误处理中间件
      if (error.isCustom) {
        return next(error);
      }
      
      // 未知错误，创建通用错误并传递
      return next(createError(
        'recommendation_detail_retrieval_failed',
        '获取推荐详情失败',
        500
      ));
    }
  }
  
  /**
   * 获取每日建议
   * @param {Request} req - Express请求对象
   * @param {Response} res - Express响应对象
   * @param {NextFunction} next - Express下一个中间件函数
   */
  async getDailyAdvice(req, res, next) {
    try {
      const { userId } = req.params;
      
      // 调用推荐服务获取每日建议
      const dailyAdvice = await this.recommendationsService.getDailyAdvice(userId);
      
      // 返回结果
      return res.json(dailyAdvice);
    } catch (error) {
      logger.error(`获取每日建议失败: ${error.message}`, { userId: req.params.userId });
      
      // 如果是已知错误类型，直接传递给错误处理中间件
      if (error.isCustom) {
        return next(error);
      }
      
      // 未知错误，创建通用错误并传递
      return next(createError(
        'daily_advice_retrieval_failed',
        '获取每日建议失败',
        500
      ));
    }
  }
  
  /**
   * 提供推荐反馈
   * @param {Request} req - Express请求对象
   * @param {Response} res - Express响应对象
   * @param {NextFunction} next - Express下一个中间件函数
   */
  async provideRecommendationFeedback(req, res, next) {
    try {
      const { userId, recommendationId } = req.params;
      const feedback = req.body;
      
      // 验证反馈数据
      if (!feedback || typeof feedback !== 'object') {
        return next(createError(
          'invalid_feedback',
          '无效的反馈数据',
          400
        ));
      }
      
      // 调用推荐服务记录反馈
      const result = await this.recommendationsService.provideRecommendationFeedback(
        userId,
        recommendationId,
        feedback
      );
      
      // 返回结果
      return res.json(result);
    } catch (error) {
      logger.error(`处理推荐反馈失败: ${error.message}`, {
        userId: req.params.userId,
        recommendationId: req.params.recommendationId
      });
      
      // 如果是已知错误类型，直接传递给错误处理中间件
      if (error.isCustom) {
        return next(error);
      }
      
      // 未知错误，创建通用错误并传递
      return next(createError(
        'feedback_processing_failed',
        '处理推荐反馈失败',
        500
      ));
    }
  }
}

module.exports = RecommendationsController; 