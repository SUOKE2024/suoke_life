/**
 * 生活方式控制器
 * 处理与用户生活方式相关的API请求
 */

const { createError } = require('../utils/error-handler');
const logger = require('../utils/logger');

class LifestyleController {
  constructor(lifestyleService) {
    this.lifestyleService = lifestyleService;
    
    // 绑定方法到实例
    this.getDietaryHabitsAnalysis = this.getDietaryHabitsAnalysis.bind(this);
    this.getLifestyleAnalysis = this.getLifestyleAnalysis.bind(this);
    this.getSeasonalLifestyleGuidance = this.getSeasonalLifestyleGuidance.bind(this);
    this.updateLifestyleSettings = this.updateLifestyleSettings.bind(this);
    
    logger.info('生活方式控制器初始化完成');
  }
  
  /**
   * 获取用户饮食习惯分析
   * @param {Request} req - Express请求对象
   * @param {Response} res - Express响应对象
   * @param {NextFunction} next - Express下一个中间件函数
   */
  async getDietaryHabitsAnalysis(req, res, next) {
    try {
      const { userId } = req.params;
      const { period = 'month' } = req.query;
      
      // 调用服务获取饮食习惯分析
      const dietaryAnalysis = await this.lifestyleService.getDietaryHabitsAnalysis(userId, period);
      
      // 返回结果
      return res.json(dietaryAnalysis);
    } catch (error) {
      logger.error(`获取用户饮食习惯分析失败: ${error.message}`, { userId: req.params.userId });
      
      // 如果是已知错误类型，直接传递给错误处理中间件
      if (error.isCustom) {
        return next(error);
      }
      
      // 未知错误，创建通用错误并传递
      return next(createError(
        'dietary_habits_analysis_failed',
        '获取用户饮食习惯分析失败',
        500
      ));
    }
  }
  
  /**
   * 获取生活方式综合分析
   * @param {Request} req - Express请求对象
   * @param {Response} res - Express响应对象
   * @param {NextFunction} next - Express下一个中间件函数
   */
  async getLifestyleAnalysis(req, res, next) {
    try {
      const { userId } = req.params;
      
      // 调用服务获取生活方式综合分析
      const lifestyleAnalysis = await this.lifestyleService.getLifestyleAnalysis(userId);
      
      // 返回结果
      return res.json(lifestyleAnalysis);
    } catch (error) {
      logger.error(`获取用户生活方式分析失败: ${error.message}`, { userId: req.params.userId });
      
      // 如果是已知错误类型，直接传递给错误处理中间件
      if (error.isCustom) {
        return next(error);
      }
      
      // 未知错误，创建通用错误并传递
      return next(createError(
        'lifestyle_analysis_failed',
        '获取用户生活方式分析失败',
        500
      ));
    }
  }
  
  /**
   * 获取季节性生活调整建议
   * @param {Request} req - Express请求对象
   * @param {Response} res - Express响应对象
   * @param {NextFunction} next - Express下一个中间件函数
   */
  async getSeasonalLifestyleGuidance(req, res, next) {
    try {
      const { userId } = req.params;
      
      // 调用服务获取季节性生活调整建议
      const seasonalGuidance = await this.lifestyleService.getSeasonalLifestyleGuidance(userId);
      
      // 返回结果
      return res.json(seasonalGuidance);
    } catch (error) {
      logger.error(`获取季节性生活调整建议失败: ${error.message}`, { userId: req.params.userId });
      
      // 如果是已知错误类型，直接传递给错误处理中间件
      if (error.isCustom) {
        return next(error);
      }
      
      // 未知错误，创建通用错误并传递
      return next(createError(
        'seasonal_guidance_failed',
        '获取季节性生活调整建议失败',
        500
      ));
    }
  }
  
  /**
   * 更新用户生活方式设置
   * @param {Request} req - Express请求对象
   * @param {Response} res - Express响应对象
   * @param {NextFunction} next - Express下一个中间件函数
   */
  async updateLifestyleSettings(req, res, next) {
    try {
      const { userId } = req.params;
      const settings = req.body;
      
      // 验证请求体
      if (!settings || typeof settings !== 'object') {
        return next(createError(
          'invalid_settings',
          '无效的设置数据',
          400
        ));
      }
      
      // 调用服务更新生活方式设置
      const result = await this.lifestyleService.updateLifestyleSettings(userId, settings);
      
      // 返回结果
      return res.json(result);
    } catch (error) {
      logger.error(`更新生活方式设置失败: ${error.message}`, { userId: req.params.userId });
      
      // 如果是已知错误类型，直接传递给错误处理中间件
      if (error.isCustom) {
        return next(error);
      }
      
      // 未知错误，创建通用错误并传递
      return next(createError(
        'update_lifestyle_settings_failed',
        '更新生活方式设置失败',
        500
      ));
    }
  }
}

module.exports = LifestyleController; 