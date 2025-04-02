/**
 * 日常活动控制器
 * 处理与用户日常活动相关的API请求
 */
const DailyActivitiesService = require('../services/dailyActivities.service');
const { logger } = require('../utils/logger');
const { ValidationError, NotFoundError, DatabaseError } = require('../utils/errors');

/**
 * 日常活动控制器类
 */
class DailyActivitiesController {
  constructor() {
    this.service = new DailyActivitiesService();
    logger.info('日常活动控制器初始化完成');
  }

  /**
   * 获取活动摘要
   * @param {Object} request - 请求对象
   * @param {Object} reply - 响应对象
   * @returns {Promise<Object>} 活动摘要数据
   */
  getActivitySummary = async (request, reply) => {
    try {
      const { userId } = request.params;
      const { period = 'day' } = request.query;
      
      logger.info('获取活动摘要', { userId, period });
      
      // 验证时间段参数
      if (period && !['day', 'week', 'month'].includes(period)) {
        throw new ValidationError('无效的时间段参数', { period });
      }
      
      const summary = await this.service.getActivitySummary(userId, period);
      return summary;
    } catch (error) {
      logger.error('获取活动摘要处理失败', { 
        error: error.message,
        stack: error.stack
      });
      throw error;
    }
  };

  /**
   * 获取活动详情
   * @param {Object} request - 请求对象
   * @param {Object} reply - 响应对象
   * @returns {Promise<Object>} 活动详情数据
   */
  getActivityDetail = async (request, reply) => {
    try {
      const { userId, activityId } = request.params;
      
      logger.info('获取活动详情', { userId, activityId });
      
      if (!activityId) {
        throw new ValidationError('缺少活动ID参数');
      }
      
      const activity = await this.service.getActivityDetail(userId, activityId);
      return activity;
    } catch (error) {
      logger.error('获取活动详情处理失败', { 
        error: error.message,
        stack: error.stack
      });
      throw error;
    }
  };

  /**
   * 记录新活动
   * @param {Object} request - 请求对象
   * @param {Object} reply - 响应对象
   * @returns {Promise<Object>} 新创建的活动数据
   */
  recordActivity = async (request, reply) => {
    try {
      const { userId } = request.params;
      const activityData = request.body;
      
      logger.info('记录新活动', { userId, activityType: activityData?.type });
      
      // 验证请求体
      if (!activityData || Object.keys(activityData).length === 0) {
        throw new ValidationError('缺少活动数据');
      }
      
      // 基础字段验证
      const requiredFields = ['type', 'description', 'duration'];
      const missingFields = requiredFields.filter(field => !activityData[field]);
      
      if (missingFields.length > 0) {
        throw new ValidationError('缺少必要的活动字段', { missingFields });
      }
      
      const activity = await this.service.recordActivity(userId, activityData);
      return activity;
    } catch (error) {
      logger.error('记录活动处理失败', { 
        error: error.message,
        stack: error.stack
      });
      throw error;
    }
  };

  /**
   * 获取活动建议
   * @param {Object} request - 请求对象
   * @param {Object} reply - 响应对象
   * @returns {Promise<Array>} 活动建议列表
   */
  getActivityRecommendations = async (request, reply) => {
    try {
      const { userId } = request.params;
      
      logger.info('获取活动建议', { userId });
      
      const recommendations = await this.service.getActivityRecommendations(userId);
      return recommendations;
    } catch (error) {
      logger.error('获取活动建议处理失败', { 
        error: error.message,
        stack: error.stack
      });
      throw error;
    }
  };
}

module.exports = DailyActivitiesController; 