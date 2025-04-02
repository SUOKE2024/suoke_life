import mongoose from 'mongoose';
import { logger } from '../../utils/logger';
import { Subscription } from '../../core/agent/types';
import { getCache, setCache } from '../../core/cache';
import { SubscriptionModel, SubscriptionStatus } from '../../models/subscription.model';
import { serviceSubscriptionCounter } from '../../core/metrics';

// 缓存配置
const SUBSCRIPTION_CACHE_TTL = parseInt(process.env.SUBSCRIPTION_CACHE_TTL || '3600', 10); // 默认1小时

/**
 * 订阅服务类
 * 负责管理用户服务订阅
 */
export class SubscriptionService {
  /**
   * 创建新订阅
   */
  async createSubscription(subscriptionData: Omit<Subscription, 'id'>): Promise<Subscription> {
    try {
      // 创建订阅记录
      const subscription = await SubscriptionModel.create(subscriptionData);
      
      // 更新指标
      serviceSubscriptionCounter.inc({
        service_type: subscription.serviceType,
        duration: subscription.billingCycle,
        status: subscription.status
      });
      
      // 返回结果
      return {
        id: subscription._id.toString(),
        userId: subscription.userId,
        serviceName: subscription.serviceName,
        serviceType: subscription.serviceType,
        status: subscription.status,
        startDate: subscription.startDate,
        endDate: subscription.endDate,
        price: subscription.price,
        billingCycle: subscription.billingCycle,
        autoRenew: subscription.autoRenew,
        details: subscription.details,
        metadata: subscription.metadata
      };
    } catch (error) {
      logger.error('创建订阅失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取订阅详情
   */
  async getSubscriptionById(subscriptionId: string): Promise<Subscription | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = `subscription:${subscriptionId}`;
      const cachedSubscription = await getCache<Subscription>(cacheKey);
      
      if (cachedSubscription) {
        logger.debug(`从缓存获取订阅信息: ${subscriptionId}`);
        return cachedSubscription;
      }
      
      // 从数据库获取
      const subscription = await SubscriptionModel.findById(subscriptionId).lean();
      
      if (!subscription) {
        logger.debug(`订阅不存在: ${subscriptionId}`);
        return null;
      }
      
      // 转换为Subscription类型
      const subscriptionInfo: Subscription = {
        id: subscription._id.toString(),
        userId: subscription.userId,
        serviceName: subscription.serviceName,
        serviceType: subscription.serviceType,
        status: subscription.status,
        startDate: subscription.startDate,
        endDate: subscription.endDate,
        price: subscription.price,
        billingCycle: subscription.billingCycle,
        autoRenew: subscription.autoRenew,
        details: subscription.details,
        metadata: subscription.metadata
      };
      
      // 更新缓存
      await setCache(cacheKey, subscriptionInfo, SUBSCRIPTION_CACHE_TTL);
      
      return subscriptionInfo;
    } catch (error) {
      logger.error(`获取订阅信息失败:`, error);
      throw error;
    }
  }
  
  /**
   * 获取用户的所有订阅
   */
  async getUserSubscriptions(userId: string): Promise<Subscription[]> {
    try {
      // 尝试从缓存获取
      const cacheKey = `subscriptions:user:${userId}`;
      const cachedSubscriptions = await getCache<Subscription[]>(cacheKey);
      
      if (cachedSubscriptions) {
        logger.debug(`从缓存获取用户订阅列表: ${userId}`);
        return cachedSubscriptions;
      }
      
      // 从数据库获取
      const subscriptions = await SubscriptionModel.find({ userId }).lean();
      
      // 转换为Subscription类型
      const subscriptionInfos = subscriptions.map(subscription => ({
        id: subscription._id.toString(),
        userId: subscription.userId,
        serviceName: subscription.serviceName,
        serviceType: subscription.serviceType,
        status: subscription.status,
        startDate: subscription.startDate,
        endDate: subscription.endDate,
        price: subscription.price,
        billingCycle: subscription.billingCycle,
        autoRenew: subscription.autoRenew,
        details: subscription.details,
        metadata: subscription.metadata
      }));
      
      // 更新缓存
      await setCache(cacheKey, subscriptionInfos, SUBSCRIPTION_CACHE_TTL);
      
      return subscriptionInfos;
    } catch (error) {
      logger.error(`获取用户订阅列表失败:`, error);
      throw error;
    }
  }
  
  /**
   * 更新订阅状态
   */
  async updateSubscriptionStatus(subscriptionId: string, status: string): Promise<Subscription | null> {
    try {
      // 验证状态值
      if (!Object.values(SubscriptionStatus).includes(status as SubscriptionStatus)) {
        throw new Error(`无效的订阅状态: ${status}`);
      }

      // 更新数据库
      const subscription = await SubscriptionModel.findByIdAndUpdate(
        subscriptionId,
        { status },
        { new: true }
      ).lean();

      if (!subscription) {
        logger.debug(`订阅不存在: ${subscriptionId}`);
        return null;
      }
      
      // 转换为Subscription类型
      const subscriptionInfo: Subscription = {
        id: subscription._id.toString(),
        userId: subscription.userId,
        serviceName: subscription.serviceName,
        serviceType: subscription.serviceType,
        status: subscription.status,
        startDate: subscription.startDate,
        endDate: subscription.endDate,
        price: subscription.price,
        billingCycle: subscription.billingCycle,
        autoRenew: subscription.autoRenew,
        details: subscription.details,
        metadata: subscription.metadata
      };
      
      // 清除缓存
      const cacheKey = `subscription:${subscriptionId}`;
      await setCache(cacheKey, null, 1);
      await setCache(`subscriptions:user:${subscription.userId}`, null, 1);
      
      // 更新指标
      serviceSubscriptionCounter.inc({
        service_type: subscription.serviceType,
        duration: subscription.billingCycle,
        status: subscription.status
      });
      
      return subscriptionInfo;
    } catch (error) {
      logger.error(`更新订阅状态失败:`, error);
      throw error;
    }
  }
  
  /**
   * 续订服务
   */
  async renewSubscription(subscriptionId: string, duration: string): Promise<Subscription | null> {
    const session = await mongoose.startSession();
    session.startTransaction();

    try {
      // 获取当前订阅
      const currentSubscription = await SubscriptionModel.findById(subscriptionId).session(session);

      if (!currentSubscription) {
        await session.abortTransaction();
        session.endSession();
        logger.debug(`订阅不存在: ${subscriptionId}`);
        return null;
      }

      // 计算新的结束日期
      const currentEndDate = new Date(currentSubscription.endDate);
      let newEndDate = new Date(currentEndDate);

      switch (duration) {
        case 'monthly':
          newEndDate.setMonth(newEndDate.getMonth() + 1);
          break;
        case 'quarterly':
          newEndDate.setMonth(newEndDate.getMonth() + 3);
          break;
        case 'semi_annual':
          newEndDate.setMonth(newEndDate.getMonth() + 6);
          break;
        case 'annual':
          newEndDate.setFullYear(newEndDate.getFullYear() + 1);
          break;
        default:
          throw new Error(`无效的续订周期: ${duration}`);
      }

      // 更新订阅
      const updatedSubscription = await SubscriptionModel.findByIdAndUpdate(
        subscriptionId,
        {
          endDate: newEndDate.toISOString().split('T')[0],
          status: SubscriptionStatus.ACTIVE,
          billingCycle: duration
        },
        { new: true, session }
      ).lean();

      await session.commitTransaction();
      session.endSession();

      if (!updatedSubscription) {
        logger.error(`续订失败: ${subscriptionId}`);
        return null;
      }

      // 转换为Subscription类型
      const subscriptionInfo: Subscription = {
        id: updatedSubscription._id.toString(),
        userId: updatedSubscription.userId,
        serviceName: updatedSubscription.serviceName,
        serviceType: updatedSubscription.serviceType,
        status: updatedSubscription.status,
        startDate: updatedSubscription.startDate,
        endDate: updatedSubscription.endDate,
        price: updatedSubscription.price,
        billingCycle: updatedSubscription.billingCycle,
        autoRenew: updatedSubscription.autoRenew,
        details: updatedSubscription.details,
        metadata: updatedSubscription.metadata
      };

      // 清除缓存
      const cacheKey = `subscription:${subscriptionId}`;
      await setCache(cacheKey, null, 1);
      await setCache(`subscriptions:user:${updatedSubscription.userId}`, null, 1);

      // 更新指标
      serviceSubscriptionCounter.inc({
        service_type: updatedSubscription.serviceType,
        duration: updatedSubscription.billingCycle,
        status: updatedSubscription.status
      });

      return subscriptionInfo;
    } catch (error) {
      await session.abortTransaction();
      session.endSession();
      logger.error(`续订服务失败:`, error);
      throw error;
    }
  }
  
  /**
   * 取消自动续订
   */
  async cancelAutoRenew(subscriptionId: string): Promise<Subscription | null> {
    try {
      // 更新订阅自动续订状态
      const subscription = await SubscriptionModel.findByIdAndUpdate(
        subscriptionId,
        { autoRenew: false },
        { new: true }
      ).lean();
      
      if (!subscription) {
        logger.debug(`订阅不存在: ${subscriptionId}`);
        return null;
      }
      
      // 清除缓存
      const cacheKey = `subscription:${subscriptionId}`;
      await setCache(cacheKey, null, 1);
      
      // 转换为Subscription类型
      const subscriptionInfo: Subscription = {
        id: subscription._id.toString(),
        userId: subscription.userId,
        serviceName: subscription.serviceName,
        serviceType: subscription.serviceType,
        status: subscription.status,
        startDate: subscription.startDate,
        endDate: subscription.endDate,
        price: subscription.price,
        billingCycle: subscription.billingCycle,
        autoRenew: subscription.autoRenew,
        details: subscription.details,
        metadata: subscription.metadata
      };
      
      return subscriptionInfo;
    } catch (error) {
      logger.error(`取消自动续订失败:`, error);
      throw error;
    }
  }
}

export default new SubscriptionService();