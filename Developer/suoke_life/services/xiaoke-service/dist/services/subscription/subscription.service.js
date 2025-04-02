"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SubscriptionService = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
const subscription_model_1 = require("../../models/subscription.model");
const metrics_1 = require("../../core/metrics");
// 缓存配置
const SUBSCRIPTION_CACHE_TTL = parseInt(process.env.SUBSCRIPTION_CACHE_TTL || '3600', 10); // 默认1小时
/**
 * 订阅服务类
 * 负责管理用户服务订阅
 */
class SubscriptionService {
    /**
     * 创建新订阅
     */
    async createSubscription(subscriptionData) {
        try {
            // 创建订阅记录
            const subscription = await subscription_model_1.SubscriptionModel.create(subscriptionData);
            // 更新指标
            metrics_1.serviceSubscriptionCounter.inc({
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
        }
        catch (error) {
            logger_1.logger.error('创建订阅失败:', error);
            throw error;
        }
    }
    /**
     * 获取订阅详情
     */
    async getSubscriptionById(subscriptionId) {
        try {
            // 尝试从缓存获取
            const cacheKey = `subscription:${subscriptionId}`;
            const cachedSubscription = await (0, cache_1.getCache)(cacheKey);
            if (cachedSubscription) {
                logger_1.logger.debug(`从缓存获取订阅信息: ${subscriptionId}`);
                return cachedSubscription;
            }
            // 从数据库获取
            const subscription = await subscription_model_1.SubscriptionModel.findById(subscriptionId).lean();
            if (!subscription) {
                logger_1.logger.debug(`订阅不存在: ${subscriptionId}`);
                return null;
            }
            // 转换为Subscription类型
            const subscriptionInfo = {
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
            await (0, cache_1.setCache)(cacheKey, subscriptionInfo, SUBSCRIPTION_CACHE_TTL);
            return subscriptionInfo;
        }
        catch (error) {
            logger_1.logger.error(`获取订阅信息失败:`, error);
            throw error;
        }
    }
    /**
     * 获取用户的所有订阅
     */
    async getUserSubscriptions(userId) {
        try {
            // 尝试从缓存获取
            const cacheKey = `subscriptions:user:${userId}`;
            const cachedSubscriptions = await (0, cache_1.getCache)(cacheKey);
            if (cachedSubscriptions) {
                logger_1.logger.debug(`从缓存获取用户订阅列表: ${userId}`);
                return cachedSubscriptions;
            }
            // 从数据库获取
            const subscriptions = await subscription_model_1.SubscriptionModel.find({ userId }).lean();
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
            await (0, cache_1.setCache)(cacheKey, subscriptionInfos, SUBSCRIPTION_CACHE_TTL);
            return subscriptionInfos;
        }
        catch (error) {
            logger_1.logger.error(`获取用户订阅列表失败:`, error);
            throw error;
        }
    }
    /**
     * 更新订阅状态
     */
    async updateSubscriptionStatus(subscriptionId, status) {
        try {
            // 验证状态值
            if (!Object.values(subscription_model_1.SubscriptionStatus).includes(status)) {
                throw new Error(`无效的订阅状态: ${status}`);
            }
            // 更新数据库
            const subscription = await subscription_model_1.SubscriptionModel.findByIdAndUpdate(subscriptionId, { status }, { new: true }).lean();
            if (!subscription) {
                logger_1.logger.debug(`订阅不存在: ${subscriptionId}`);
                return null;
            }
            // 转换为Subscription类型
            const subscriptionInfo = {
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
            await (0, cache_1.setCache)(cacheKey, null, 1);
            await (0, cache_1.setCache)(`subscriptions:user:${subscription.userId}`, null, 1);
            // 更新指标
            metrics_1.serviceSubscriptionCounter.inc({
                service_type: subscription.serviceType,
                duration: subscription.billingCycle,
                status: subscription.status
            });
            return subscriptionInfo;
        }
        catch (error) {
            logger_1.logger.error(`更新订阅状态失败:`, error);
            throw error;
        }
    }
    /**
     * 续订服务
     */
    async renewSubscription(subscriptionId, duration) {
        const session = await mongoose_1.default.startSession();
        session.startTransaction();
        try {
            // 获取当前订阅
            const currentSubscription = await subscription_model_1.SubscriptionModel.findById(subscriptionId).session(session);
            if (!currentSubscription) {
                await session.abortTransaction();
                session.endSession();
                logger_1.logger.debug(`订阅不存在: ${subscriptionId}`);
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
            const updatedSubscription = await subscription_model_1.SubscriptionModel.findByIdAndUpdate(subscriptionId, {
                endDate: newEndDate.toISOString().split('T')[0],
                status: subscription_model_1.SubscriptionStatus.ACTIVE,
                billingCycle: duration
            }, { new: true, session }).lean();
            await session.commitTransaction();
            session.endSession();
            if (!updatedSubscription) {
                logger_1.logger.error(`续订失败: ${subscriptionId}`);
                return null;
            }
            // 转换为Subscription类型
            const subscriptionInfo = {
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
            await (0, cache_1.setCache)(cacheKey, null, 1);
            await (0, cache_1.setCache)(`subscriptions:user:${updatedSubscription.userId}`, null, 1);
            // 更新指标
            metrics_1.serviceSubscriptionCounter.inc({
                service_type: updatedSubscription.serviceType,
                duration: updatedSubscription.billingCycle,
                status: updatedSubscription.status
            });
            return subscriptionInfo;
        }
        catch (error) {
            await session.abortTransaction();
            session.endSession();
            logger_1.logger.error(`续订服务失败:`, error);
            throw error;
        }
    }
    /**
     * 取消自动续订
     */
    async cancelAutoRenew(subscriptionId) {
        try {
            // 更新订阅自动续订状态
            const subscription = await subscription_model_1.SubscriptionModel.findByIdAndUpdate(subscriptionId, { autoRenew: false }, { new: true }).lean();
            if (!subscription) {
                logger_1.logger.debug(`订阅不存在: ${subscriptionId}`);
                return null;
            }
            // 清除缓存
            const cacheKey = `subscription:${subscriptionId}`;
            await (0, cache_1.setCache)(cacheKey, null, 1);
            // 转换为Subscription类型
            const subscriptionInfo = {
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
        }
        catch (error) {
            logger_1.logger.error(`取消自动续订失败:`, error);
            throw error;
        }
    }
}
exports.SubscriptionService = SubscriptionService;
exports.default = new SubscriptionService();
