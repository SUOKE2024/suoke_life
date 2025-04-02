import mongoose from 'mongoose';
import { logger } from '../../utils/logger';
import { FarmActivity, ActivityReview } from '../../core/agent/types';
import { getCache, setCache } from '../../core/cache';
import { ActivityModel, ActivityRegistrationModel } from '../../models/activity.model';
import { farmActivityCounter } from '../../core/metrics';

// 缓存配置
const ACTIVITY_CACHE_TTL = parseInt(process.env.ACTIVITY_CACHE_TTL || '3600', 10); // 默认1小时

/**
 * 活动服务类
 * 负责管理农事活动信息、预约和评价
 */
export class ActivityService {
  /**
   * 获取活动列表
   */
  async getActivities(options: {
    category?: string;
    query?: string;
    location?: string;
    startDate?: string;
    endDate?: string;
    sort?: string;
    limit?: number;
    skip?: number;
  }): Promise<{ activities: FarmActivity[]; total: number }> {
    try {
      const {
        category,
        query,
        location,
        startDate,
        endDate,
        sort = 'startDate_asc',
        limit = 20,
        skip = 0
      } = options;
      
      // 构建查询条件
      const filter: any = {};
      
      if (category) {
        filter.category = category;
      }
      
      if (query) {
        filter.$or = [
          { name: { $regex: query, $options: 'i' } },
          { description: { $regex: query, $options: 'i' } }
        ];
      }
      
      if (location) {
        filter.location = { $regex: location, $options: 'i' };
      }
      
      if (startDate) {
        filter.startDate = { $gte: startDate };
      }
      
      if (endDate) {
        filter.endDate = { $lte: endDate };
      }
      
      // 处理排序
      const [sortField, sortOrder] = sort.split('_');
      const sortOptions: any = {};
      sortOptions[sortField] = sortOrder === 'desc' ? -1 : 1;
      
      // 执行查询
      const total = await ActivityModel.countDocuments(filter);
      
      const activities = await ActivityModel.find(filter)
        .sort(sortOptions)
        .skip(skip)
        .limit(limit)
        .lean();
      
      // 转换结果
      const activityInfos = activities.map(activity => ({
        id: activity._id.toString(),
        name: activity.name,
        description: activity.description,
        location: activity.location,
        startDate: activity.startDate,
        endDate: activity.endDate,
        capacity: activity.capacity,
        currentRegistrations: activity.currentRegistrations,
        price: activity.price,
        category: activity.category,
        organizer: activity.organizer,
        contactInfo: activity.contactInfo,
        images: activity.images,
        requirements: activity.requirements,
        included: activity.included,
        reviews: activity.reviews,
        metadata: activity.metadata
      }));
      
      // 更新指标
      farmActivityCounter.inc({ 
        activity_type: category || 'all', 
        location: 'multiple', 
        status: 'view' 
      });
      
      return { activities: activityInfos, total };
    } catch (error) {
      logger.error(`获取活动列表失败:`, error);
      throw error;
    }
  }
  
  /**
   * 获取活动详情
   */
  async getActivityById(activityId: string): Promise<FarmActivity | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = `activity:${activityId}`;
      const cachedActivity = await getCache<FarmActivity>(cacheKey);
      
      if (cachedActivity) {
        logger.debug(`从缓存获取活动信息: ${activityId}`);
        
        // 更新指标
        farmActivityCounter.inc({
          activity_type: cachedActivity.category,
          location: cachedActivity.location,
          status: 'view'
        });
        
        return cachedActivity;
      }
      
      // 从数据库获取
      const activity = await ActivityModel.findById(activityId).lean();
      
      if (!activity) {
        logger.debug(`活动不存在: ${activityId}`);
        return null;
      }
      
      // 转换为FarmActivity类型
      const activityInfo: FarmActivity = {
        id: activity._id.toString(),
        name: activity.name,
        description: activity.description,
        location: activity.location,
        startDate: activity.startDate,
        endDate: activity.endDate,
        capacity: activity.capacity,
        currentRegistrations: activity.currentRegistrations,
        price: activity.price,
        category: activity.category,
        organizer: activity.organizer,
        contactInfo: activity.contactInfo,
        images: activity.images,
        requirements: activity.requirements,
        included: activity.included,
        reviews: activity.reviews,
        metadata: activity.metadata
      };
      
      // 更新缓存
      await setCache(cacheKey, activityInfo, ACTIVITY_CACHE_TTL);
      
      // 更新指标
      farmActivityCounter.inc({
        activity_type: activity.category,
        location: activity.location,
        status: 'view'
      });
      
      return activityInfo;
    } catch (error) {
      logger.error(`获取活动信息失败:`, error);
      throw error;
    }
  }
  
  /**
   * 预约活动
   */
  async registerForActivity(activityId: string, userId: string, participants: number): Promise<boolean> {
    try {
      // 使用事务确保原子性
      const session = await mongoose.startSession();
      session.startTransaction();
      
      try {
        // 查找活动
        const activity = await ActivityModel.findById(activityId).session(session);
        
        if (!activity) {
          throw new Error(`活动不存在: ${activityId}`);
        }
        
        // 检查是否已经注册
        const existingRegistration = await ActivityRegistrationModel.findOne({
          activityId,
          userId
        }).session(session);
        
        if (existingRegistration) {
          throw new Error('您已经预约过此活动');
        }
        
        // 检查容量
        if (activity.currentRegistrations + participants > activity.capacity) {
          throw new Error('活动名额不足');
        }
        
        // 创建预约记录
        await ActivityRegistrationModel.create([{
          activityId,
          userId,
          participants,
          registrationDate: new Date().toISOString(),
          status: 'confirmed'
        }], { session });
        
        // 更新活动当前注册人数
        await ActivityModel.findByIdAndUpdate(
          activityId,
          { $inc: { currentRegistrations: participants } },
          { session }
        );
        
        // 提交事务
        await session.commitTransaction();
        
        // 清除缓存
        const cacheKey = `activity:${activityId}`;
        await setCache(cacheKey, null, 1);
        
        // 更新指标
        farmActivityCounter.inc({
          activity_type: activity.category,
          location: activity.location,
          status: 'registered'
        });
        
        return true;
      } catch (error) {
        // 回滚事务
        await session.abortTransaction();
        throw error;
      } finally {
        // 结束会话
        session.endSession();
      }
    } catch (error) {
      logger.error(`预约活动失败:`, error);
      throw error;
    }
  }
  
  /**
   * 添加活动评价
   */
  async addActivityReview(activityId: string, review: Omit<ActivityReview, 'date'>): Promise<FarmActivity | null> {
    try {
      // 添加日期
      const reviewWithDate: ActivityReview = {
        ...review,
        date: new Date().toISOString()
      };
      
      // 更新活动评价
      const activity = await ActivityModel.findByIdAndUpdate(
        activityId,
        { $push: { reviews: reviewWithDate } },
        { new: true }
      ).lean();
      
      if (!activity) {
        logger.debug(`活动不存在: ${activityId}`);
        return null;
      }
      
      // 清除缓存
      const cacheKey = `activity:${activityId}`;
      await setCache(cacheKey, null, 1);
      
      // 转换为FarmActivity类型
      const activityInfo: FarmActivity = {
        id: activity._id.toString(),
        name: activity.name,
        description: activity.description,
        location: activity.location,
        startDate: activity.startDate,
        endDate: activity.endDate,
        capacity: activity.capacity,
        currentRegistrations: activity.currentRegistrations,
        price: activity.price,
        category: activity.category,
        organizer: activity.organizer,
        contactInfo: activity.contactInfo,
        images: activity.images,
        requirements: activity.requirements,
        included: activity.included,
        reviews: activity.reviews,
        metadata: activity.metadata
      };
      
      // 更新指标
      farmActivityCounter.inc({
        activity_type: activity.category,
        location: activity.location,
        status: 'reviewed'
      });
      
      return activityInfo;
    } catch (error) {
      logger.error(`添加活动评价失败:`, error);
      throw error;
    }
  }
  
  /**
   * 获取热门活动
   */
  async getPopularActivities(limit: number = 5): Promise<FarmActivity[]> {
    try {
      // 尝试从缓存获取
      const cacheKey = `activities:popular:limit:${limit}`;
      const cachedActivities = await getCache<FarmActivity[]>(cacheKey);
      
      if (cachedActivities) {
        logger.debug(`从缓存获取热门活动`);
        return cachedActivities;
      }
      
      // 查询热门活动 (基于注册人数百分比)
      const activities = await ActivityModel.aggregate([
        {
          $match: {
            startDate: { $gte: new Date().toISOString() }
          }
        },
        {
          $addFields: {
            registrationPercentage: {
              $multiply: [
                { $divide: ['$currentRegistrations', '$capacity'] },
                100
              ]
            }
          }
        },
        {
          $sort: { registrationPercentage: -1 }
        },
        {
          $limit: limit
        }
      ]);
      
      // 转换结果
      const activityInfos = activities.map(activity => ({
        id: activity._id.toString(),
        name: activity.name,
        description: activity.description,
        location: activity.location,
        startDate: activity.startDate,
        endDate: activity.endDate,
        capacity: activity.capacity,
        currentRegistrations: activity.currentRegistrations,
        price: activity.price,
        category: activity.category,
        organizer: activity.organizer,
        contactInfo: activity.contactInfo,
        images: activity.images,
        requirements: activity.requirements,
        included: activity.included,
        reviews: activity.reviews,
        metadata: activity.metadata
      }));
      
      // 更新缓存
      await setCache(cacheKey, activityInfos, ACTIVITY_CACHE_TTL);
      
      return activityInfos;
    } catch (error) {
      logger.error(`获取热门活动失败:`, error);
      throw error;
    }
  }
}

export default new ActivityService(); 