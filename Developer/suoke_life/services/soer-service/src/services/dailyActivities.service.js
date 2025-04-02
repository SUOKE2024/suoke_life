/**
 * 日常活动服务
 * 处理与用户日常活动相关的业务逻辑
 */
const { v4: uuidv4 } = require('uuid');
const { logger } = require('../utils/logger');
const { 
  NotFoundError, 
  ValidationError, 
  DatabaseError
} = require('../utils/errors');
const dbService = require('../models/db.service');
const { 
  ACTIVITIES_TABLE, 
  ACTIVITY_METRICS_TABLE,
  formatActivityForDb,
  formatActivityForApi
} = require('../models/dailyActivities.model');

// TODO: 待删除的模拟数据代码，保留一段时间用于开发参考
// 模拟活动类型
const ACTIVITY_TYPES = {
  WALKING: 'walking',
  RUNNING: 'running',
  CYCLING: 'cycling',
  SWIMMING: 'swimming',
  YOGA: 'yoga',
  MEDITATION: 'meditation',
  EXERCISE: 'exercise'
};

/**
 * 日常活动服务类
 */
class DailyActivitiesService {
  constructor() {
    this.db = dbService;
    // 确保应用启动时已初始化数据库连接
    this._initDatabase();
  }

  /**
   * 初始化数据库连接
   * @private
   */
  async _initDatabase() {
    try {
      await this.db.connect();
    } catch (error) {
      logger.error('初始化日常活动服务数据库连接失败', { error: error.message });
      // 初始化失败不阻止服务启动，后续操作会重试连接
    }
  }

  /**
   * 获取用户活动摘要
   * @param {string} userId - 用户ID
   * @param {string} period - 时间段 (day, week, month)
   * @returns {Promise<Object>} 活动摘要数据
   */
  async getActivitySummary(userId, period = 'day') {
    try {
      logger.info('获取用户活动摘要', { userId, period });
      
      // 验证时间段参数
      if (!['day', 'week', 'month'].includes(period)) {
        throw new ValidationError('无效的时间段参数', { period });
      }

      // 获取当前日期
      const currentDate = new Date();
      
      // 查询数据库中的活动指标
      const metrics = await this.db.find(ACTIVITY_METRICS_TABLE, {
        user_id: userId,
        period: period
      }, {
        // 按日期降序排序，获取最新记录
        sort: 'date DESC',
        limit: 1
      });

      // 如果找到了指标记录
      if (metrics && metrics.length > 0) {
        const metricData = metrics[0];
        
        // 解析JSON字段
        let activityBreakdown = metricData.activity_breakdown;
        if (typeof activityBreakdown === 'string') {
          try {
            activityBreakdown = JSON.parse(activityBreakdown);
          } catch (e) {
            activityBreakdown = [];
          }
        }

        return {
          userId,
          period,
          date: metricData.date,
          totalActivities: metricData.total_activities || 0,
          totalDuration: metricData.total_duration || 0,
          totalDistance: metricData.total_distance || 0,
          totalCalories: metricData.total_calories || 0,
          activityBreakdown: activityBreakdown || [],
          lastUpdated: metricData.updated_at
        };
      }

      // 如果没有指标记录，从原始活动数据计算
      // 确定时间范围
      let startDate;
      const endDate = new Date(currentDate);
      
      if (period === 'day') {
        startDate = new Date(currentDate);
        startDate.setHours(0, 0, 0, 0);
      } else if (period === 'week') {
        startDate = new Date(currentDate);
        startDate.setDate(startDate.getDate() - startDate.getDay());
        startDate.setHours(0, 0, 0, 0);
      } else if (period === 'month') {
        startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      }
      
      // 查询指定时间范围内的活动
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];
      
      const activities = await this.db.query(
        `SELECT * FROM ${ACTIVITIES_TABLE} 
         WHERE user_id = ? 
         AND DATE(start_time) >= ? 
         AND DATE(start_time) <= ?
         ORDER BY start_time DESC`,
        [userId, startDateStr, endDateStr]
      );
      
      // 如果没有活动记录，返回空摘要
      if (!activities || activities.length === 0) {
        return {
          userId,
          period,
          date: currentDate,
          totalActivities: 0,
          totalDuration: 0,
          totalDistance: 0,
          totalCalories: 0,
          activityBreakdown: [],
          lastUpdated: currentDate
        };
      }
      
      // 计算摘要数据
      let totalDuration = 0;
      let totalDistance = 0;
      let totalCalories = 0;
      const activityCounts = {};
      
      activities.forEach(activity => {
        totalDuration += activity.duration || 0;
        totalDistance += activity.distance || 0;
        totalCalories += activity.calories || 0;
        
        // 累计活动类型
        if (!activityCounts[activity.type]) {
          activityCounts[activity.type] = {
            type: activity.type,
            typeLabel: activity.type_label || activity.type,
            count: 0,
            duration: 0
          };
        }
        
        activityCounts[activity.type].count += 1;
        activityCounts[activity.type].duration += activity.duration || 0;
      });
      
      // 转换为数组
      const activityBreakdown = Object.values(activityCounts);
      
      // 创建指标记录用于缓存
      const newMetrics = {
        user_id: userId,
        date: currentDate,
        period: period,
        total_activities: activities.length,
        total_duration: totalDuration,
        total_distance: totalDistance,
        total_calories: totalCalories,
        activity_breakdown: JSON.stringify(activityBreakdown)
      };
      
      // 异步保存指标数据，不等待完成
      this.db.create(ACTIVITY_METRICS_TABLE, newMetrics)
        .catch(err => logger.error('保存活动指标失败', { error: err.message }));
      
      // 返回摘要数据
      return {
        userId,
        period,
        date: currentDate,
        totalActivities: activities.length,
        totalDuration: totalDuration,
        totalDistance: totalDistance,
        totalCalories: totalCalories,
        activityBreakdown: activityBreakdown,
        lastUpdated: currentDate
      };
    } catch (error) {
      logger.error('获取活动摘要失败', { userId, period, error: error.message });
      
      if (error instanceof ValidationError) {
        throw error;
      }
      
      throw new DatabaseError('获取活动摘要失败', { cause: error });
    }
  }

  /**
   * 获取活动详情
   * @param {string} userId - 用户ID
   * @param {string} activityId - 活动ID
   * @returns {Promise<Object>} 活动详情
   */
  async getActivityDetail(userId, activityId) {
    try {
      logger.info('获取活动详情', { userId, activityId });
      
      // 查询数据库
      const activity = await this.db.query(
        `SELECT * FROM ${ACTIVITIES_TABLE} WHERE id = ? AND user_id = ?`,
        [activityId, userId]
      );
      
      if (!activity || activity.length === 0) {
        throw new NotFoundError('未找到指定活动');
      }
      
      // 转换为API格式
      return formatActivityForApi(activity[0]);
    } catch (error) {
      logger.error('获取活动详情失败', { 
        userId, 
        activityId, 
        error: error.message 
      });
      
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      throw new DatabaseError('获取活动详情失败', { cause: error });
    }
  }

  /**
   * 记录新活动
   * @param {string} userId - 用户ID
   * @param {Object} activityData - 活动数据
   * @returns {Promise<Object>} 创建的活动
   */
  async recordActivity(userId, activityData) {
    try {
      logger.info('记录新活动', { userId });
      
      // 验证必要字段
      if (!activityData.type || !activityData.description || !activityData.duration) {
        throw new ValidationError('活动数据缺少必要字段', { 
          required: ['type', 'description', 'duration'] 
        });
      }
      
      // 验证活动类型
      const validTypes = ['walking', 'running', 'cycling', 'swimming', 'yoga', 'meditation', 'exercise', 'other'];
      if (!validTypes.includes(activityData.type)) {
        throw new ValidationError('无效的活动类型', { 
          type: activityData.type,
          allowedTypes: validTypes 
        });
      }
      
      // 准备数据
      const now = new Date();
      const newActivity = {
        ...activityData,
        userId: userId, // 确保使用路径参数中的用户ID
        createdAt: now,
        updatedAt: now
      };
      
      // 转换为数据库格式
      const dbActivity = formatActivityForDb(newActivity);
      
      // 保存到数据库
      const result = await this.db.create(ACTIVITIES_TABLE, dbActivity);
      
      // 转换回API格式
      return formatActivityForApi(result);
    } catch (error) {
      logger.error('记录活动失败', { userId, error: error.message });
      
      if (error instanceof ValidationError) {
        throw error;
      }
      
      throw new DatabaseError('记录活动失败', { cause: error });
    }
  }

  /**
   * 获取活动建议
   * @param {string} userId - 用户ID
   * @returns {Promise<Array>} 活动建议列表
   */
  async getActivityRecommendations(userId) {
    try {
      logger.info('获取活动建议', { userId });
      
      // 获取用户最近活动类型
      const recentActivities = await this.db.query(
        `SELECT type, COUNT(*) as count FROM ${ACTIVITIES_TABLE} 
         WHERE user_id = ? 
         GROUP BY type 
         ORDER BY count DESC 
         LIMIT 3`,
        [userId]
      );
      
      // 固定的建议列表
      const standardRecommendations = [
        {
          id: uuidv4(),
          type: 'walking',
          title: '晨间轻松散步',
          description: '早上进行20-30分钟的轻松散步，帮助促进血液循环，唤醒身体。',
          durationMinutes: 30,
          caloriesBurned: 120,
          benefits: ['改善心情', '增强新陈代谢', '促进血液循环'],
          bestTimeOfDay: '早晨',
          tcmPrinciples: ['疏通经络', '调和气血']
        },
        {
          id: uuidv4(),
          type: 'yoga',
          title: '平衡阴阳瑜伽',
          description: '结合呼吸与温和动作的瑜伽练习，平衡身体能量。',
          durationMinutes: 45,
          caloriesBurned: 180,
          benefits: ['提高柔韧性', '改善姿势', '减轻压力'],
          bestTimeOfDay: '黄昏',
          tcmPrinciples: ['调和阴阳', '舒筋活络']
        },
        {
          id: uuidv4(),
          type: 'meditation',
          title: '五行冥想',
          description: '基于五行理论的引导冥想，帮助平衡体内元素。',
          durationMinutes: 15,
          caloriesBurned: 20,
          benefits: ['减轻焦虑', '提高专注力', '改善睡眠'],
          bestTimeOfDay: '睡前',
          tcmPrinciples: ['宁心安神', '调理五脏']
        }
      ];
      
      // 根据用户喜好定制的建议
      let customRecommendations = [];
      
      // 如果有历史活动，则根据用户喜好提供更多相关建议
      if (recentActivities && recentActivities.length > 0) {
        const favoriteType = recentActivities[0].type;
        
        if (favoriteType === 'walking' || favoriteType === 'running') {
          customRecommendations.push({
            id: uuidv4(),
            type: favoriteType,
            title: favoriteType === 'walking' ? '五行散步疗法' : '调息慢跑',
            description: `结合传统五行理论的${favoriteType === 'walking' ? '散步' : '慢跑'}技巧，重点关注呼吸与步伐的协调。`,
            durationMinutes: favoriteType === 'walking' ? 40 : 25,
            caloriesBurned: favoriteType === 'walking' ? 160 : 250,
            benefits: ['排解压力', '增强肺活量', '调和气血'],
            bestTimeOfDay: '傍晚',
            tcmPrinciples: ['行气活血', '调节阴阳平衡']
          });
        } else if (favoriteType === 'yoga' || favoriteType === 'meditation') {
          customRecommendations.push({
            id: uuidv4(),
            type: favoriteType,
            title: favoriteType === 'yoga' ? '经络瑜伽' : '引导式经络冥想',
            description: `专注于主要经络的${favoriteType === 'yoga' ? '瑜伽姿势' : '冥想技巧'}，促进气血流通。`,
            durationMinutes: favoriteType === 'yoga' ? 50 : 20,
            caloriesBurned: favoriteType === 'yoga' ? 200 : 30,
            benefits: ['疏通经络', '平衡气血', '提升能量'],
            bestTimeOfDay: favoriteType === 'yoga' ? '早晨' : '晚上',
            tcmPrinciples: ['调和阴阳', '疏通经络']
          });
        }
      }
      
      // 组合建议
      const recommendations = [...customRecommendations, ...standardRecommendations];
      
      // 确保不返回太多建议
      return recommendations.slice(0, 5);
    } catch (error) {
      logger.error('获取活动建议失败', { userId, error: error.message });
      throw new DatabaseError('获取活动建议失败', { cause: error });
    }
  }
}

module.exports = DailyActivitiesService; 